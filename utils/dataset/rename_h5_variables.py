# Rename INPUTS/TARGETS variables (or any group/dataset) in a SPANet h5 file,
# copying it to a new file. Edit RENAME_MAP below to configure which full
# paths get changed.

import argparse

import h5py

# full source path -> full destination path. Only exact matches are renamed;
# anything not listed is copied unchanged. The destination can move a
# dataset/group to a different parent group entirely (intermediate groups are
# created automatically), so this covers both INPUTS/... and TARGETS/... vars.
RENAME_MAP = {
    "INPUTS/Jet/btagB": "INPUTS/Jet/btagPNetB",
    "INPUTS/Jet/btagB_3wp": "INPUTS/Jet/btagPNetB_3wp",
    "INPUTS/Jet/btagB_5wp": "INPUTS/Jet/btagPNetB_5wp",
}


def copy_and_rename(src_path, dst_path, rename_map=RENAME_MAP):
    with h5py.File(src_path, "r") as fin, h5py.File(dst_path, "w") as fout:

        def copy(name, obj):
            target = rename_map.get(name, name)
            if isinstance(obj, h5py.Group):
                out = fout.require_group(target)
            else:
                out = fout.create_dataset(
                    target,
                    shape=obj.shape,
                    dtype=obj.dtype,
                    chunks=obj.chunks,
                    compression=obj.compression,
                    compression_opts=obj.compression_opts,
                )
                # copy in slices along the first axis to keep memory bounded
                if obj.shape:
                    step = max(
                        1, 1_000_000 // max(1, int(obj.size / max(1, obj.shape[0])))
                    )
                    for i in range(0, obj.shape[0], step):
                        out[i : i + step] = obj[i : i + step]
                else:
                    out[()] = obj[()]
            for k, v in obj.attrs.items():
                out.attrs[k] = v
            if target != name:
                print(f"renamed: {name}  ->  {target}")

        fin.visititems(copy)
        for k, v in fin.attrs.items():
            fout.attrs[k] = v

    print("wrote", dst_path)


if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description="Rename INPUTS/TARGETS variable names in a SPANet h5 file "
        "according to RENAME_MAP, writing the result to a new file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("-i", "--input", required=True, help="Input h5 file path")
    p.add_argument(
        "-o",
        "--output",
        required=True,
        help="Output h5 file path (created/overwritten)",
    )
    args = p.parse_args()

    copy_and_rename(args.input, args.output)
