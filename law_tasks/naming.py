"""Derivation of every name used by the pipeline from the options file.

The rules implemented here are the ones that were previously applied by hand:
the test file follows from the training file, the ``true_dict`` key, the plot
label and the plot directory follow from the options file basename.
"""

import json
import os
import re

from law_tasks.config import settings


def load_options(options_file):
    """Load a SPANet options JSON file and return its content."""
    with open(options_file) as fobj:
        return json.load(fobj)


def model_key(options_file, suffix=""):
    """``hh4b_pairing_..._ClassLoss7`` from ``.../hh4b_pairing_..._ClassLoss7.json``."""
    return os.path.splitext(os.path.basename(options_file))[0] + (suffix or "")


def training_file(options_file):
    """The ``training_file`` entry of the options file, with variables expanded."""
    options = load_options(options_file)
    path = options.get("training_file")
    if not path:
        raise ValueError("no 'training_file' entry in {}".format(options_file))
    return os.path.expandvars(path)


def derive_test_file(train_file):
    """Map a training file onto the file the model has to be evaluated on.

    ``_train.h5`` becomes ``_test.h5`` and every ``PtFlatten`` is dropped from
    the *basename*: a model trained on a pt flattened sample has to be
    evaluated on the non flattened one.
    """
    directory, basename = os.path.split(train_file)

    if not basename.endswith("_train.h5"):
        raise ValueError(
            "training file '{}' does not end with '_train.h5', pass the test "
            "file explicitly with --test-file".format(train_file)
        )
    basename = basename[: -len("_train.h5")] + "_test.h5"
    basename = basename.replace("PtFlatten", "")

    if "PtFlatten" in basename:  # defensive, replace() above removes all of them
        raise ValueError("could not remove 'PtFlatten' from '{}'".format(basename))

    return os.path.join(directory, basename)


def prediction_name(test_file):
    """Name of the prediction file written by ``spanet.predict``."""
    return "predict_" + os.path.basename(test_file)


def _strip_model_prefix(key):
    prefix = settings().model_prefix
    return key[len(prefix):] if prefix and key.startswith(prefix) else key


def _drop_training_only_tokens(tokens):
    patterns = [re.compile(r"\A(?:{})\Z".format(p)) for p in settings().training_only_tokens]
    return [t for t in tokens if not any(p.match(t) for p in patterns)]


def derive_true_key(key):
    """``true_dict`` key of the dataset a model is evaluated on.

    Tokens that only describe the training (the loss scale, the number of
    epochs, the pt flattening) are dropped, so that models differing only by
    those share the same truth entry.
    """
    stripped = _strip_model_prefix(key)
    tokens = _drop_training_only_tokens(stripped.split("_"))
    return settings().true_key_prefix + "_".join(tokens)


def derive_label(key):
    """Human readable legend entry, e.g. ``VBF pair+clas - JetTotal - DNN Vars``."""
    cfg = settings()

    stripped = _strip_model_prefix(key)
    has_prefix = bool(cfg.label_strip) and stripped.startswith(cfg.label_strip)
    if has_prefix:
        stripped = stripped[len(cfg.label_strip):]

    tokens = []
    for token in stripped.split("_"):
        if not token:
            continue
        token = cfg.label_replacements.get(token, token)
        if token in cfg.label_train_tokens:
            token += " Train"
        tokens.append(token)

    if has_prefix and cfg.label_prefix:
        tokens.insert(0, cfg.label_prefix)

    return " - ".join(tokens)


def derive_plot_dir(key):
    """Parent directory of all plots of one model, e.g. ``plots_VBFPairing_...``."""
    return "plots_" + _strip_model_prefix(key)


def pick_color(used_colors, palette=None):
    """First color of the palette that is not used by another model yet."""
    palette = palette or settings().palette
    used = set(used_colors)
    for color in palette:
        if color not in used:
            return color
    # more models than colors: cycle, keeping the assignment deterministic
    return palette[len(used) % len(palette)]


def extra_entries(key):
    """Additional ``spanet_dict``/``true_dict`` items implied by the model name.

    Configured in the ``[model_extras]`` section of ``law.cfg``.
    """
    spanet_extra, true_extra = {}, {}
    for token, extras in settings().model_extras.items():
        if token in key:
            spanet_extra.update(extras.get("spanet", {}))
            true_extra.update(extras.get("true", {}))
    return spanet_extra, true_extra
