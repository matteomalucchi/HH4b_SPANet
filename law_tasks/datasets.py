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


def _load_yaml(path):
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


def load_config(path=None):
    """Return the dataset configuration as ``(defaults, datasets)``."""
    path = path or settings().dataset_config
    if not path or not os.path.exists(path):
        return {}, {}

    content = _load_yaml(path) or {}
    return content.get("defaults") or {}, content.get("datasets") or {}


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

    def jet_collections(self):
        """The jet collections, with a named group replaced by its content.

        This reproduces the expansion done by ``coffea_to_h5_direct.py``.
        """
        jets = list(self.jets)
        if len(jets) != 1 or not jets[0].isupper():
            return jets

        path = settings().collections_module
        spec = importlib.util.spec_from_file_location("law_collections", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        groups = getattr(module, "jet_collections_dict", {})
        return groups.get(jets[0], jets)

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

        command = " ".join(shlex.quote(str(part)) for part in parts)
        if self.convert_args:
            command += " " + self.convert_args
        return command


def resolve(name, config_path=None, **overrides):
    """Build a :py:class:`Dataset` from the configuration and the overrides.

    Values given on the command line win over the dataset entry, which wins
    over the ``defaults`` section of the dataset configuration.
    """
    defaults, datasets = load_config(config_path)

    if name in datasets:
        entry = datasets[name] or {}
    elif not overrides.get("output_prefix"):
        known = ", ".join(sorted(datasets)) or "none"
        raise ValueError(
            "unknown dataset '{}' (known datasets: {}); either add it to {} or "
            "pass at least --output-prefix".format(
                name, known, config_path or settings().dataset_config
            )
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
