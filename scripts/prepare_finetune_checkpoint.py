#!/usr/bin/env python3
"""Prepare a stage-1 (pretrain) checkpoint for stage-2 (fine-tune) loading.

Builds the real stage-2 SPANet model (from --event_file/--training_file/--options_file,
exactly as spanet.train does) purely to read off each layer's expected shape, then filters
the stage-1 checkpoint's state dict down to only the keys whose shape matches. Keys that
exist in both but with a different shape (e.g. the classifier head after growing from 2 to
4 classes, or a branch's first embedding layer after adding an input variable) are dropped
so they fall back to fresh random init instead of crashing `load_state_dict`.

Must be run in your SPANet training environment (needs torch, pytorch_lightning, spanet
importable) -- not the lightweight plotting venv.

Usage:
    python prepare_finetune_checkpoint.py \
        --checkpoint stage1_run/version_0/checkpoints/best.ckpt \
        --event_file event_files/hh4b_5class.yaml \
        --training_file stage2_train.h5 \
        --validation_file stage2_val.h5 \
        --options_file options_files/HH4b/classification/.../my_options.json \
        --output stage1_filtered_for_stage2.pth

Then launch stage 2 with:
    python -m spanet.train --options_file <same options_file> \
        --event_file <same event_file> \
        --training_file stage2_train.h5 --validation_file stage2_val.h5 \
        --state_dict stage1_filtered_for_stage2.pth \
        -n <run_name> --log_dir <run_name> --gpus <n>
    # add --freeze_state_dict if you want to freeze the transferred layers at first
"""
import argparse
import json
import sys

import torch


def build_stage2_reference_model(event_file, training_file, validation_file, options_file):
    from spanet import JetReconstructionModel, Options

    options = Options(event_file, training_file, validation_file)
    if options_file is not None:
        with open(options_file, "r") as f:
            options.update_options(json.load(f))

    # Building the model loads the full training dataset to size every layer
    # (num classes, num input features per branch, etc.) -- same cost as spanet.train pays.
    model = JetReconstructionModel(options)
    return model


def filter_checkpoint(checkpoint_path, reference_state):
    raw = torch.load(checkpoint_path, map_location="cpu")
    stage1_state = raw["state_dict"] if "state_dict" in raw else raw

    kept, dropped, new_layers = {}, [], []

    for key, tensor in stage1_state.items():
        if key not in reference_state:
            dropped.append((key, tuple(tensor.shape), None))
            continue
        if tuple(tensor.shape) != tuple(reference_state[key].shape):
            dropped.append((key, tuple(tensor.shape), tuple(reference_state[key].shape)))
            continue
        kept[key] = tensor

    for key in reference_state:
        if key not in stage1_state:
            new_layers.append((key, tuple(reference_state[key].shape)))

    return kept, dropped, new_layers


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--checkpoint", required=True, help="Stage-1 (pretrain) .ckpt file")
    parser.add_argument("--event_file", required=True, help="Stage-2 event.yaml")
    parser.add_argument("--training_file", required=True, help="Stage-2 training .h5")
    parser.add_argument("--validation_file", required=True, help="Stage-2 validation .h5")
    parser.add_argument("--options_file", default=None, help="options.json (same one used for both stages)")
    parser.add_argument("--output", required=True, help="Where to write the filtered state dict (.pth)")
    parser.add_argument("--spanet-dir", default=None, help="Path to SPANet repo, if not pip-installed")
    args = parser.parse_args()

    if args.spanet_dir:
        sys.path.insert(0, args.spanet_dir)

    print("Building stage-2 reference model (this loads the full stage-2 training dataset)...")
    model = build_stage2_reference_model(
        args.event_file, args.training_file, args.validation_file, args.options_file
    )
    reference_state = model.state_dict()

    print(f"Filtering stage-1 checkpoint: {args.checkpoint}")
    kept, dropped, new_layers = filter_checkpoint(args.checkpoint, reference_state)

    print(f"\nTransferred {len(kept)}/{len(reference_state)} tensors from stage 1.\n")

    if dropped:
        print(f"Dropped {len(dropped)} tensors (shape changed -> will be randomly re-initialized):")
        for key, old_shape, new_shape in dropped:
            if new_shape is None:
                print(f"  {key}: was {old_shape}, no longer exists in stage-2 model")
            else:
                print(f"  {key}: {old_shape} -> {new_shape}")

    if new_layers:
        print(f"\n{len(new_layers)} tensors exist only in the stage-2 model (new layers/branches, randomly initialized):")
        for key, shape in new_layers:
            print(f"  {key}: {shape}")

    torch.save({"state_dict": kept}, args.output)
    print(f"\nSaved filtered checkpoint to {args.output}")
    print("Use it with: python -m spanet.train ... --state_dict " + args.output)


if __name__ == "__main__":
    main()