# coffea_to_h5_direct.py

Converts `.coffea` accumulator files directly to HDF5 files in the SPANet input format, without an intermediate Parquet step.

## Basic usage

```bash
python utils/dataset/coffea_to_h5_direct.py \
    -i input.coffea \
    -o path/to/output/prefix_name
```

The script writes one pair of files per jet collection group:

```
path/to/output/prefix_name<JetCollectionName>_train.h5
path/to/output/prefix_name<JetCollectionName>_test.h5
```

## All CLI options

| Flag | Default | Description |
|------|---------|-------------|
| `-i`, `--input` | *(required)* | Input `.coffea` file path |
| `-o`, `--output` | *(required)* | Output HDF5 path prefix (e.g. `path/to/file/prefix_`) |
| `-r`, `--regions` | `2b_signal_region_postW 4b_signal_region` | Regions to use, one per class label (positional correspondence) |
| `-cl`, `--class-labels` | `DATA GluGlu` | Class labels for classification, one per region |
| `-j`, `--jets` | `JetTotalSPANetPtFlattenPadded JetTotalSPANetPadded` | Jet collections to process (see [Collection configuration](#collection-configuration)) |
| `-g`, `--global-vars` | `all` | Global (event-level) variables to save, or `all` (see [Global variables](#global-variables)) |
| `-m`, `--max-jets` | `5 5` | Maximum number of jets to keep, one value per jet collection |
| `-tf`, `--train-frac` | `0.8` | Fraction of events used for training |
| `-ns`, `--no-shuffle` | off | Disable random shuffling of events |
| `-n`, `--norm-weights` | off | Normalize weights by `sum_genweights` |
| `-rw`, `--remove-high-weights` | off | Remove events with weight > 100 (only for regions whose name contains `postW`) |
| `--novars` | off | Expect the old save format without variations (no `nominal` key) |

## Collection configuration

Collection configuration is defined in `collections_coffea_to_h5_direct.py`.
The file exports three objects used by the main script:

- `KEEP_TOGETHER_COLLECTIONS` — prefixes that should not be split on the first underscore when inferring the collection name from a variable name.
- `jet_collections_dict` — named groups of jet collections (see below).
- `global_collections_dict` — named groups of global variables (see below).

### Easy mode: plain collection names

For the simplest case, pass one or more coffea collection names directly:

```bash
python utils/dataset/coffea_to_h5_direct.py \
    -i input.coffea -o out/prefix_ \
    -j JetTotalSPANetPtFlattenPadded JetTotalSPANetPadded \
    -m 5 5
```

Each name is treated as a single-collection group saved under the HDF5 key `Jet` with up to `--max-jets` jets, no resonance targets.

### Advanced mode: predefined uppercase group keys

Pass a single **uppercase** key (e.g. `JET_COLLECTIONS_SEPARATE_HIGGS_VBF`) as the `-j` argument. The script looks it up in `jet_collections_dict` and replaces it with the full list of collection groups defined there.

```bash
python utils/dataset/coffea_to_h5_direct.py \
    -i input.coffea -o out/prefix_ \
    -j JET_COLLECTIONS_SEPARATE_HIGGS_VBF \
    -g GLOBAL_COLLECTIONS_VBF
```

### Jet collection group format

Each entry in `jet_collections_dict` is a **list of groups**. A group is a dictionary mapping coffea collection names to their configuration:

```python
jet_collections_dict = {
    "MY_GROUP_KEY": [          # one entry per output file pair
        {
            "CoffeaCollectionName": {
                "saved_name": "HDF5GroupName",   # name in INPUTS/<saved_name>/
                "max_num_jets": 4,               # pad/clip to this many jets
                "resonances": ["h1", "h2"],      # None → dummy targets; list → real targets
                # "min_num_jets": 4,             # optional, default 4
            },
            # optionally a second collection in the same output file:
            "AnotherCoffeaCollection": {
                "saved_name": "JetVBF",
                "max_num_jets": 5,
                "resonances": ["vbf"],
            },
        },
        # additional groups → additional output file pairs
    ],
}
```

Resonance labels must be a subset of `h1`, `h2`, `vbf` (matching the provenance encoding 1, 2, 3 in the coffea file). Set `resonances: None` to write dummy integer targets instead.

### Global variables

By default (`-g all`) every variable whose collection has no corresponding `_N` count column is treated as a global (event-level) variable and stored under `INPUTS/<Collection>/<var>`.

To select specific variables explicitly, pass their coffea names:

```bash
-g events_mjjJetTotalSPANetPtFlattenPadded events_detaJetTotalSPANetPtFlattenPadded
```

To use a predefined uppercase group key from `global_collections_dict`, pass it as the sole `-g` argument:

```bash
-g GLOBAL_COLLECTIONS_VBF
```

#### Global collection group format

Each entry in `global_collections_dict` is a **list of dictionaries**, one per jet collection group (same length and order as the corresponding jet group list). Each dictionary maps coffea variable names to their HDF5 destination:

```python
global_collections_dict = {
    "MY_GLOBAL_KEY": [
        {   # corresponds to jet group index 0
            "events_mjjJetColl": {
                "saved_name_coll": "Event",   # INPUTS/<saved_name_coll>/
                "saved_name_var": "mjjVBF",   # INPUTS/Event/mjjVBF
            },
            # more variables ...
        },
        {   # corresponds to jet group index 1
            # ...
        },
    ],
}
```

### `KEEP_TOGETHER_COLLECTIONS`

When inferring `(collection, variable)` from a coffea column name, the script splits on the first underscore. Prefixes listed in `KEEP_TOGETHER_COLLECTIONS` are exempt and treated as the full collection name:

```python
KEEP_TOGETHER_COLLECTIONS = ["add_jet1pt"]
# "add_jet1pt_pt" → collection="add_jet1pt", var="pt"  (not collection="add", var="jet1pt_pt")
```

## Output HDF5 structure

```
train.h5 / test.h5
├── INPUTS/
│   ├── <saved_name>/       # one group per jet collection
│   │   ├── pt
│   │   ├── eta
│   │   ├── ...
│   │   └── MASK
│   └── Event/              # global variables
│       ├── kl
│       └── ...
├── TARGETS/
│   ├── h1/  b1, b2
│   ├── h2/  b3, b4
│   └── vbf/ q1, q2
├── WEIGHTS/
│   └── weight
└── CLASSIFICATIONS/
    └── EVENT/
        └── class
```

## Examples

### Simple: two plain collections, one region pair

```bash
python utils/dataset/coffea_to_h5_direct.py \
    -i ./output_all.coffea \
    -o ./h5/spanet_ \
    -r 2b_signal_region_postW 4b_signal_region \
    -cl DATA GluGlu \
    -j JetTotalSPANetPtFlattenPadded JetTotalSPANetPadded \
    -m 5 5 \
    --norm-weights
```

### Advanced: separate Higgs and VBF jet collections with VBF global variables

```bash
python utils/dataset/coffea_to_h5_direct.py \
    -i ./output_all.coffea \
    -o ./h5/spanet_ \
    -r 2b_signal_region_postW 4b_signal_region \
    -cl DATA GluGlu \
    -j JET_COLLECTIONS_SEPARATE_HIGGS_VBF \
    -g GLOBAL_COLLECTIONS_VBF
```
