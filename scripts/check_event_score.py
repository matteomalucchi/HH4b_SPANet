#!/usr/bin/env python3
"""Print the SPANet classification score for given event number(s) in a prediction h5 file."""
import argparse

import h5py
import numpy as np

DEFAULT_FILE = (
    "/eos/user/m/mmalucch/php-plots/HH4b/SPANet_studies/training_outputs/"
    "2026-10-06_out_hh4b_pairing_vbf_ggf_all_Klambda_VBFPairingAfterHiggsPairingWithZSamples_"
    "JetHiggsSeparate_DNNVars_VBFNoKinCut_ClassLoss7_2024_NoBtag/out_seed_trainings_100/version_0/"
    "predict_VBFPairingAfterHiggsPairingWithZSamples_DNNVars_vbfregions_2024SPANetHiggsTraining_"
    "parking_presel_JetGoodVBFMergedProvVBFPadded_JetGoodProvHiggsPadded_test.h5"
)
DEFAULT_FILE = ("/eos/user/m/mmalucch/spanet_infos/spanet_inputs/vbf/11_05_02_out_ggf_vbf_spanet_input_AllKlambda_DetaMjjCentrality_VBFPairingAfterHiggsPairingWithZSamples_DNNVars_vbfregions_2024SPANetHiggsTraining_parking_presel/NormWeightPerSample_VBFPairingAfterHiggsPairingWithZSamples_DNNVars_vbfregions_2024SPANetHiggsTraining_parking_presel_JetGoodVBFMergedProvVBFPadded_JetGoodProvHiggsPadded_train.h5"
)
DEFAULT_FILE = ("/eos/user/m/mmalucch/php-plots/HH4b/SPANet_studies/training_outputs/2026-10-12_out_hh4b_pairing_vbf_ggf_all_Klambda_VBFPairingAfterHiggsPairingWithZSamples_JetHiggsSeparate_DNNVars_VBFNoKinCut_ClassLoss7_2024_NormWeightsPerSample_NoBtag/out_seed_trainings_100/version_0/predict_train_NormWeightPerSample_VBFPairingAfterHiggsPairingWithZSamples_DNNVars_vbfregions_2024SPANetHiggsTraining_parking_presel_JetGoodVBFMergedProvVBFPadded_JetGoodProvHiggsPadded_train.h5"
)

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    "events", type=int, nargs="*",
    help="Event number(s) to look up. If omitted, print all events for --kl",
)
parser.add_argument("-i", "--input", default=DEFAULT_FILE, help="Prediction h5 file")
parser.add_argument("--kl", type=float, default=None, help="Only show matches with this kl value")
args = parser.parse_args()
if not args.events and args.kl is None:
    parser.error("give at least one event number or --kl")

with h5py.File(args.input, "r") as f:
    event = f["INPUTS/Event/event"][:].astype(np.int64)
    kl = f["INPUTS/Event/kl"][:]
    scores = f["CLASSIFICATIONS/EVENT/class"][:]
    vbf = f["TARGETS/vbf"]
    q1, q2 = vbf["q1"][:], vbf["q2"][:]
    try:
        assign_prob = vbf["assignment_probability"][:]
    except KeyError:
        assign_prob = None


def print_row(i):
    score_str = ", ".join(f"class{c}={s:.6f}" for c, s in enumerate(scores[i]))
    print(
        f"  row={i:<7d} event={event[i]:<9d} kl={kl[i]:<6g} {score_str}  "
        f"vbf_pair=({q1[i]},{q2[i]}) assign_prob={assign_prob[i]:.4f}"
    )


if not args.events:
    # Print all events for the given kl
    idx = np.where(np.isclose(kl, args.kl))[0]
    if len(idx) == 0:
        print(f"kl={args.kl}: no events found. Available kl: {np.unique(kl)}")
    else:
        print(f"kl={args.kl}: {len(idx)} event(s)")
        for i in idx:
            print_row(i)

for ev in args.events:
    idx = np.where(event == ev)[0]
    if args.kl is not None:
        idx = idx[np.isclose(kl[idx], args.kl)]
    if len(idx) == 0:
        print(f"Event {ev}: not found")
        continue
    print(f"Event {ev}: {len(idx)} match(es)")
    for i in idx:
        print_row(i)
