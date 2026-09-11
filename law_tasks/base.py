"""Common base tasks: parameter set, path resolution and command execution."""

import glob
import json
import os
import re
import shlex
import subprocess
import time

import law
import luigi

from law_tasks import naming
from law_tasks.config import settings

class BaseTask(law.Task):
    """Adds command execution helpers on top of ``law.Task``."""

    task_namespace = "hh4b"
    exclude_index = True

    #: run the payload inside the apptainer image
    apptainer = luigi.ChoiceParameter(
        default="auto",
        choices=["auto", "yes", "no"],
        significant=False,
        description="run the payload inside the apptainer image; 'auto' skips "
        "the container when already inside one; default: auto",
    )

    @property
    def cfg(self):
        return settings()

    # -- container ---------------------------------------------------------

    def inside_container(self):
        return bool(
            os.environ.get("APPTAINER_CONTAINER") or os.environ.get("SINGULARITY_CONTAINER")
        )

    def use_apptainer(self):
        if self.apptainer == "yes":
            return True
        if self.apptainer == "no":
            return False
        return not self.inside_container()

    def venv_prefix(self):
        """``source <venv>/bin/activate && `` unless the venv is already active."""
        env_dir = self.cfg.spanet_env_dir
        if not env_dir:
            return ""
        if os.environ.get("VIRTUAL_ENV") == env_dir and not self.use_apptainer():
            return ""
        activate = os.path.join(env_dir, "bin", "activate")
        return "source {} && ".format(shlex.quote(activate))

    def wrap_command(self, command, gpu=False):
        """Wrap ``command`` into the apptainer call and the venv activation."""
        payload = self.venv_prefix() + command

        if not self.use_apptainer():
            return payload

        parts = ["apptainer", "exec"]
        for bind in self.cfg.apptainer_binds:
            parts += ["-B", bind]

        if os.environ.get("XDG_RUNTIME_DIR"):
            parts += [
                "--env",
                "KRB5CCNAME=FILE:{}/krb5cc".format(os.environ["XDG_RUNTIME_DIR"]),
            ]
        for variable in ("SPANET_MAIN_DIR", "SPANET_ENV_DIR", "EOS_SPANET"):
            if os.environ.get(variable):
                parts += ["--env", "{}={}".format(variable, os.environ[variable])]

        if gpu:
            parts.append("--nv")

        parts.append(self.cfg.apptainer_image)
        parts += ["bash", "-c", payload]

        return " ".join(shlex.quote(part) for part in parts)

    # -- execution ---------------------------------------------------------

    def run_command(self, command, gpu=False, cwd=None, wrap=True):
        """Print and run ``command``, raising when it fails."""
        full = self.wrap_command(command, gpu=gpu) if wrap else command

        self.publish_message("running: {}".format(full))
        code = subprocess.call(full, shell=True, executable="/bin/bash", cwd=cwd)
        if code != 0:
            raise RuntimeError("command failed with exit code {}:\n{}".format(code, full))
        return code


class ModelTask(BaseTask):
    """Everything that is defined by one options file and one training seed."""

    exclude_index = True

    options_file = luigi.Parameter(
        description="path to the SPANet options JSON file (absolute, or "
        "relative to the repository)",
    )
    seed = luigi.IntParameter(
        default=100,
        description="training seed, matching 'out_seed_trainings_<seed>'; default: 100",
    )
    suffix = luigi.Parameter(
        default="",
        description="suffix appended to the directory name derived from the "
        "options file; default: empty",
    )
    model_version = luigi.IntParameter(
        default=-1,
        description="'version_N' subdirectory of the training; -1 selects the "
        "highest existing one; default: -1",
    )
    output_base = luigi.Parameter(
        default="",
        significant=False,
        description="directory in which 'out_spanet_outputs' lives; default: "
        "from law.cfg / $EOS_SPANET",
    )
    test_file = luigi.Parameter(
        default="",
        description="file the model is evaluated on; default: derived from the "
        "training file of the options file",
    )

    # -- paths -------------------------------------------------------------

    @property
    def options_path(self):
        path = os.path.expandvars(os.path.expanduser(self.options_file))
        if not os.path.isabs(path):
            path = os.path.join(self.cfg.repo_dir, path)
        if not os.path.exists(path):
            raise ValueError("options file '{}' does not exist".format(path))
        return os.path.abspath(path)

    @property
    def model_key(self):
        return naming.model_key(self.options_path, self.suffix)

    @property
    def base_dir(self):
        return self.output_base or self.cfg.output_base

    @property
    def log_dir_rel(self):
        """Training directory relative to the output base, as condor sees it."""
        return os.path.join(
            "out_spanet_outputs",
            "out_{}".format(self.model_key),
            "out_seed_trainings_{}".format(self.seed),
        )

    @property
    def run_dir(self):
        """``.../out_spanet_outputs/out_<model_key>/out_seed_trainings_<seed>``."""
        return os.path.join(self.base_dir, self.log_dir_rel)

    @property
    def marker_dir(self):
        return os.path.join(self.run_dir, "law")

    def marker(self, name):
        return law.LocalFileTarget(os.path.join(self.marker_dir, name))

    def write_marker(self, target, **content):
        content.setdefault("task", self.__class__.__name__)
        content.setdefault("timestamp", time.strftime("%Y-%m-%d %H:%M:%S"))
        target.parent.touch()
        with open(target.path, "w") as fobj:
            json.dump(content, fobj, indent=4)
            fobj.write("\n")

    # -- versions ----------------------------------------------------------

    def existing_versions(self, require_checkpoint=True):
        """Sorted indices of the ``version_N`` directories of this training."""
        versions = []
        for path in glob.glob(os.path.join(self.run_dir, "version_*")):
            match = re.match(r"^version_(\d+)$", os.path.basename(path))
            if not match or not os.path.isdir(path):
                continue
            if require_checkpoint and not glob.glob(
                os.path.join(path, "checkpoints", "*.ckpt")
            ):
                continue
            versions.append(int(match.group(1)))
        return sorted(versions)

    def resolve_version(self, require_checkpoint=True):
        """The requested version, the latest trained one, or ``None``."""
        if self.model_version >= 0:
            return self.model_version
        versions = self.existing_versions(require_checkpoint=require_checkpoint)
        return versions[-1] if versions else None

    def version_dir(self, version=None):
        version = self.resolve_version() if version is None else version
        if version is None:
            raise RuntimeError(
                "no trained 'version_N' directory found in {}".format(self.run_dir)
            )
        return os.path.join(self.run_dir, "version_{}".format(version))

    # -- input files -------------------------------------------------------

    @property
    def training_file(self):
        return naming.training_file(self.options_path)

    @property
    def evaluation_file(self):
        """The test file the predictions are computed on."""
        if self.test_file:
            return os.path.expandvars(os.path.expanduser(self.test_file))
        return naming.derive_test_file(self.training_file)

    @property
    def prediction_name(self):
        return naming.prediction_name(self.evaluation_file)

    def prediction_path(self, version=None):
        return os.path.join(self.version_dir(version), self.prediction_name)
