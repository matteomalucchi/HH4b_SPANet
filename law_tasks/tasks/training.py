"""Training of a SPANet model, either on HTCondor or interactively."""

import importlib.util
import os
import time

import luigi

from law_tasks.base import ModelTask

#: HTCondor job status codes
JOB_STATUS = {
    1: "idle",
    2: "running",
    3: "removed",
    4: "completed",
    5: "held",
    6: "transferring output",
    7: "suspended",
}


def _condor_submitter(repo_dir):
    """Import ``jobs/submit_to_condor.py`` without requiring it to be a package."""
    path = os.path.join(repo_dir, "jobs", "submit_to_condor.py")
    spec = importlib.util.spec_from_file_location("spanet_submit_to_condor", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Training(ModelTask):
    """Train the model described by the options file.

    An already trained ``version_N`` directory is adopted instead of starting a
    new training, unless ``--force-training`` is given.  A job of a previous
    submission that is still in the queue is picked up and waited for.
    """

    job_config = luigi.Parameter(
        default="jobs/config/training_1gpu_1d.yaml",
        description="condor job configuration; default: jobs/config/training_1gpu_1d.yaml",
    )
    checkpoint = luigi.Parameter(
        default="",
        description="checkpoint to restore weights and optimizer state from; "
        "default: empty",
    )
    train_args = luigi.Parameter(
        default="",
        description="additional arguments forwarded to spanet.train; default: empty",
    )
    local_training = luigi.BoolParameter(
        default=False,
        description="run the training in the current session instead of "
        "submitting it to HTCondor; default: False",
    )
    force_training = luigi.BoolParameter(
        default=False,
        significant=False,
        description="train even if a trained version already exists; default: False",
    )
    no_wait = luigi.BoolParameter(
        default=False,
        significant=False,
        description="submit the training and stop instead of waiting for the "
        "condor job to finish; default: False",
    )
    poll_interval = luigi.IntParameter(
        default=300,
        significant=False,
        description="seconds between two condor status queries; default: 300",
    )
    max_wait_hours = luigi.FloatParameter(
        default=72.0,
        significant=False,
        description="give up waiting for the condor job after this many hours; "
        "default: 72",
    )

    def output(self):
        return self.marker("training.json")

    def complete(self):
        if self.force_training and not getattr(self, "_trained_here", False):
            return False
        return super(Training, self).complete()

    # -- condor helpers ----------------------------------------------------

    def _queued_jobs(self):
        """Cluster ids of jobs of this training that are still in the queue."""
        import htcondor

        schedd = htcondor.Schedd()
        jobs = schedd.query(
            constraint='Owner == "{}"'.format(os.environ.get("USER", "")),
            projection=["ClusterId", "JobStatus", "Out"],
        )
        return sorted(
            {
                int(job["ClusterId"])
                for job in jobs
                if self.log_dir_rel in str(job.get("Out", ""))
            }
        )

    def _job_status(self, cluster_id):
        """Status string of ``cluster_id``, or ``None`` once it left the queue."""
        import htcondor

        schedd = htcondor.Schedd()
        jobs = schedd.query(
            constraint="ClusterId == {}".format(cluster_id), projection=["JobStatus"]
        )
        if not jobs:
            return None
        return JOB_STATUS.get(int(jobs[0]["JobStatus"]), "unknown")

    def _wait_for(self, cluster_id):
        """Block until ``cluster_id`` left the queue."""
        deadline = time.time() + self.max_wait_hours * 3600

        while True:
            status = self._job_status(cluster_id)
            if status is None:
                self.publish_message("job {} left the queue".format(cluster_id))
                return
            if status == "held":
                raise RuntimeError(
                    "condor job {} is held, inspect it with "
                    "'condor_q -better-analyze {}'".format(cluster_id, cluster_id)
                )

            if time.time() > deadline:
                raise RuntimeError(
                    "condor job {} is still '{}' after {} hours; increase "
                    "--max-wait-hours or rerun the pipeline later".format(
                        cluster_id, status, self.max_wait_hours
                    )
                )

            self.publish_message(
                "job {} is {}, checking again in {} s".format(
                    cluster_id, status, self.poll_interval
                )
            )
            time.sleep(self.poll_interval)

    def _submit(self):
        submitter = _condor_submitter(self.cfg.repo_dir)
        job_config = self.job_config
        if not os.path.isabs(job_config):
            job_config = os.path.join(self.cfg.repo_dir, job_config)

        return submitter.submit_training(
            cfg=job_config,
            options_file=os.path.relpath(self.options_path, self.cfg.repo_dir),
            log_dir=self.log_dir_rel,
            seed=self.seed,
            checkpoint=self.checkpoint or None,
            extra_args=self.train_args,
            output_dir=self.base_dir,
            basedir=self.cfg.repo_dir,
        )

    def _run_locally(self):
        script = os.path.join(self.cfg.repo_dir, "jobs", "training.sh")
        command = (
            "bash {script} -o {options} -n {run_dir} -s {seed} -g {gpus} "
            "-m {main} -e {env} -H {home} -- {extra}".format(
                script=script,
                options=self.options_path,
                run_dir=self.run_dir,
                seed=self.seed,
                gpus=1,
                main=self.cfg.spanet_main_dir,
                env=self.cfg.spanet_env_dir,
                home=os.environ["HOME"],
                extra=self.train_args,
            )
        )
        if self.checkpoint:
            command += " -cf {}".format(self.checkpoint)

        os.makedirs(self.run_dir, exist_ok=True)
        self.run_command(command, gpu=True, cwd=self.cfg.repo_dir)

    # -- run ---------------------------------------------------------------

    def run(self):
        existing = self.existing_versions()
        reusable = (
            self.model_version in existing
            if self.model_version >= 0
            else bool(existing)
        )

        if reusable and not self.force_training:
            version = self.resolve_version()
            self.publish_message(
                "reusing the trained model in {}".format(self.version_dir(version))
            )
            self._write(version, cluster_id=None, reused=True)
            return

        cluster_id = None
        if self.local_training:
            self._run_locally()
        else:
            queued = [] if self.force_training else self._queued_jobs()
            if queued:
                cluster_id = queued[-1]
                self.publish_message(
                    "a job of this training is already in the queue "
                    "(cluster {}), waiting for it".format(cluster_id)
                )
            else:
                cluster_id = self._submit()

            if self.no_wait:
                raise RuntimeError(
                    "training submitted (cluster {}), --no-wait requested; "
                    "rerun the pipeline once the job is done".format(cluster_id)
                )
            self._wait_for(cluster_id)

        versions = self.existing_versions()
        new = [v for v in versions if v not in existing] or versions
        if not new:
            raise RuntimeError(
                "the training did not produce any checkpoint in {}, check the "
                "condor log files there".format(self.run_dir)
            )

        self._trained_here = True
        self._write(new[-1], cluster_id=cluster_id, reused=False)

    def _write(self, version, cluster_id, reused):
        self.write_marker(
            self.output(),
            model_key=self.model_key,
            seed=self.seed,
            version=version,
            version_dir=self.version_dir(version),
            options_file=self.options_path,
            training_file=self.training_file,
            cluster_id=cluster_id,
            reused_existing_training=reused,
        )
