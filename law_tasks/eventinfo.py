"""What the event file of a model says about its jets and its resonances.

The efficiency and the ROC configurations need to know which sequential input
holds the Higgs jets, which one holds the VBF jets, how many jets of the VBF
collection belong to the Higgs and by how much the indices predicted by SPANet
are shifted with respect to the ones stored in the file.  All of it follows
from the event file the model is trained with, so none of it has to be written
by hand:

    INPUTS:                       EVENT:              ->  jet_coll_higgs: JetHiggs
      SEQUENTIAL:                   h1:                   jet_coll_vbf:   JetVBF
        JetHiggs: ...                 - b1: JetHiggs      n_higgs_jets:   0
        JetVBF:   ...                 - b2: JetHiggs      offset_jet_idx_higgs: 0
                                    vbf:                  offset_jet_idx_vbf:  -4
                                      - q1: JetVBF        resonances: DEFAULT_RESONANCES
                                      - q2: JetVBF

The event file also says which efficiencies can be computed at all: one
without a Higgs resonance cannot be asked for the Higgs pairing efficiency.
"""

import os
import shlex
from functools import lru_cache

from law_tasks.datasets import load_yaml

#: name of the VBF resonance in the event files
VBF_RESONANCE = "vbf"

#: daughters of every entry of RESONANCES_DICT in
#: utils/performance/efficiency_functions.py, which is what ``resonances``
#: selects; the first match wins, and the first entry is the default of the
#: efficiency script
RESONANCE_SETS = {
    "OLD_RESONANCES": {
        "h1": ("b1", "b2"),
        "h2": ("b3", "b4"),
        VBF_RESONANCE: ("q1", "q2"),
    },
    "DEFAULT_RESONANCES": {
        "h1": ("b1", "b2"),
        "h2": ("b1", "b2"),
        VBF_RESONANCE: ("q1", "q2"),
    },
}


class EventInfo(object):
    """The parts of a SPANet event file the performance plots depend on."""

    def __init__(self, path, sequential, event):
        #: path of the event file
        self.path = path
        #: names of the sequential inputs, in the order SPANet concatenates them
        self.sequential = list(sequential)
        #: ``{resonance: [(daughter, collection or None), ...]}``
        self.event = dict(event)

    def __repr__(self):
        return "EventInfo({})".format(os.path.basename(self.path))

    # -- resonances --------------------------------------------------------

    @property
    def higgs_resonances(self):
        return [name for name in self.event if name != VBF_RESONANCE]

    @property
    def has_higgs(self):
        return bool(self.higgs_resonances)

    @property
    def has_vbf(self):
        return VBF_RESONANCE in self.event

    @property
    def resonances(self):
        """Name of the ``RESONANCES_DICT`` entry matching the daughters."""
        mine = {
            name: tuple(daughter for daughter, _ in daughters)
            for name, daughters in self.event.items()
        }
        for key, known in RESONANCE_SETS.items():
            if all(known.get(name) == daughters for name, daughters in mine.items()):
                return key
        return None

    # -- collections -------------------------------------------------------

    def collection(self, resonance):
        """The sequential input the daughters of ``resonance`` come from."""
        for _, collection in self.event.get(resonance, []):
            if collection:
                return collection
        # the daughters of a file with a single collection do not name it
        return self.sequential[0] if len(self.sequential) == 1 else None

    @property
    def jet_coll_higgs(self):
        """The collection the masks and the jet four-vectors are read from."""
        if self.has_higgs:
            return self.collection(self.higgs_resonances[0])
        # without a Higgs resonance the plots still need a collection, and the
        # one that carries the targets is the one that is there
        return self.collection(VBF_RESONANCE)

    @property
    def jet_coll_vbf(self):
        """The collection of the VBF jets, when it is one of its own."""
        if not self.has_vbf:
            return None
        collection = self.collection(VBF_RESONANCE)
        return collection if collection != self.jet_coll_higgs else None

    @property
    def n_higgs_jets(self):
        """Jets of the VBF collection that belong to the Higgs, or ``None``.

        A collection of its own -- ``JetVBF`` -- holds the VBF jets alone,
        while the collection that holds every jet of the event starts with the
        four Higgs ones, which is what the efficiency script assumes by
        default.  ``None`` keeps that default.
        """
        collection = self.collection(VBF_RESONANCE) or self.jet_coll_higgs
        if collection and "vbf" in collection.lower():
            return 0
        return None

    # -- index offsets -----------------------------------------------------

    def offset(self, resonance, slots):
        """Shift between the indices SPANet predicts and the ones in the file.

        SPANet numbers the jets over its sequential inputs concatenated, the
        file stores them per collection, so the indices of a collection are
        shifted by the number of slots of the collections before it.
        """
        collection = self.collection(resonance)
        if collection not in self.sequential:
            return 0
        before = self.sequential[: self.sequential.index(collection)]
        return -sum(slots[name] for name in before)

    def needs_slots(self):
        """Collections whose number of slots is needed for the offsets."""
        needed = set()
        for resonance in self.event:
            collection = self.collection(resonance)
            if collection in self.sequential:
                needed.update(self.sequential[: self.sequential.index(collection)])
        return sorted(needed)

    # -- configuration entries --------------------------------------------

    def collection_keys(self):
        """The keys describing the collections, for a ``true_dict`` entry."""
        keys = {}
        if self.jet_coll_higgs:
            keys["jet_coll_higgs"] = self.jet_coll_higgs
        if self.jet_coll_vbf:
            keys["jet_coll_vbf"] = self.jet_coll_vbf
        if self.n_higgs_jets is not None:
            keys["n_higgs_jets"] = self.n_higgs_jets
        return keys

    def model_keys(self, slots):
        """The keys of a ``spanet_dict`` entry: collections and offsets."""
        keys = self.collection_keys()
        if self.has_higgs:
            keys["offset_jet_idx_higgs"] = self.offset(
                self.higgs_resonances[0], slots
            )
        if self.has_vbf:
            keys["offset_jet_idx_vbf"] = self.offset(VBF_RESONANCE, slots)
        if self.resonances:
            keys["resonances"] = self.resonances
        return keys

    # -- which plots can be made -------------------------------------------

    def unsupported(self, plot_args):
        """Why a plot run with ``plot_args`` cannot be made, or ``None``.

        ``efficiency_studies.py`` computes the Higgs pairing efficiency unless
        it is given ``--ignore-higgs``, and the VBF one when it is given
        ``--vbf``; a resonance that the event file does not define is not in
        the prediction either, and the plot fails looking for it.
        """
        tokens = shlex.split(plot_args or "")
        if not ({"-ih", "--ignore-higgs"} & set(tokens)) and not self.has_higgs:
            return "{} defines no Higgs resonance".format(os.path.basename(self.path))
        if ({"-v", "--vbf"} & set(tokens)) and not self.has_vbf:
            return "{} defines no VBF resonance".format(os.path.basename(self.path))
        return None


@lru_cache(maxsize=None)
def load(path):
    """Read an event file into an :class:`EventInfo`.

    The result is cached: one run asks for it once per task, and an event file
    does not change while the pipeline runs.
    """
    content = load_yaml(path) or {}

    inputs = content.get("INPUTS") or {}
    sequential = list(inputs.get("SEQUENTIAL") or {})

    event = {}
    for resonance, daughters in (content.get("EVENT") or {}).items():
        parsed = []
        for daughter in daughters or []:
            if isinstance(daughter, dict):
                parsed.extend(daughter.items())
            else:
                parsed.append((str(daughter), None))
        event[resonance] = parsed

    return EventInfo(path, sequential, event)


def input_slots(h5_path, names):
    """Number of slots of every collection of ``names`` in an input file."""
    if not names:
        return {}

    try:
        import h5py
    except ImportError:  # pragma: no cover
        raise ImportError(
            "reading the number of jet slots of {} needs h5py".format(h5_path)
        )

    slots = {}
    with h5py.File(h5_path, "r") as fobj:
        for name in names:
            try:
                slots[name] = int(fobj["INPUTS"][name]["MASK"].shape[1])
            except KeyError:
                raise RuntimeError(
                    "the input file {} has no collection 'INPUTS/{}/MASK'; the "
                    "event file and the file the model is evaluated on do not "
                    "match".format(h5_path, name)
                )
    return slots
