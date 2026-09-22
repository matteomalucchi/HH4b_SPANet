"""ONNX export of a trained model, and its copy to the analysis machine.

The model that is used in the analysis is not the checkpoint but the ONNX file
exported from it, and that file has to travel the way the h5 inputs came, only
backwards::

    lxplus                                analysis machine
    ------                                ----------------
    hh4b.ExportModel  --- rsync --->      /work/<me>/spanet_vbf_models/

Both steps run on lxplus, where the training is: the copy is a push made from
here, not a pull made on the other side.  By hand that is

    cd <run dir>/version_N
    python -m spanet.export ./ <onnx dir>/<model>.onnx --gpu
    rsync <onnx dir>/<model>.onnx <user>@<analysis machine>:<directory>/
"""

import json
import os
import shlex

import law
import luigi

from law_tasks.base import ModelTask
from law_tasks.tasks.training import Training


class ExportParameters(object):
    """Where the ONNX model is written and where it is copied to.

    They live in a mixin because ``hh4b.Performance`` carries them as well:
    a parameter is only handed down to the tasks it requires when the task it
    is given to has it too.
    """

    onnx_dir = luigi.Parameter(
        default="",
        description="directory the ONNX model is written to; default: from "
        "law.cfg / $SPANET_ONNX_DIR, i.e. <eos_base>/spanet_model",
    )
    onnx_file = luigi.Parameter(
        default="",
        description="name of the ONNX file; default: '<model>.onnx', the "
        "basename of the options file",
    )
    onnx_host = luigi.Parameter(
        default="",
        significant=False,
        description="'user@host' the ONNX model is copied to; 'local' or "
        "empty copies into --onnx-remote-dir without ssh; default: from "
        "law.cfg / $SPANET_ONNX_HOST",
    )
    onnx_remote_dir = luigi.Parameter(
        default="",
        description="directory on --onnx-host the ONNX model is copied into, "
        "usually the one the analysis reads the models from; default: from "
        "law.cfg / $SPANET_ONNX_REMOTE_DIR, and no copy when that is unset",
    )

    @property
    def onnx_name(self):
        """Basename of the ONNX file of this model."""
        return self.onnx_file or "{}.onnx".format(self.model_key)

    @property
    def onnx_path(self):
        """Where ``spanet.export`` writes the ONNX model."""
        directory = self.onnx_dir or self.cfg.onnx_base
        return os.path.join(os.path.abspath(self.cfg.expand(directory)), self.onnx_name)

    @property
    def onnx_destination(self):
        """``(host, directory)`` the model is copied to, ``(host, "")`` if nowhere."""
        return (
            self.onnx_host or self.cfg.onnx_host,
            self.onnx_remote_dir or self.cfg.onnx_remote_dir,
        )

    def push_command(self, path):
        """The rsync ``hh4b.TransferModel`` makes, run from this machine."""
        host, directory = self.onnx_destination
        if not directory:
            # nothing is configured: show the shape of the command instead
            destination = "<user>@<analysis machine>:<directory>"
        elif host and host != "local":
            destination = "{}:{}".format(host, directory)
        else:
            destination = directory
        return "rsync {opts} {path} {dest}/".format(
            opts=self.cfg.rsync_options, path=path, dest=destination
        )

    def export_marker(self, kind):
        """Marker of an export step, named after the ONNX file it belongs to."""
        return self.marker(
            "{}_{}.json".format(kind, os.path.splitext(self.onnx_name)[0])
        )


class ExportModel(ExportParameters, ModelTask):
    """Run ``spanet.export`` on the trained model.

    The ONNX file is named after the options file and written into one
    directory for all models, so that the analysis finds them in one place.
    A model that is trained again (``--overwrite``) replaces its own file;
    ``--onnx-file`` gives it another name to keep the two apart.
    """

    #: the exported model is data: --overwrite-plots leaves it alone
    produces_data = True

    export_args = luigi.Parameter(
        default="",
        description="additional arguments forwarded to spanet.export, e.g. "
        "'--input-log-transform --output-log-transform'; default: empty",
    )

    def requires(self):
        return self.clone(Training)

    def output(self):
        return {
            "onnx": law.LocalFileTarget(self.onnx_path),
            "marker": self.export_marker("export"),
        }

    def run(self):
        with open(self.input().path) as fobj:
            version = json.load(fobj)["version"]

        version_dir = self.version_dir(version)
        onnx = self.onnx_path
        os.makedirs(os.path.dirname(onnx), exist_ok=True)

        command = "cd {dir} && python -m spanet.export ./ {onnx}".format(
            dir=shlex.quote(version_dir), onnx=shlex.quote(onnx)
        )
        if self.gpu:
            command += " --gpu"
        if self.export_args:
            command += " " + self.export_args

        self.run_command(command, gpu=self.gpu)

        if not os.path.exists(onnx):
            raise RuntimeError("spanet.export did not create {}".format(onnx))

        self.write_marker(
            self.output()["marker"],
            model_key=self.model_key,
            seed=self.seed,
            version_dir=version_dir,
            onnx_file=onnx,
            gpu=self.gpu,
        )
        self.publish_message("wrote {}".format(onnx))

        host, directory = self.onnx_destination
        if not directory:
            self.publish_message(
                "not copied anywhere: set 'onnx_host' and 'onnx_remote_dir' in "
                "law.cfg to copy it from here to the analysis machine, or run"
            )
            self.publish_message("  {}".format(self.push_command(onnx)))


class TransferModel(ExportParameters, ModelTask):
    """Copy the exported ONNX model to the machine the coffea files live on.

    The destination is ``onnx_host``/``onnx_remote_dir`` of ``law.cfg``, the
    way back of the h5 files the training was made from.
    """

    #: a copy of the exported model: --overwrite-plots leaves it alone
    produces_data = True

    def requires(self):
        return self.clone(ExportModel)

    def output(self):
        return self.export_marker("export_transfer")

    def run(self):
        source = self.input()["onnx"].path
        host, directory = self.onnx_destination

        if not directory:
            raise RuntimeError(
                "no destination for the ONNX model: set 'onnx_remote_dir' in "
                "law.cfg (or $SPANET_ONNX_REMOTE_DIR, or --onnx-remote-dir), "
                "or pass --export no to keep the model on this machine"
            )

        directory = os.path.expandvars(os.path.expanduser(directory))
        remote = os.path.join(directory, os.path.basename(source))

        if host and host != "local":
            self.check_remote_no_overwrite(host, [remote])
            self.run_command(
                "ssh {host} {mkdir}".format(
                    host=shlex.quote(host),
                    mkdir=shlex.quote("mkdir -p {}".format(shlex.quote(directory))),
                )
            )
            destination = "{}:{}/".format(host, directory)
        else:
            self.check_no_overwrite([remote], what="ONNX model")
            os.makedirs(directory, exist_ok=True)
            destination = directory + "/"

        self.run_command(
            "rsync {opts} {source} {dest}".format(
                opts=self.cfg.rsync_options,
                source=shlex.quote(source),
                dest=shlex.quote(destination),
            )
        )

        self.write_marker(
            self.output(),
            model_key=self.model_key,
            onnx_file=source,
            host=host or "local",
            remote_dir=directory,
            remote_file=remote,
        )
        self.publish_message(
            "copied {} to {}".format(source, destination)
        )



