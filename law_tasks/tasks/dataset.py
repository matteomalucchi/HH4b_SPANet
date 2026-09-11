"""Conversion of the coffea outputs into SPANet h5 inputs, and their transfer.

These tasks run on the machine holding the coffea files, which is usually not
the machine the training runs on.  The workflow is therefore:

    law run hh4b.Dataset --dataset <name>        # on the analysis machine
    law run hh4b.Performance --options-file ...  # on lxplus

with the ``training_file`` of the options file pointing at the transferred h5.
"""

import json
import os
import shlex

import law
import luigi

from law_tasks import datasets
from law_tasks.base import BaseTask


class DatasetTask(BaseTask):
    """Parameters shared by every dataset task.

    Every field of the dataset configuration can be overridden here, so a
    dataset that is not in the configuration file can be converted by passing
    at least ``--output-prefix``, ``--coffea-dir`` and ``--regions``.
    """

    exclude_index = True

    dataset = luigi.Parameter(
        description="name of the dataset in the dataset configuration",
    )
    coffea_dir = luigi.Parameter(
        default="",
        description="directory holding the coffea file, absolute or relative "
        "to the configured coffea base directory",
    )
    coffea_file = luigi.Parameter(
        default="",
        description="name of the coffea file; default: output_all.coffea",
    )
    output_dir = luigi.Parameter(
        default="",
        description="directory for the h5 files; default: the coffea directory",
    )
    output_prefix = luigi.Parameter(
        default="",
        description="prefix of the produced h5 files, i.e. the -o argument of "
        "coffea_to_h5_direct.py",
    )
    regions = luigi.Parameter(
        default="",
        description="regions, one per class label, separated by spaces",
    )
    class_labels = luigi.Parameter(
        default="",
        description="class labels, separated by spaces (e.g. 'GluGlu VBF')",
    )
    jets = luigi.Parameter(
        default="",
        description="jet collections or the name of a predefined group",
    )
    global_vars = luigi.Parameter(
        default="",
        description="global variables or the name of a predefined group",
    )
    jet_like_global_vars = luigi.Parameter(
        default="",
        description="jet-like global variables or the name of a predefined group",
    )
    max_jets = luigi.Parameter(
        default="",
        description="maximum number of jets per collection, separated by spaces",
    )
    convert_args = luigi.Parameter(
        default="",
        description="additional arguments forwarded to coffea_to_h5_direct.py",
    )
    collections = luigi.Parameter(
        default="",
        description="jet collection groups to transfer, separated by spaces; "
        "default: all of them",
    )
    remote_dir = luigi.Parameter(
        default="",
        description="destination directory, absolute or relative to the "
        "remote input base directory",
    )
    dataset_config = luigi.Parameter(
        default="",
        significant=False,
        description="YAML file describing the datasets; default: from law.cfg",
    )

    @property
    def spec(self):
        """The resolved dataset description."""
        overrides = {
            field: getattr(self, field)
            for field in datasets.FIELDS
            if getattr(self, field, "")
        }
        return datasets.resolve(
            self.dataset, config_path=self.dataset_config or None, **overrides
        )

    # -- environment -------------------------------------------------------

    def use_apptainer(self):
        # the conversion runs on the analysis machine, which has its own
        # environment and usually no container
        return self.apptainer == "yes"

    def venv_prefix(self):
        env_dir = self.cfg.conversion_env
        if not env_dir or os.environ.get("VIRTUAL_ENV") == env_dir:
            return ""
        return "source {} && ".format(
            shlex.quote(os.path.join(env_dir, "bin", "activate"))
        )

    # -- markers -----------------------------------------------------------

    def marker(self, name):
        return law.LocalFileTarget(
            os.path.join(self.spec.local_dir, "law", name)
        )

    def write_marker(self, target, **content):
        content.setdefault("dataset", self.dataset)
        target.parent.touch()
        with open(target.path, "w") as fobj:
            json.dump(content, fobj, indent=4)
            fobj.write("\n")


class ConvertDataset(DatasetTask):
    """Convert a coffea file into the SPANet h5 inputs.

    The produced files are ``<prefix><jet collection group>_{train,test}.h5``,
    one pair per jet collection group, and they are the outputs of this task.
    """

    def output(self):
        spec = self.spec
        return {
            key: law.LocalFileTarget(path)
            for key, path in spec.all_files().items()
        }

    def run(self):
        spec = self.spec

        if not os.path.exists(spec.coffea_path):
            raise RuntimeError(
                "coffea file '{}' does not exist".format(spec.coffea_path)
            )

        os.makedirs(spec.local_dir, exist_ok=True)
        command = spec.convert_command(
            self.cfg.converter_script, python=self.cfg.conversion_python
        )
        self.run_command(command, cwd=spec.local_dir)

        missing = [
            path for path in spec.all_files().values() if not os.path.exists(path)
        ]
        if missing:
            raise RuntimeError(
                "the conversion did not produce:\n  {}".format("\n  ".join(missing))
            )

        for path in sorted(spec.all_files().values()):
            self.publish_message("wrote {}".format(path))


class TransferDataset(DatasetTask):
    """Copy the converted h5 files to the machine the training runs on."""

    def requires(self):
        return self.clone(ConvertDataset)

    def output(self):
        return self.marker("transfer_{}.json".format(self.dataset))

    def run(self):
        spec = self.spec
        files = spec.transfer_files()
        if not files:
            raise RuntimeError(
                "no file to transfer for dataset '{}'; check the 'collections' "
                "setting".format(self.dataset)
            )

        host = self.cfg.remote_host
        target = spec.remote_path
        local = " ".join(shlex.quote(path) for path in sorted(files.values()))

        if host and host != "local":
            self.run_command(
                "ssh {host} {mkdir}".format(
                    host=shlex.quote(host),
                    mkdir=shlex.quote("mkdir -p {}".format(shlex.quote(target))),
                )
            )
            destination = "{}:{}/".format(host, target)
        else:
            os.makedirs(target, exist_ok=True)
            destination = target + "/"

        self.run_command(
            "rsync {opts} {files} {dest}".format(
                opts=self.cfg.rsync_options,
                files=local,
                dest=shlex.quote(destination),
            )
        )

        remote_files = spec.remote_files()
        self.write_marker(
            self.output(),
            host=host or "local",
            remote_dir=target,
            files=remote_files,
        )
        for key in sorted(remote_files):
            self.publish_message("{}: {}".format(key, remote_files[key]))


class Dataset(DatasetTask):
    """Convert a coffea file and copy the result to the training machine.

    This is the task to run on the analysis machine::

        law run hh4b.Dataset --dataset <name>

    It writes a summary with the ``training_file`` paths to put into the
    SPANet options file.
    """

    def requires(self):
        return self.clone(TransferDataset)

    def output(self):
        return self.marker("dataset_{}.json".format(self.dataset))

    def run(self):
        spec = self.spec
        remote_files = spec.remote_files()
        training_files = {
            key[: -len("_train")]: path
            for key, path in remote_files.items()
            if key.endswith("_train")
        }

        self.write_marker(
            self.output(),
            coffea_file=spec.coffea_path,
            local_dir=spec.local_dir,
            local_files=spec.transfer_files(),
            remote_dir=spec.remote_path,
            remote_files=remote_files,
            training_files=training_files,
        )

        self.publish_message("")
        self.publish_message("dataset:     {}".format(self.dataset))
        self.publish_message("coffea file: {}".format(spec.coffea_path))
        self.publish_message("local dir:   {}".format(spec.local_dir))
        self.publish_message("remote dir:  {}".format(spec.remote_path))
        self.publish_message("")
        self.publish_message("training_file entries for the options file:")
        for name in sorted(training_files):
            self.publish_message('  "{}": "{}"'.format(name, training_files[name]))
        self.publish_message("summary:     {}".format(self.output().path))
