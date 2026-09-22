"""Description of the datasets that are converted from coffea to SPANet h5.

A dataset is defined in a YAML file (``law_tasks/datasets.yaml`` by default,
see the ``dataset_config`` setting) and every field can be overridden on the
command line, so a dataset that is not in the file can be converted as well.

The h5 files that ``coffea_to_h5_direct.py`` writes follow from the output
prefix and the jet collections, which is what lets the law tasks know their
outputs without running the conversion first.
"""

import importlib.util
import os
import shlex
from functools import lru_cache

from law_tasks.config import settings

#: fields of a dataset, with their defaults
FIELDS = {
    "coffea_dir": "",
    "coffea_file": "output_all.coffea",
    "output_dir": "",
    "output_prefix": "",
    "regions": [],
    "class_labels": [],
    "jets": [],
    "global_vars": [],
    "jet_like_global_vars": [],
    "max_jets": [],
    "resonances": "",
    "convert_args": "",
    "collections": [],
    "remote_dir": "",
}

#: fields holding a list of values
LIST_FIELDS = [
    "regions",
    "class_labels",
    "jets",
    "global_vars",
    "jet_like_global_vars",
    "max_jets",
    "collections",
]


@lru_cache(maxsize=None)
def _collections_module(path):
    spec = importlib.util.spec_from_file_location("law_collections", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def collections_module():
    """``collections_coffea_to_h5_direct.py``, with the named groups."""
    return _collections_module(settings().collections_module)


def load_yaml(path):
    try:
        from omegaconf import OmegaConf

        return OmegaConf.to_container(OmegaConf.load(path), resolve=True)
    except ImportError:
        pass

    try:
        import yaml
    except ImportError:  # pragma: no cover
        raise ImportError(
            "reading {} needs omegaconf or PyYAML, install one of them".format(path)
        )

    with open(path) as fobj:
        return yaml.safe_load(fobj) or {}


#: file names that say nothing about the dataset they describe
GENERIC_NAMES = ("dataset", "datasets", "config", "conversion", "spanet")


def config_name(path):
    """Name of the dataset a configuration of its own describes."""
    stem = os.path.splitext(os.path.basename(path))[0]
    if stem.lower() in GENERIC_NAMES:
        return os.path.basename(os.path.dirname(os.path.abspath(path))) or stem
    return stem


def load_config(path=None):
    """Return the dataset configuration as ``(defaults, datasets, standalone)``.

    Two shapes are read.  A file with a ``datasets`` mapping describes several
    datasets, each selected by name -- the central ``law_tasks/datasets.yaml``
    is one of those.  A file without it describes a single dataset, its fields
    at the top level: that is the one written next to the coffea file it
    converts, and then ``coffea_dir`` is the directory holding it and the name
    comes from the file, or from that directory when the file is called
    something like ``dataset.yaml``.
    """
    path = path or settings().dataset_config
    if not path or not os.path.exists(path):
        return {}, {}, False

    content = load_yaml(path) or {}
    if "datasets" in content:
        return content.get("defaults") or {}, content.get("datasets") or {}, False

    entry = {key: value for key, value in content.items() if key != "defaults"}
    entry.setdefault("coffea_dir", os.path.dirname(os.path.abspath(path)))
    return content.get("defaults") or {}, {config_name(path): entry}, True


def _as_list(value):
    if value is None or value == "":
        return []
    if isinstance(value, (list, tuple)):
        return [str(v) for v in value]
    return shlex.split(str(value))


class Dataset(object):
    """One coffea file and the h5 files derived from it."""

    def __init__(self, name, **fields):
        self.name = name
        for field, default in FIELDS.items():
            value = fields.get(field, default)
            setattr(self, field, _as_list(value) if field in LIST_FIELDS else value)

        if not self.output_prefix:
            raise ValueError(
                "dataset '{}' has no output_prefix; add it to {} or pass "
                "--output-prefix".format(name, settings().dataset_config)
            )

    # -- paths -------------------------------------------------------------

    @property
    def coffea_path(self):
        """Absolute path of the coffea file to convert."""
        directory = self.coffea_dir
        if not os.path.isabs(directory):
            directory = os.path.join(settings().coffea_base, directory)
        return os.path.abspath(os.path.join(directory, self.coffea_file))

    @property
    def local_dir(self):
        """Directory the h5 files are written to (default: the coffea one)."""
        directory = self.output_dir or os.path.dirname(self.coffea_path)
        if not os.path.isabs(directory):
            directory = os.path.join(settings().coffea_base, directory)
        return os.path.abspath(directory)

    @property
    def remote_path(self):
        """Directory the h5 files are copied to on the remote host."""
        directory = self.remote_dir
        if not directory:
            raise ValueError(
                "dataset '{}' has no remote_dir; add it to the dataset "
                "configuration or pass --remote-dir".format(self.name)
            )
        if os.path.isabs(directory):
            return directory
        return os.path.join(settings().remote_input_base, directory)

    # -- outputs -----------------------------------------------------------

    def expand_group(self, values, dict_name, field):
        """Replace a named group by its content, as the converter does.

        ``coffea_to_h5_direct.py`` replaces a single upper case name by the
        entry of the corresponding dictionary of
        ``collections_coffea_to_h5_direct.py``; a name that is not in there is
        a typo, and silently converting the wrong thing is worse than stopping.
        """
        values = list(values)
        if len(values) != 1 or not values[0].isupper():
            return values

        groups = getattr(collections_module(), dict_name, {})
        if values[0] not in groups:
            raise ValueError(
                "unknown {} group '{}' in dataset '{}'; {} of {} holds: "
                "{}".format(
                    field,
                    values[0],
                    self.name,
                    dict_name,
                    settings().collections_module,
                    ", ".join(sorted(groups)) or "nothing",
                )
            )
        return groups[values[0]]

    def jet_collections(self):
        """The jet collections, with a named group replaced by its content."""
        return self.expand_group(self.jets, "jet_collections_dict", "jet collection")

    def global_collections(self):
        """The global variables, with a named group replaced by its content."""
        return self.expand_group(
            self.global_vars, "global_collections_dict", "global variable"
        )

    def check_collections(self):
        """Stop when the global groups do not cover the jet collection groups.

        ``coffea_to_h5_direct.py`` takes the global variables of the *n*-th jet
        collection group from the *n*-th entry of the global group, so a
        shorter one fails in the middle of the conversion.
        """
        jets = self.jet_collections()
        if len(self.global_vars) != 1 or not self.global_vars[0].isupper():
            return

        groups = self.global_collections()
        if len(groups) < len(jets):
            raise ValueError(
                "the global variable group '{}' describes {} jet collection "
                "group(s) while '{}' has {}; every jet collection group needs "
                "its own entry in global_collections_dict".format(
                    self.global_vars[0],
                    len(groups),
                    self.jets[0] if self.jets else "the jet collections",
                    len(jets),
                )
            )

    def collection_names(self):
        """Name of each produced jet collection group, e.g. ``JetTotalSPANetPadded``."""
        names = []
        for group in self.jet_collections():
            names.append("_".join(group) if isinstance(group, dict) else str(group))
        return names

    def files(self, collections=None):
        """``{<group>_<train|test>: <path>}`` of all h5 files of this dataset."""
        # the converter strips an extension from the prefix before appending
        base = os.path.join(self.local_dir, os.path.splitext(self.output_prefix)[0])

        wanted = collections if collections is not None else self.collections
        files = {}
        for name in self.collection_names():
            if wanted and name not in wanted:
                continue
            for split in ("train", "test"):
                files["{}_{}".format(name, split)] = "{}{}_{}.h5".format(
                    base, name, split
                )
        return files

    def all_files(self):
        """Every h5 file written by the conversion, ignoring ``collections``."""
        return self.files(collections=[])

    def transfer_files(self):
        """The h5 files that are copied to the remote host."""
        return self.files()

    def remote_files(self):
        """``{<group>_<train|test>: <remote path>}`` after the transfer."""
        return {
            key: os.path.join(self.remote_path, os.path.basename(path))
            for key, path in self.transfer_files().items()
        }

    # -- command -----------------------------------------------------------

    def convert_command(self, script, python="python3"):
        """The ``coffea_to_h5_direct.py`` call converting this dataset."""
        parts = [python, script, "-i", self.coffea_path]
        parts += ["-o", os.path.join(self.local_dir, self.output_prefix)]

        for flag, values in (
            ("--regions", self.regions),
            ("--class-labels", self.class_labels),
            ("-j", self.jets),
            ("-g", self.global_vars),
            ("-jg", self.jet_like_global_vars),
            ("-m", self.max_jets),
        ):
            if values:
                parts += [flag] + list(values)

        if self.resonances:
            parts += ["-rs", self.resonances]

        command = " ".join(shlex.quote(str(part)) for part in parts)
        if self.convert_args:
            command += " " + self.convert_args
        return command


def resolve(name="", config_path=None, **overrides):
    """Build a :py:class:`Dataset` from the configuration and the overrides.

    Values given on the command line win over the dataset entry, which wins
    over the ``defaults`` section of the dataset configuration.
    """
    defaults, datasets, standalone = load_config(config_path)
    path = config_path or settings().dataset_config

    if standalone:
        # the configuration next to the coffea file describes that one
        # dataset, and is named after the file or the directory
        only = next(iter(datasets))
        if name and name != only:
            raise ValueError(
                "{} describes the single dataset '{}'; drop --dataset or pass "
                "--dataset {}".format(path, only, only)
            )
        name = only
    elif not name and not overrides.get("output_prefix"):
        raise ValueError(
            "no dataset given: pass --dataset <name> for one of [{}], or "
            "--dataset-config <file> describing the dataset next to its coffea "
            "file".format(", ".join(sorted(datasets)) or "none")
        )

    if name in datasets:
        entry = datasets[name] or {}
    elif not overrides.get("output_prefix"):
        known = ", ".join(sorted(datasets)) or "none"
        raise ValueError(
            "unknown dataset '{}' (known datasets: {}); add it to {}, write a "
            "configuration next to the coffea file and pass --dataset-config, "
            "or pass at least --output-prefix".format(name, known, path)
        )
    else:
        entry = {}

    fields = dict(defaults)
    fields.update(entry)
    for field, value in overrides.items():
        if value not in (None, "", [], ()):
            fields[field] = value

    unknown = set(fields) - set(FIELDS)
    if unknown:
        raise ValueError(
            "dataset '{}' has unknown fields: {}".format(name, ", ".join(sorted(unknown)))
        )

    return Dataset(name, **fields)
