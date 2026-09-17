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

    #: tasks that only drive other ones hand --overwrite down to them
    propagates_overwrite = False

    #: steps that cost hours: a propagated --overwrite leaves them alone
    overwrite_only_explicitly = False

    overwrite = luigi.BoolParameter(
        default=False,
        significant=False,
        description="redo this task and replace what is already there; on the "
        "tasks that only drive others (hh4b.Dataset, hh4b.Performance, "
        "hh4b.EfficiencyPlots, hh4b.RocPlots) it applies to the steps they "
        "drive as well, the training and the prediction excepted; default: False",
    )
    overwrite_driven = luigi.BoolParameter(
        default=False,
        significant=False,
        description="set by law itself when --overwrite is given to a task "
        "that drives this one; default: False",
    )
    overwrite_all = luigi.BoolParameter(
        default=False,
        significant=False,
        description="redo this task and everything it depends on, the training "
        "and the prediction included; default: False",
    )

    @property
    def cfg(self):
        return settings()

    @property
    def force_overwrite(self):
        return bool(self.overwrite or self.overwrite_driven or self.overwrite_all)

    def __init__(self, *args, **kwargs):
        super(BaseTask, self).__init__(*args, **kwargs)

        # an overwrite redoes the task even when its outputs are already
        # there; the flag below keeps it complete once it has actually run
        self._overwrite_done = False
        if self.force_overwrite:
            inner_run = self.run

            def run_and_mark(*args, **kwargs):
                try:
                    return inner_run(*args, **kwargs)
                finally:
                    self._overwrite_done = True

            self.run = run_and_mark

    def complete(self):
        if self.force_overwrite and not self._overwrite_done:
            return False
        return super(BaseTask, self).complete()

    def clone(self, cls=None, **kwargs):
        # --overwrite alone redoes the task it is given, so that redrawing one
        # plot does not recompute the prediction below it.  On a task that only
        # drives others it would mean nothing, so there it keeps reaching the
        # steps it drives -- the training and the prediction excepted, which
        # cost hours and are asked for by name.  --overwrite-all redoes
        # everything below, whatever it is.
        deep = self.overwrite_all
        driven = deep or self.overwrite_driven or (
            self.overwrite and self.propagates_overwrite
        )
        if (
            driven
            and not deep
            and cls is not None
            and getattr(cls, "overwrite_only_explicitly", False)
        ):
            driven = False

        kwargs.setdefault("overwrite", False)
        kwargs.setdefault("overwrite_driven", driven)
        kwargs.setdefault("overwrite_all", deep)
        return super(BaseTask, self).clone(cls, **kwargs)

    def output_paths(self):
        """Absolute paths of the files this task declares as its outputs."""
        paths = set()
        for target in law.util.flatten(self.output()):
            path = getattr(target, "path", None)
            if path:
                paths.add(os.path.abspath(path))
        return paths

    def check_no_overwrite(self, paths, what="file"):
        """Stop unless ``--overwrite`` is given and something is in the way.

        What the task declares as its own output is never in the way: law only
        runs a task whose outputs are missing, so one that is nevertheless
        there is the leftover of an attempt that did not finish, or a result
        that no longer matches the inputs.  Refusing to replace it would leave
        the task unable to ever complete.  Everything else is protected.
        """
        owned = self.output_paths()
        existing = sorted(
            path
            for path in paths
            if os.path.exists(path) and os.path.abspath(path) not in owned
        )
        if existing and not self.force_overwrite:
            raise RuntimeError(
                "refusing to overwrite {} {}(s) that {} already there:\n  {}\n"
                "pass --overwrite to replace them".format(
                    len(existing),
                    what,
                    "is" if len(existing) == 1 else "are",
                    "\n  ".join(existing),
                )
            )
        return existing

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
    eval_tag = luigi.Parameter(
        default="",
        description="name of the evaluation, keeping the predictions, the "
        "configurations and the plots of a model evaluated on several test "
        "files apart; default: derived from --test-file",
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

    def eval_marker(self, name):
        """Marker of a task that depends on the file the model is evaluated on."""
        stem, ext = os.path.splitext(name)
        return self.marker("{}{}{}".format(stem, self.eval_suffix, ext))

    def write_marker(self, target, **content):
        content.setdefault("task", self.__class__.__name__)
        content.setdefault("timestamp", time.strftime("%Y-%m-%d %H:%M:%S"))
        if "version_dir" not in content:
            # the training this result belongs to, so that a later training
            # does not silently reuse it (see marker_is_stale)
            try:
                content["version_dir"] = self.version_dir()
            except RuntimeError:
                pass
        target.parent.touch()
        with open(target.path, "w") as fobj:
            json.dump(content, fobj, indent=4)
            fobj.write("\n")

    # -- staleness ---------------------------------------------------------

    def marker_is_stale(self, target):
        """True when ``target`` was written for another training version.

        Everything below the training is named after the model, not after the
        ``version_N`` directory, so a new training would otherwise inherit the
        configurations and the plots of the previous one and law would report
        a performance that is not the one of the model it just trained.
        """
        path = getattr(target, "path", "")
        if not path.endswith(".json") or not os.path.exists(path):
            return False

        try:
            with open(path) as fobj:
                recorded = json.load(fobj).get("version_dir")
        except (ValueError, OSError):
            return False
        if not recorded:
            return False

        try:
            current = self.version_dir()
        except RuntimeError:
            return False
        return os.path.normpath(recorded) != os.path.normpath(current)

    def complete(self):
        if not super(ModelTask, self).complete():
            return False
        return not any(
            self.marker_is_stale(target) for target in law.util.flatten(self.output())
        )

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
    def eval_key(self):
        """Short name of this evaluation, empty for the model's own test file."""
        if self.eval_tag:
            return self.eval_tag
        if not self.test_file:
            return ""

        try:
            default = naming.derive_test_file(self.training_file)
        except ValueError:
            default = ""
        if default and os.path.realpath(self.evaluation_file) == os.path.realpath(default):
            return ""
        return naming.derive_eval_tag(self.evaluation_file, default)

    @property
    def eval_suffix(self):
        return "_{}".format(self.eval_key) if self.eval_key else ""

    @property
    def prediction_name(self):
        return naming.prediction_name(self.evaluation_file, self.eval_key)

    def prediction_path(self, version=None):
        return os.path.join(self.version_dir(version), self.prediction_name)
