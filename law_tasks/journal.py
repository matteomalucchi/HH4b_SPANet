"""Record of what the pipeline did: the steps, the commands and their output.

Every ``law run`` invocation gets a directory of its own, next to what the
steps produced: the generated configurations of a model, the h5 files of a
dataset.

    <base>/journal/<run id>/run.jsonl              one line per step and command
    <base>/journal/<run id>/001_ConvertDataset.log the output of that command

so that a run can be read back exactly as it happened, including the bash
command each step executed.  ``<base>/journal/latest`` points at the directory
of the most recent run.
"""

import itertools
import json
import os
import threading
import time

#: one identifier per ``law run``, so that the steps of a run stay together
RUN_ID = "{}_{}".format(time.strftime("%Y%m%d_%H%M%S"), os.getpid())


def run_dir(base):
    """Directory of the current run, created on first use."""
    directory = os.path.join(base, "journal", RUN_ID)
    if not os.path.isdir(directory):
        os.makedirs(directory, exist_ok=True)
        _point_latest_at(directory)
    return directory


def _point_latest_at(directory):
    """Keep a ``latest`` link next to the runs; a file when links are not possible."""
    latest = os.path.join(os.path.dirname(directory), "latest")
    try:
        if os.path.islink(latest) or os.path.exists(latest):
            os.remove(latest)
        os.symlink(os.path.basename(directory), latest)
    except OSError:
        # EOS through fuse does not always allow symlinks
        try:
            with open(latest, "w") as fobj:
                fobj.write(directory + "\n")
        except OSError:
            pass


#: commands are numbered in the order they run, over the whole run
_counter = itertools.count(1)
_lock = threading.Lock()


def log_path(base, task):
    """Path of the file holding the output of the next command."""
    with _lock:
        index = next(_counter)
    return os.path.join(run_dir(base), "{:03d}_{}.log".format(index, task))


def record(base, entry):
    """Append one entry to the journal of the current run."""
    entry = dict(entry)
    entry.setdefault("time", time.strftime("%Y-%m-%d %H:%M:%S"))

    path = os.path.join(run_dir(base), "run.jsonl")
    with open(path, "a") as fobj:
        fobj.write(json.dumps(entry) + "\n")
    return path


def journal_path(base):
    return os.path.join(run_dir(base), "run.jsonl")
