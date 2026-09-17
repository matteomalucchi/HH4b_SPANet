#!/usr/bin/env python3
"""Build a 2-class (HH vs QCD) pretraining subset from a 5-class SPANet h5 file.

Original 5-class encoding in CLASSIFICATIONS/EVENT/class: 0=ggF, 1=VBF, 2=ZH, 3=ZZ, 4=QCD
Pretrain encoding: keep only ggF/VBF/QCD events, merge ggF+VBF -> label 0 (HH), QCD -> label 1.
ZH and ZZ events are dropped entirely for this stage.

Works on any h5 file with this structure (test or train) - just point --input at it.
"""
import argparse
import h5py
import numpy as np

LABEL_KEY = "CLASSIFICATIONS/EVENT/class"

KEEP_ORIGINAL_CLASSES = {0, 1, 4}   # ggF, VBF, QCD (drop ZH=2, ZZ=3)
NEW_LABEL = {0: 0, 1: 0, 4: 1}      # ggF, VBF -> HH (0); QCD -> QCD (1)


def build_subset(input_path, output_path):
    with h5py.File(input_path, "r") as src:
        orig_labels = src[LABEL_KEY][:]
        mask = np.isin(orig_labels, list(KEEP_ORIGINAL_CLASSES))
        print(f"{input_path}: keeping {mask.sum()}/{len(orig_labels)} events")

        with h5py.File(output_path, "w") as dst:
            def visitor(name, obj):
                if not isinstance(obj, h5py.Dataset):
                    return
                data = obj[...]
                if data.shape[0] != mask.shape[0]:
                    raise ValueError(
                        f"Dataset {name} has first dim {data.shape[0]}, expected {mask.shape[0]} "
                        "(not event-indexed the way this script assumes)"
                    )
                data = data[mask]
                if name == LABEL_KEY:
                    data = np.vectorize(NEW_LABEL.get)(data).astype(obj.dtype)
                dst.create_dataset(name, data=data, dtype=obj.dtype, compression="gzip")

            src.visititems(visitor)

    with h5py.File(output_path, "r") as f:
        vals, counts = np.unique(f[LABEL_KEY][:], return_counts=True)
        print("new label counts (0=HH, 1=QCD):", dict(zip(vals.tolist(), counts.tolist())))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Source h5 file (5-class)")
    parser.add_argument("--output", required=True, help="Destination h5 file (2-class HH vs QCD)")
    args = parser.parse_args()
    build_subset(args.input, args.output)