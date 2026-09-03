"""Resolution of all site/user specific settings used by the law tasks.

Every setting is looked up in this order:

1. the ``law.cfg`` file (section ``[hh4b_spanet]``),
2. an environment variable,
3. a generic default derived from ``$USER`` / the repository location.

Nothing here is hard coded to a specific user, so the same ``law.cfg`` works
for everybody.
"""

import json
import os
from functools import lru_cache

try:  # law is only needed when running the tasks, not for the unit tests
    import law

    _law_config = law.config.Config.instance()
except ImportError:  # pragma: no cover
    _law_config = None


#: repository root (the directory containing ``law_tasks``)
REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: main section of ``law.cfg`` holding the paths
SECTION = "hh4b_spanet"

DEFAULT_APPTAINER_IMAGE = (
    "/cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmsml/cmsml:latest"
)

#: colors used for new entries, in the order in which they are assigned
DEFAULT_PALETTE = [
    "orange",
    "blue",
    "green",
    "red",
    "purple",
    "magenta",
    "dodgerblue",
    "firebrick",
    "teal",
    "darkorange",
    "lime",
    "cyan",
    "brown",
    "gold",
    "navy",
    "black",
]

#: efficiency plots produced by ``hh4b.EfficiencyPlots``: name -> extra arguments
DEFAULT_EFFICIENCY_PLOTS = {
    "VBFEff_vbf_no_kin_cuts": "--vbf -c 1 -ih -r vbf_no_kin_cuts -k",
    "VBFEff_vbf_presel": "--vbf -c 1 -ih -r vbf_presel -k",
    "HiggsEff": "-c 0 -k",
}

#: ROC plots produced by ``hh4b.RocPlots``: name -> extra arguments
DEFAULT_ROC_PLOTS = {
    "vbf_no_kin_cuts": "-r vbf_no_kin_cuts -klb 1 all -s 0.8",
    "vbf_presel": "-r vbf_presel -klb 1 all -s 0.8",
}

#: additional dictionary entries triggered by a token of the options basename
DEFAULT_MODEL_EXTRAS = {
    "JetVBFHiggs": {
        "spanet": {"jet_coll": "JetVBF", "n_higgs_jets": 0, "offset_jet_idx": -4},
        "true": {"jet_coll_higgs": "JetVBF", "n_higgs_jets": 0},
    },
}


def cfg_get(option, env_var=None, default=None):
    """Return ``option`` from ``law.cfg``, then from ``env_var``, then ``default``."""
    if _law_config is not None and _law_config.has_option(SECTION, option):
        value = _law_config.get_expanded(SECTION, option)
        if value not in (None, "", "None"):
            return os.path.expandvars(os.path.expanduser(str(value)))

    if env_var and os.environ.get(env_var):
        return os.path.expandvars(os.path.expanduser(os.environ[env_var]))

    return default


def cfg_section(section, default=None):
    """Return a whole ``law.cfg`` section as a dict, or ``default`` if absent."""
    if _law_config is not None and _law_config.has_section(section):
        items = dict(_law_config.items(section))
        if items:
            return items
    return dict(default or {})


def _user():
    return os.environ.get("USER") or os.environ.get("LOGNAME") or ""


def _default_eos_base():
    """``<eos home>/spanet_infos`` when on lxplus, ``$HOME/spanet_infos`` otherwise."""
    if os.environ.get("EOS_SPANET"):
        return os.path.dirname(os.path.expandvars(os.environ["EOS_SPANET"]).rstrip("/"))

    user = _user()
    if user:
        eos_home = "/eos/user/{}/{}".format(user[0], user)
        if os.path.isdir(eos_home):
            return os.path.join(eos_home, "spanet_infos")

    return os.path.join(os.path.expanduser("~"), "spanet_infos")


class Settings(object):
    """Lazily resolved collection of all configurable values."""

    # -- directories ------------------------------------------------------

    @property
    def repo_dir(self):
        return cfg_get("repo_dir", "HH4B_SPANET_DIR", REPO_DIR)

    @property
    def spanet_main_dir(self):
        """Directory holding both the ``SPANet`` and ``HH4b_SPANet`` checkouts."""
        return cfg_get(
            "spanet_main_dir",
            "SPANET_MAIN_DIR",
            os.path.dirname(self.repo_dir),
        )

    @property
    def spanet_env_dir(self):
        """The python virtual environment (e.g. ``spanet_env_test_eos``)."""
        return cfg_get(
            "spanet_env_dir",
            "SPANET_ENV_DIR",
            os.environ.get("VIRTUAL_ENV", ""),
        )

    @property
    def eos_base(self):
        return cfg_get("eos_base", "SPANET_EOS_BASE", _default_eos_base())

    @property
    def output_base(self):
        """Directory in which ``out_spanet_outputs`` is created."""
        return cfg_get(
            "output_base",
            "EOS_SPANET",
            os.path.join(self.eos_base, "spanet_outputs"),
        )

    @property
    def eff_plot_base(self):
        return cfg_get(
            "eff_plot_base",
            "SPANET_EFF_PLOT_DIR",
            os.path.join(self.eos_base, "spanet_eff_plots", "vbf"),
        )

    @property
    def roc_plot_base(self):
        return cfg_get(
            "roc_plot_base",
            "SPANET_ROC_PLOT_DIR",
            os.path.join(self.eos_base, "spanet_roc_curves"),
        )

    @property
    def work_dir(self):
        """Where the generated performance configurations are written."""
        return cfg_get(
            "work_dir",
            "SPANET_LAW_WORK_DIR",
            os.path.join(self.eos_base, "law_work"),
        )

    # -- scripts and base configurations ----------------------------------

    @property
    def efficiency_script(self):
        return cfg_get(
            "efficiency_script",
            None,
            os.path.join(self.repo_dir, "utils", "performance", "efficiency_studies.py"),
        )

    @property
    def roc_script(self):
        return cfg_get(
            "roc_script",
            None,
            os.path.join(self.repo_dir, "utils", "roccurves", "ROC_plots.py"),
        )

    @property
    def training_metrics_script(self):
        return cfg_get(
            "training_metrics_script",
            None,
            os.path.join(self.repo_dir, "scripts", "plot_training_metrics.py"),
        )

    @property
    def eff_base_config(self):
        return cfg_get(
            "eff_base_config",
            None,
            os.path.join(
                self.repo_dir,
                "utils",
                "performance",
                "efficiency_configuration_vbf_ggf.py",
            ),
        )

    @property
    def roc_base_config(self):
        return cfg_get(
            "roc_base_config",
            None,
            os.path.join(
                self.repo_dir, "utils", "roccurves", "roc_configuration_vbf_ggf.py"
            ),
        )

    # -- apptainer --------------------------------------------------------

    @property
    def apptainer_image(self):
        return cfg_get(
            "apptainer_image", "SPANET_APPTAINER_IMAGE", DEFAULT_APPTAINER_IMAGE
        )

    @property
    def apptainer_binds(self):
        """Bind mounts of the apptainer container, as a list of paths."""
        raw = cfg_get("apptainer_binds", "SPANET_APPTAINER_BINDS", None)
        if raw:
            binds = [b.strip() for b in raw.replace("\n", ",").split(",")]
        else:
            binds = list(self.default_binds())

        # keep the order, drop duplicates, paths inside another bind and
        # paths that do not exist (apptainer refuses to bind those)
        result = []
        for bind in binds:
            bind = os.path.expandvars(bind).rstrip("/")
            if not bind or not os.path.exists(bind):
                continue
            if any(bind == b or bind.startswith(b + os.sep) for b in result):
                continue
            result.append(bind)
        return result

    def default_binds(self):
        binds = ["/afs", "/cvmfs", "/etc/sysconfig/ngbauth-submit"]

        user = _user()
        if user:
            binds.append("/eos/user/{}/{}".format(user[0], user))

        # make sure the directories the tasks read from/write to are visible
        for path in (
            self.eos_base,
            self.output_base,
            self.eff_plot_base,
            self.roc_plot_base,
            self.work_dir,
            self.spanet_main_dir,
            self.spanet_env_dir,
        ):
            if path:
                binds.append(_mount_root(path))

        if os.environ.get("XDG_RUNTIME_DIR"):
            binds.append(os.environ["XDG_RUNTIME_DIR"])

        return binds

    # -- naming conventions ------------------------------------------------

    @property
    def model_prefix(self):
        """Prefix of the options basename that is stripped for derived names."""
        return cfg_get(
            "model_prefix", None, "hh4b_pairing_vbf_ggf_all_Klambda_"
        )

    @property
    def true_key_prefix(self):
        """Replacement of :py:attr:`model_prefix` in the ``true_dict`` keys."""
        return cfg_get("true_key_prefix", None, "9jets_all_Klambda_")

    @property
    def label_prefix(self):
        """Label given to the token that is stripped by :py:attr:`label_strip`."""
        return cfg_get("label_prefix", None, "VBF pair+clas")

    @property
    def label_strip(self):
        return cfg_get("label_strip", None, "VBFPairing_")

    @property
    def training_only_tokens(self):
        """Tokens that describe the training only and not the input dataset."""
        raw = cfg_get("training_only_tokens", None, r"ClassLoss\d*, PtFlatten, \d+e")
        return [t.strip() for t in raw.split(",") if t.strip()]

    @property
    def label_replacements(self):
        raw = cfg_get("label_replacements", None, '{"DNNVars": "DNN Vars"}')
        return json.loads(raw)

    @property
    def label_train_tokens(self):
        """Tokens that get a trailing ``Train`` in the label."""
        raw = cfg_get("label_train_tokens", None, "VBFNoKinCut, VBFPresel")
        return [t.strip() for t in raw.split(",") if t.strip()]

    @property
    def palette(self):
        raw = cfg_get("palette", None, None)
        if raw:
            return [c.strip() for c in raw.replace("\n", ",").split(",") if c.strip()]
        return list(DEFAULT_PALETTE)

    @property
    def klambda(self):
        return cfg_get("klambda", None, "postEE")

    # -- plot definitions --------------------------------------------------

    @property
    def efficiency_plots(self):
        return cfg_section("efficiency_plots", DEFAULT_EFFICIENCY_PLOTS)

    @property
    def roc_plots(self):
        return cfg_section("roc_plots", DEFAULT_ROC_PLOTS)

    @property
    def model_extras(self):
        """``token -> {"spanet": {...}, "true": {...}}`` additions."""
        section = cfg_section("model_extras", None)
        if not section:
            return {key: dict(value) for key, value in DEFAULT_MODEL_EXTRAS.items()}

        extras = {}
        for key, value in section.items():
            token, _, kind = key.rpartition(".")
            if not token or kind not in ("spanet", "true"):
                raise ValueError(
                    "invalid [model_extras] key '{}', expected '<token>.spanet' "
                    "or '<token>.true'".format(key)
                )
            extras.setdefault(token, {})[kind] = json.loads(value)
        return extras


@lru_cache(maxsize=1)
def settings():
    """Return the (cached) :py:class:`Settings` singleton."""
    return Settings()


def _mount_root(path):
    """Return the mount point that has to be bound to make ``path`` visible.

    ``/eos/user/x/xyz/foo/bar`` -> ``/eos/user/x/xyz``, ``/afs/...`` -> ``/afs``.
    Everything else is bound as it is.
    """
    path = os.path.expandvars(path)
    parts = [p for p in path.split(os.sep) if p]
    if not parts:
        return path
    if parts[0] == "afs":
        return "/afs"
    if parts[0] == "eos" and len(parts) >= 4 and parts[1] == "user":
        return os.sep + os.sep.join(parts[:4])
    return path
