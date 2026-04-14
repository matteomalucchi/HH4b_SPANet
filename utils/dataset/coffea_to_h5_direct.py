#!/usr/bin/env python3

import re
import os
import argparse
import awkward as ak
import coffea.util
import h5py
import numpy as np
import json
import pyarrow
import pyarrow.dataset as ds
import pathlib
from collections import defaultdict

from collections_coffea_to_h5_direct import (
    KEEP_TOGETHER_COLLECTIONS,
    jet_collections_dict,
    global_collections_dict,
)

COFFEA_PADDING_VALUE = -999.0
H5_PADDING_VALUE = 9999.0
SEED = 9999
_permutations = {}

RESONANCES = {
    "h1": (1, ("b1", "b2")),
    "h2": (2, ("b3", "b4")),
    "vbf": (3, ("q1", "q2")),
}
MIN_NUMBER_JETS = 4

# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------


p = argparse.ArgumentParser(
    "coffea → HDF5 converter",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)

p.add_argument("-i", "--input", required=True, help="Input coffea file path")
p.add_argument(
    "-o",
    "--output",
    required=True,
    help="Output HDF5 file path prefix (e.g. path/to/file/prefix_name)",
)
p.add_argument(
    "-r",
    "--regions",
    nargs="+",
    default=["2b_signal_region_postW", "4b_signal_region"],
    help="Regions to use for each class label",
)
p.add_argument(
    "-cl",
    "--class-labels",
    nargs="+",
    default=["DATA", "GluGlu"],
    help="Class labels to use for classification",
)
p.add_argument(
    "-j",
    "--jets",
    nargs="+",
    default=["JetTotalSPANetPtFlattenPadded", "JetTotalSPANetPadded"],
    help="Jet collections to process (must match keys in coffea file)",
)
p.add_argument(
    "-g",
    "--global-vars",
    nargs="+",
    default=["all"],
    help="Global variables to save, or 'all' to save all non-jet variables as global variables",
)
p.add_argument(
    "-m", "--max-jets", nargs="+", type=int, default=[5, 5], help="Max jets to keep"
)
p.add_argument("-tf", "--train-frac", type=float, default=0.8, help="Train fraction")
p.add_argument(
    "-ns", "--no-shuffle", action="store_true", help="Disable data shuffling"
)
p.add_argument(
    "-n",
    "--norm-weights",
    action="store_true",
    help="Normalize weights divided by sum_genweights",
)
p.add_argument(
    "--novars",
    action="store_true",
    help="If true, old save format without saved variations is expected",
    default=False,
)

args = p.parse_args()

# -----------------------------------------------------------------------------
# Utilities
# -----------------------------------------------------------------------------


def is_awkward(x):
    return isinstance(x, (ak.Array, ak.Record))


def create_resonances_targets_from_provenance(jets_prov, max_jets, resonances=None):
    """
    Parameters
    ----------
    jets_prov : awkward.Array
        Shape (Nevents, Njets), provenance labels:
          1 → h1
          2 → h2
          3 → VBF
          pad value → invalid / padded
    max_jets : int

    Returns
    -------
    dict with keys:
      ("h1", "b1"), ("h1", "b2"), ("h2", "b3"), ("h2", "b4"), ("vbf", "q1"), ("vbf", "q2")
    Each value is a numpy array of shape (Nevents,) with jet indices or -1
    """

    # local jet indices per event
    indices = ak.local_index(jets_prov)

    targets = {}

    for resonance, (prov_id, labels) in RESONANCES.items():
        if resonances is not None and resonance not in resonances:
            continue

        # mask jets belonging to this resonance
        mask = jets_prov == prov_id

        # pick jet indices, pad to exactly 2, fill missing with -1
        idx = ak.fill_none(ak.pad_none(indices[mask], 2, axis=1), -1)

        idx1 = idx[:, 0]
        idx2 = idx[:, 1]

        # enforce max_jets
        idx1 = ak.where(idx1 < max_jets, idx1, -1)
        idx2 = ak.where(idx2 < max_jets, idx2, -1)

        targets[(resonance, labels[0])] = ak.to_numpy(idx1)
        targets[(resonance, labels[1])] = ak.to_numpy(idx2)

    return targets


def create_dummy_targets(N, tr_targets, te_targets, train_mask, test_mask, shuffle):
    idx = 0
    for key in RESONANCES.keys():
        for label in RESONANCES[key][1]:
            arr = np.full(N, idx, dtype=np.int64)
            write_block_split(
                tr_targets,
                te_targets,
                [key, label],
                arr,
                train_mask,
                test_mask,
                shuffle,
            )
            idx += 1


def unflatten_to_jagged(flat, counts):
    """flat: 1D array of length sum(counts)
    counts: 1D int array of length Nevents
    returns: awkward jagged array (Nevents, Nj)
    """
    counts = np.asarray(counts).astype(np.int64)

    if flat.ndim != 1:
        raise ValueError(f"Expected flat 1D array, got shape {flat.shape}")
    if counts.ndim != 1:
        raise ValueError(f"Expected 1D counts array, got shape {counts.shape}")
    if flat.shape[0] != int(counts.sum()):
        raise ValueError("Flat length != sum(counts)")

    return ak.unflatten(flat, counts)

def pad_clip_jets(jets, max_jets):

    # replace coffea padding to h5 padding
    jets = ak.where(jets == COFFEA_PADDING_VALUE, H5_PADDING_VALUE, jets)

    # Awkward jagged
    if is_awkward(jets):
        padded = ak.pad_none(jets, max_jets, axis=1, clip=True)
        dense = ak.to_numpy(ak.fill_none(padded, H5_PADDING_VALUE))
        return dense

    arr = np.asarray(jets)

    # Ragged numpy object → awkward
    if arr.dtype == object and arr.ndim == 1:
        jets_ak = ak.Array(arr)
        padded = ak.pad_none(jets_ak, max_jets, axis=1, clip=True)
        dense = ak.to_numpy(ak.fill_none(padded, H5_PADDING_VALUE))
        return dense

    # Dense numpy
    if arr.ndim < 2:
        raise ValueError(f"Invalid jet array shape {arr.shape}")

    N, Nj = arr.shape[:2]
    use = min(Nj, max_jets)

    out = np.full((N, max_jets) + arr.shape[2:], H5_PADDING_VALUE, dtype=arr.dtype)
    out[:, :use, ...] = arr[:, :use, ...]

    return out


def infer_collection_and_var(name):
    """Rules:
    - if name starts with "events_", treat as Event-level collection "Event"
    - else split into (collection, var) by first underscore, EXCEPT keep-together collections
      e.g. "HH_pt" -> ("HH", "pt")
           "add_jet1pt_pt" -> ("add_jet1pt", "pt")
    - if no underscore, put it under Event-level "Event"
    """
    if name.startswith("events_"):
        return "Event", name[len("events_") :]

    for c in KEEP_TOGETHER_COLLECTIONS:
        if name.startswith(c + "_"):
            return c, name[len(c) + 1 :]

    if "_" in name:
        return name.split("_", 1)

    return "Event", name


def dataset_to_class_index(dataset_key, class_labels):
    key = dataset_key.lower()
    for idx, lbl in enumerate(class_labels):
        if lbl.lower() in key:
            return idx
    raise ValueError(f"Dataset key '{dataset_key}' does not match any class label")


def get_permutation(N):
    global _permutations
    if N not in _permutations:
        rng = np.random.default_rng(SEED)
        _permutations[N] = rng.permutation(N)
    return _permutations[N]


def cast_floats32(x):
    x = np.array(x)
    if np.issubdtype(x.dtype, np.floating):
        return x.astype(np.float32, copy=False)
    return x


def cast_int64(x):
    x = np.array(x)
    if np.issubdtype(x.dtype, np.integer):
        return x.astype(np.int64, copy=False)
    return x


def extract_param_value(s, param):
    """
    Extract a parameter value from a string.

    Parameters
    ----------
    s : str
        Input string.
    param : str
        Parameter name to extract (e.g. 'kl', 'CV', 'C2V', 'C3', 'kt').

    Returns
    -------
    float or None
        Extracted value or None if not found.
    """

    # pattern allows "-" or "_" after param name
    pattern = rf"{param}[-_]([mp0-9]+)"

    match = re.search(pattern, s)
    if not match:
        return None

    value_str = match.group(1)

    # convert encoding: m -> -, p -> .
    value_str = value_str.replace("m", "-").replace("p", ".")

    return float(value_str)


# -----------------------------------------------------------------------------
# HDF5 helpers
# -----------------------------------------------------------------------------


def add_column_to_group(group, path, data, shuffle, compression="gzip"):
    """Create or append to a resizable dataset located at group/<path_parts...>.
    data: numpy array, first dimension is N (events)
    """
    for p in path[:-1]:
        group = group.require_group(p)

    name = path[-1]
    data = np.asarray(data)

    if data.dtype == object:
        raise TypeError(f"Object dtype at {'/'.join(path)}")

    if name not in group:
        dset = group.create_dataset(
            name,
            data=data,
            maxshape=(None,) + data.shape[1:],
            chunks=True,
            compression=compression,
            shuffle=False,
        )
    else:
        dset = group[name]
        old = dset.shape[0]
        dset.resize((old + data.shape[0],) + dset.shape[1:])
        dset[old:] = data

    if shuffle:
        full = dset[()]
        full = full[get_permutation(len(full))]
        dset[...] = full


def write_block_split(train, test, path, data, train_mask, test_mask, shuffle):
    """Append split slices of `data` to train/test datasets."""
    add_column_to_group(train, path, data[train_mask], shuffle)
    add_column_to_group(test, path, data[test_mask], shuffle)


def get_parquet_save_directory(input_parquet):
    config_json_path = os.path.join(os.path.dirname(input_parquet), "config.json")

    with open(config_json_path, "r") as f:
        config = json.load(f)
    col_dir = config["workflow"]["workflow_options"]["dump_columns_as_arrays_per_chunk"]
    # Strip the redirector (e.g. root://t3dcachedb03.psi.ch:1094/) from the path if it exists
    if col_dir is not None and "://" in col_dir:
        col_dir = col_dir.split("://")[-1].split("/", 1)[-1]
        col_dir = "/" + col_dir.split("/", 1)[-1]

    return col_dir


def load_cols_parquet(rootdir):
    cols = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
    rootdir = pathlib.Path(rootdir)

    # Expected structure: rootdir/dataset/region/variation/
    for dataset_dir in rootdir.iterdir():
        if not dataset_dir.is_dir():
            continue

        for region_dir in dataset_dir.iterdir():
            if not region_dir.is_dir():
                continue

            for variation_dir in region_dir.iterdir():
                if not variation_dir.is_dir():
                    continue

                cols[dataset_dir.name][dataset_dir.name][region_dir.name][
                    variation_dir.name
                ] = ds.dataset(variation_dir, format="parquet")

    return cols


# -----------------------------------------------------------------------------
# Main conversion
# -----------------------------------------------------------------------------


def coffea_to_h5(
    coffea_path,
    h5_path,
    regions,
    class_labels,
    jet_collections,
    global_variables,
    max_jets,
    train_frac,
    do_data_shuffling,
    columns_key="columns",
    weight_name="weight",
):
    """Convert the columns from coffea to h5 format to use as SPANet inputs."""
    accumulator = coffea.util.load(coffea_path)
    cols = accumulator[columns_key]
    sum_genweights = accumulator["sum_genweights"]

    if cols == {}:
        rootdir = get_parquet_save_directory(coffea_path)
        print("Empty columns, trying to read from parquet files from:", rootdir)
        cols = load_cols_parquet(rootdir)

    path_base = os.path.splitext(h5_path)[0]
    out_dir_name = os.path.dirname(h5_path)
    if out_dir_name:
        os.makedirs(out_dir_name, exist_ok=True)

    if (
        len(jet_collections) == 1
        and jet_collections[0].isupper()
        and jet_collections[0] in jet_collections_dict
    ):
        jet_collections = jet_collections_dict[jet_collections[0]]

    for j, jet_coll_group in enumerate(jet_collections):

        # initialize the random numbers for every collection
        # so that the order remains the same
        rng = np.random.default_rng(SEED)

        # make sure jet_coll_group is a dictionary and put default values
        if type(jet_coll_group) != dict:
            jet_coll_group = {
                jet_coll_group: {
                    "saved_name": "Jet",
                    "max_num_jets": max_jets[j],
                    "resonances": None,
                }
            }

        jet_coll_group_str = "_".join(list(jet_coll_group.keys()))

        h5_tr = f"{path_base}{jet_coll_group_str}_train.h5"
        h5_te = f"{path_base}{jet_coll_group_str}_test.h5"

        with h5py.File(h5_tr, "w") as ftr, h5py.File(h5_te, "w") as fte:

            def mk(f):
                return (
                    f.create_group("INPUTS"),
                    f.create_group("WEIGHTS"),
                    f.create_group("CLASSIFICATIONS"),
                    f.create_group("TARGETS"),
                )

            tr_in, tr_w, tr_c, tr_t = mk(ftr)
            te_in, te_w, te_c, te_t = mk(fte)

            sample_keys = list(cols.keys())
            for i, skey in enumerate(sample_keys):
                # shuffle only on the last dataset to avoid multiple shufflings
                shuffle = do_data_shuffling and (i == len(sample_keys) - 1)

                class_idx = dataset_to_class_index(skey, class_labels)
                region = regions[class_idx]

                for dataset in cols[skey]:
                    if region not in cols[skey][dataset]:
                        raise ValueError(
                            f"Region '{region}' not found for dataset '{skey}' dataset '{dataset}'"
                        )

                    if args.novars:
                        payload = cols[skey][dataset][region]
                    else:
                        variation = "nominal"
                        payload = cols[skey][dataset][region][variation]

                    # if pyarrow dataset, convert to table to obtain the arrays
                    if type(payload) == pyarrow._dataset.FileSystemDataset:
                        payload = payload.to_table()
                        payload_columns = payload.schema.names
                    else:
                        payload_columns = list(payload.keys())

                    w = payload[weight_name].value
                    if args.norm_weights:
                        print(
                            f"weights before norm = {np.mean(w):.3f}, {np.std(w):.3f}"
                        )
                        w = w / sum_genweights[dataset]
                        print(
                            f"Dividing by sum_genweights = {sum_genweights[dataset]:.3f}",
                            f"weights after norm = {np.mean(w):.8f}, {np.std(w):.8f}",
                        )
                    N = len(w)

                    train_mask = (
                        rng.random(N) < train_frac
                        if shuffle
                        else np.arange(N) < int(N * train_frac)
                    )
                    test_mask = ~train_mask

                    write_block_split(
                        tr_w,
                        te_w,
                        ["weight"],
                        cast_floats32(w),
                        train_mask,
                        test_mask,
                        shuffle,
                    )

                    cls = np.full(N, class_idx, dtype=np.int64)
                    write_block_split(
                        tr_c,
                        te_c,
                        ["EVENT", "class"],
                        cls,
                        train_mask,
                        test_mask,
                        shuffle,
                    )
                    for jet_i, (jet_coll, jet_info_dict) in enumerate(
                        jet_coll_group.items()
                    ):

                        jet_counts = None
                        jetN = f"{jet_coll}_N"
                        if jetN in payload_columns:
                            jet_counts = payload[jetN].value
                            jet_pt = unflatten_to_jagged(
                                np.array(payload[f"{jet_coll}_pt"].value),
                                jet_counts,
                            )
                        else:
                            jet_pt = ak.Array(payload[f"{jet_coll}_pt"])

                        # Define the jet mask
                        mask_jet_pt = (
                            ak.to_numpy(
                                ak.fill_none(
                                    ak.pad_none(
                                        jet_pt,
                                        jet_info_dict["max_num_jets"],
                                        clip=True,
                                    ),
                                    COFFEA_PADDING_VALUE,
                                )
                            )
                            != COFFEA_PADDING_VALUE
                        )

                        # check that there are at least MIN_NUMBER_JETS jets in the event
                        if np.any(np.sum(mask_jet_pt, axis=1) < MIN_NUMBER_JETS):
                            raise ValueError(
                                f"Event has less than {MIN_NUMBER_JETS} jets. Check dataset {dataset}"
                            )

                        jet_mask_written = False

                        # Create the Targets
                        prov_key = f"{jet_coll}_provenance"
                        if prov_key in payload_columns:
                            if jet_counts is not None:
                                jets_prov = unflatten_to_jagged(
                                    np.array(payload[prov_key].value), jet_counts
                                )
                            else:
                                jets_prov = ak.Array(payload[prov_key])

                            # Split train / test *before* creating targets
                            prov_tr = jets_prov[train_mask]
                            prov_te = jets_prov[test_mask]

                            targets_tr = create_resonances_targets_from_provenance(
                                prov_tr,
                                jet_info_dict["max_num_jets"],
                                jet_info_dict["resonances"],
                            )
                            targets_te = create_resonances_targets_from_provenance(
                                prov_te,
                                jet_info_dict["max_num_jets"],
                                jet_info_dict["resonances"],
                            )

                            for (r, q), arr in targets_tr.items():
                                add_column_to_group(
                                    tr_t, [r, q], cast_int64(arr), shuffle
                                )

                            for (r, q), arr in targets_te.items():
                                add_column_to_group(
                                    te_t, [r, q], cast_int64(arr), shuffle
                                )
                        else:
                            create_dummy_targets(
                                N, tr_t, te_t, train_mask, test_mask, shuffle
                            )

                        for name in payload_columns:
                            arr = payload[name]

                            if name == weight_name:
                                continue

                            coll, var = infer_collection_and_var(name)
                            arr_u = arr.value
                            is_jet = coll == jet_coll and var != "N"

                            if (
                                (
                                    name in global_variables
                                    or (
                                        "all" in global_variables
                                        and f"{coll}_N" not in payload_columns
                                    )
                                )
                                and jet_i == 0
                                and type(arr_u[0]) is not np.ndarray
                            ):
                                is_global = True
                                glob_coll = coll
                                glob_var = var
                            elif (
                                (
                                    len(global_variables) == 1
                                    and global_variables[0].isupper()
                                    and global_variables[0] in global_collections_dict
                                    and name
                                    in global_collections_dict[global_variables[0]][j]
                                )
                                and jet_i == 0
                                and type(arr_u[0]) is not np.ndarray
                            ):
                                if (
                                    "PtFlatten" in jet_coll and "PtFlatten" not in name
                                ) or (
                                    "PtFlatten" not in jet_coll and "PtFlatten" in name
                                ):
                                    print(
                                        f"WARNING: Mixing pt-flatten and non-pt-flatten collections! \nMaybe need to change the global variable configuration, maybe you just need to reorder the global variables."
                                    )

                                is_global = True
                                glob_coll = global_collections_dict[
                                    global_variables[0]
                                ][j][name]["saved_name_coll"]
                                glob_var = global_collections_dict[global_variables[0]][
                                    j
                                ][name]["saved_name_var"]
                            else:
                                is_global = False
                                glob_coll = None
                                glob_var = None

                            if is_jet or is_global:
                                print(
                                    f"Processing {skey} {dataset} {region} variable {name} with shape {arr_u.shape} (jet: {is_jet}, global: {is_global})"
                                )

                            if is_jet:
                                jets = (
                                    unflatten_to_jagged(arr_u, jet_counts)
                                    if arr_u.ndim == 1 and jet_counts is not None
                                    else ak.Array(arr_u)
                                )

                                jtr, jte = jets[train_mask], jets[test_mask]
                                mtr, mte = (
                                    mask_jet_pt[train_mask],
                                    mask_jet_pt[test_mask],
                                )
                                dtr = pad_clip_jets(jtr, jet_info_dict["max_num_jets"])
                                dte = pad_clip_jets(jte, jet_info_dict["max_num_jets"])

                                add_column_to_group(
                                    tr_in,
                                    [jet_info_dict["saved_name"], var],
                                    cast_floats32(dtr),
                                    shuffle,
                                )
                                add_column_to_group(
                                    te_in,
                                    [jet_info_dict["saved_name"], var],
                                    cast_floats32(dte),
                                    shuffle,
                                )

                                if not jet_mask_written:
                                    add_column_to_group(
                                        tr_in,
                                        [jet_info_dict["saved_name"], "MASK"],
                                        mtr,
                                        shuffle,
                                    )
                                    add_column_to_group(
                                        te_in,
                                        [jet_info_dict["saved_name"], "MASK"],
                                        mte,
                                        shuffle,
                                    )
                                    jet_mask_written = True

                            elif is_global:
                                # replace coffea padding to h5 padding
                                arr_u = ak.where(
                                    arr_u == COFFEA_PADDING_VALUE,
                                    H5_PADDING_VALUE,
                                    arr_u,
                                )
                                write_block_split(
                                    tr_in,
                                    te_in,
                                    [glob_coll, glob_var],
                                    cast_floats32(arr_u),
                                    train_mask,
                                    test_mask,
                                    shuffle,
                                )

                    # Get the various k-values for each dataset
                    if "GluGlu" in dataset:
                        kl_val = extract_param_value(dataset, "kl")
                        kl_val_array = kl_val * ak.ones_like(payload[weight_name].value)
                        write_block_split(
                            tr_in,
                            te_in,
                            ["Event", "kl"],
                            cast_floats32(kl_val_array),
                            train_mask,
                            test_mask,
                            shuffle,
                        )
                    elif "VBF" in dataset:
                        # Get the C2V and not the k_lambda because the c2v is unique for each dataset of vbf
                        # while the k_lambda is not
                        c2v_val = extract_param_value(dataset, "C2V")
                        c2v_val_array = c2v_val * ak.ones_like(payload[weight_name].value)
                        write_block_split(
                            tr_in,
                            te_in,
                            ["Event", "kl"],
                            cast_floats32(c2v_val_array),
                            train_mask,
                            test_mask,
                            shuffle,
                        )
                    else:
                        kl_padding = H5_PADDING_VALUE * ak.ones_like(payload[weight_name].value)
                        write_block_split(
                            tr_in,
                            te_in,
                            ["Event", "kl"],
                            cast_floats32(kl_padding),
                            train_mask,
                            test_mask,
                            shuffle,
                        )

        print(f"Wrote: {h5_tr}, {h5_te}")


if __name__ == "__main__":

    coffea_to_h5(
        coffea_path=args.input,
        h5_path=args.output,
        regions=args.regions,
        class_labels=args.class_labels,
        jet_collections=args.jets,
        global_variables=args.global_vars,
        max_jets=args.max_jets,
        train_frac=args.train_frac,
        do_data_shuffling=not args.no_shuffle,
    )
