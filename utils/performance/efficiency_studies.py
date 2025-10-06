import argparse
import logging
import os

import awkward as ak
import h5py
import numpy as np
import vector

from efficiency_configuration import run2_dataset_DATA, run2_dataset_MC, spanet_dict, true_dict
from efficiency_functions import (
    best_reco_higgs,
    calculate_diff_efficiencies,
    calculate_efficiencies,
    distance_pt_func,
    load_jets_and_pairing,
    plot_diff_eff,
    plot_diff_eff_klambda,
    plot_histos_1d,
    plot_mhh,
    reco_higgs,
    separate_klambda,
)

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(funcName)s | %(message)s",
    datefmt="%d-%b-%y %H-%M-%S",
)


vector.register_numba()
vector.register_awkward()

parser = argparse.ArgumentParser(
    description="Convert awkward ntuples in parquet files to h5 files."
)
parser.add_argument(
    "-pd",
    "--plot-dir",
    default="plots",
    help="Directory to save the plots",
)
parser.add_argument(
    "-k",
    "--klambda",
    default=False,
    action="store_true",
    help="evaluate on different klambda values",
)
parser.add_argument(
    "-d",
    "--data",
    default=False,
    action="store_true",
    help="evaluate on data",
)

args = parser.parse_args()


if args.data:
    # remove non data samples
    run2_dataset = run2_dataset_DATA
    spanet_dict = {k: v for k, v in spanet_dict.items() if "data" in k}
else:
    run2_dataset = run2_dataset_MC
    spanet_dict = {k: v for k, v in spanet_dict.items() if "data" not in k}

mh_bins = np.linspace(0, 300, 150)
mh_bins_peak = np.linspace(100, 140, 20)
mh_bins_2d = (
    [np.linspace(50, 200, 80) for _ in range(3)]
    + [np.linspace(50, 200, 40) for _ in range(6)]
    + [np.linspace(0, 500, 50) for _ in range(2)]
    + [np.linspace(0, 500, 100) for _ in range(5)]
)

# For differential pairing efficiency by hh mass. (where the pairing efficiency is somehow added cumulative).
mhh_bins = np.linspace(250, 700, 10)

# Create plotting directory
plot_dir = args.plot_dir
os.makedirs(plot_dir, exist_ok=True)

# We are now filling a dictionary with one entry for each file.
# Then we extract all the information from the files, that we did before, but now targeted at the specific entries.
df_collection = {}
for model_name, file_dict in spanet_dict.items():
    spanetfile = h5py.File(file_dict["file"], "r")
    truefile = h5py.File(true_dict[file_dict["true"]]["name"], "r")
    truefile_klambda = true_dict[file_dict["true"]]["klambda"]

    idx_true = load_jets_and_pairing(truefile, "true")
    idx_spanet_pred = load_jets_and_pairing(spanetfile, "spanet")

    # load jet information
    jet_ptPNetRegNeutrino = truefile["INPUTS"]["Jet"]["ptPnetRegNeutrino"][()]
    jet_eta = truefile["INPUTS"]["Jet"]["eta"][()]
    jet_phi = truefile["INPUTS"]["Jet"]["phi"][()]
    jet_mass = truefile["INPUTS"]["Jet"]["mass"][()]

    jet_infos = [jet_ptPNetRegNeutrino, jet_eta, jet_phi, jet_mass]

    # These lists are to be expanded. Didn't think of a better way than to copy them here already
    # if not klambda, the two lists stay equal.
    alltrue_idx = [idx_true]
    allspanet_idx = [idx_spanet_pred]
    alljetinfos = [jet_infos]
    all_name_list = [model_name]

    if args.klambda and truefile_klambda != "none":
        logger.info("Separating the klambdas")
        # separate the different klambdas
        (
            true_kl_idx_list,
            spanet_kl_idx_list,
            kl_values,
            jet_infos_separate_klambda,
        ) = separate_klambda(
            jet_infos, truefile, spanetfile, idx_true, idx_spanet_pred
            )

        # I got now indexes for true and spanet and different kl.
        # For this, I will add them to a list. If no kl is there, I will just make it a list of one element
        alltrue_idx.extend(true_kl_idx_list)
        allspanet_idx.extend(spanet_kl_idx_list)
        alljetinfos.extend(jet_infos_separate_klambda)
        all_name_list.extend(kl_values)

    # Fully matched events
    mask_fully_matched = [ak.all(ak.all(idx >= 0, axis=-1), axis=-1) for idx in alltrue_idx]
    alltrue_idx_fully_matched = [idx[mask] for idx, mask in zip(alltrue_idx, mask_fully_matched)]
    allspanet_idx_fully_matched = [idx[mask] for idx, mask in zip(allspanet_idx, mask_fully_matched)]

    logger.info(f"Model name: {model_name}")
    logger.info(file_dict["label"])
    logger.info(f"alltrue_idx_fully_matched {[len(idx) for idx in alltrue_idx_fully_matched]}")
    logger.info(f"allspanet_idx_fully_matched {[len(idx) for idx in allspanet_idx_fully_matched]}")
    logger.info(f"allspanet_idx {[len(pred) for pred in allspanet_idx]}")
    logger.info(f"mask_fully_matched {[len(mask) for mask in mask_fully_matched]}")

    if not args.data:
        # Performing the matching
        frac_fully_matched, efficiencies_fully_matched, total_efficiencies_fully_matched, matching_eval_spanet = calculate_efficiencies(alltrue_idx_fully_matched, allspanet_idx_fully_matched, mask_fully_matched, file_dict["true"], kl_values, all_name_list, "fully matched")

        # do the same for partially matched events (only one higgs is matched)
        mask_1h = [
            ak.sum(ak.any(idx == -1, axis=-1) == 1, axis=-1) == 1 for idx in alltrue_idx
        ]
        idx_true_partially_matched_1h = [idx[mask] for idx, mask in zip(alltrue_idx, mask_1h)]
        idx_spanet_partially_matched_1h = [idx[mask] for idx, mask in zip(allspanet_idx, mask_1h)]

        frac_partially_matched_1h, efficiencies_partially_matched_spanet, total_efficiencies_partially_matched_spanet, matching_eval_spanet_partial = calculate_efficiencies(idx_true_partially_matched_1h, idx_spanet_partially_matched_1h, mask_1h, file_dict["true"], kl_values, all_name_list, "partially matched")

        # compute number of events with 0 higgs matched
        mask_0h = [ak.sum(ak.any(idx == -1, axis=-1), axis=-1) == 2 for idx in alltrue_idx]

        idx_true_unmatched = [idx[mask] for idx, mask in zip(alltrue_idx, mask_0h)]
        frac_unmatched = [ak.sum(mask) / len(mask) for mask in mask_0h]
        logger.info("\n")
        for label, frac in zip([file_dict["true"]] + kl_values.tolist(), frac_unmatched):
            logger.info(f"Fraction of unmatched events for {label}: {frac:.3f}")

    # create a LorentzVector for the jets
    jet = [
        ak.zip(
            {
                "pt": jet_i[0],
                "eta": jet_i[1],
                "phi": jet_i[2],
                "mass": jet_i[3],
            },
            with_name="Momentum4D",
        )
        for jet_i in alljetinfos
    ]

    # Reconstruct the Higgs boson candidates
    # of the jets considering the true pairings, the spanet pairings
    jet_fully_matched = [
        j[m] for j, m in zip(jet, mask_fully_matched)
    ]
    # Reconstruction of the Higgs boson candidates with the predicted/true pairings
    spanet_higgs_fully_matched = [
        best_reco_higgs(j, spanet_idx)
        for j, spanet_idx in zip(jet_fully_matched, allspanet_idx_fully_matched)
    ]
    if not args.data:
        true_higgs_fully_matched = [
            best_reco_higgs(j, idx)
            for j, idx in zip(jet_fully_matched, alltrue_idx_fully_matched)
        ]
        true_hh_fully_matched = [
            true_h_matched[:, 0] + true_h_matched[:, 1]
            for true_h_matched in true_higgs_fully_matched
        ]

    if not args.data:
        # Differential efficiency
        eff_dict = {
            "diff_eff_spanet": [],
            "unc_diff_eff_spanet": [],
            "total_diff_eff_spanet": [],
            "total_unc_diff_eff_spanet": [],
        }

        for true_hh, matched_spanet, mask_matched in zip(
                true_hh_fully_matched, matching_eval_spanet, mask_fully_matched
                ):
            temp = {k: [] for k in eff_dict.keys()}
            for i in range(1, len(mhh_bins)):
                mask = (true_hh.mass > mhh_bins[i - 1]) & (true_hh.mass < mhh_bins[i])

                eff_spanet, unc_eff_spanet, total_eff_spanet, unc_total_eff_spanet = calculate_diff_efficiencies(matched_spanet, mask, mask_matched)

                temp["diff_eff_spanet"].append(eff_spanet)
                temp["unc_diff_eff_spanet"].append(unc_eff_spanet)
                temp["total_diff_eff_spanet"].append(total_eff_spanet)
                temp["total_unc_diff_eff_spanet"].append(unc_total_eff_spanet)
                # for key, val in zip(temp.keys(), [eff_spanet, unc_eff_spanet, total_eff_spanet, unc_total_eff_spanet]):
                #     temp[key] = val
            # Remember, we iterate here through: [inclusive, *[single kls])
            for key in eff_dict.keys():
                eff_dict[key].append(temp[key])

    # Iteration over the different datasets over ####
    df_collection[model_name] = {
            "file_dict": file_dict,
            "spanet_higgs_fully_matched": spanet_higgs_fully_matched,
            }
    if args.klambda and truefile_klambda != "none":
        df_collection[model_name] = df_collection[model_name] | {
                "kl_values": kl_values,
                }
    if not args.data:
        df_collection[model_name] = df_collection[model_name] | {
                "efficiencies_fully_matched": efficiencies_fully_matched,
                "total_efficiencies_fully_matched": total_efficiencies_fully_matched,
                "diff_eff_spanet": eff_dict["diff_eff_spanet"],
                "unc_diff_eff_spanet": eff_dict["unc_diff_eff_spanet"],
                "total_diff_eff_spanet": eff_dict["total_diff_eff_spanet"],
                "total_unc_diff_eff_spanet": eff_dict["total_unc_diff_eff_spanet"],
                "true_hh_fully_matched":  true_hh_fully_matched,
                "true_higgs_fully_matched": true_higgs_fully_matched,
                }


# -- Loading Run2 model
truefile = h5py.File(true_dict[run2_dataset]["name"], "r")
truefile_klambda = true_dict[run2_dataset]["klambda"]
idx_true = load_jets_and_pairing(truefile, "true")

# load jet information
jet_ptPNetRegNeutrino = truefile["INPUTS"]["Jet"]["ptPnetRegNeutrino"][()]
jet_eta = truefile["INPUTS"]["Jet"]["eta"][()]
jet_phi = truefile["INPUTS"]["Jet"]["phi"][()]
jet_mass = truefile["INPUTS"]["Jet"]["mass"][()]

jet_infos = [jet_ptPNetRegNeutrino, jet_eta, jet_phi, jet_mass]

# These lists are to be expanded. Didn't think of a better way than to copy them here already
# if not klambda, the two lists stay equal.
alltrue_idx = [idx_true]
alljetinfos = [jet_infos]
all_name_list = [run2_dataset]

if args.klambda and truefile_klambda != "none":
    logger.info("Separating the klambdas")
    # separate the different klambdas
    (
        true_kl_idx_list,
        _,
        kl_values,
        jet_infos_separate_klambda,
    ) = separate_klambda(
        jet_infos, truefile, spanetfile, idx_true, None)  # Needs option for None in Spanet

    # I got now indexes for true and spanet and different kl.
    # For this, I will add them to a list. If no kl is there, I will just make it a list of one element
    alltrue_idx.extend(true_kl_idx_list)
    alljetinfos.extend(jet_infos_separate_klambda)
    all_name_list.extend(kl_values)

# Fully matched events
mask_fully_matched = [ak.all(ak.all(idx >= 0, axis=-1), axis=-1) for idx in alltrue_idx]
alltrue_idx_fully_matched = [idx[mask] for idx, mask in zip(alltrue_idx, mask_fully_matched)]

logger.info(f"Run2 dataset name: {run2_dataset}")
logger.info(f"alltrue_idx_fully_matched {[len(idx) for idx in alltrue_idx_fully_matched]}")
logger.info(f"mask_fully_matched {[len(mask) for mask in mask_fully_matched]}")

# create a LorentzVector for the jets
jet = [
    ak.zip(
        {
            "pt": jet_i[0],
            "eta": jet_i[1],
            "phi": jet_i[2],
            "mass": jet_i[3],
        },
        with_name="Momentum4D",
    )
    for jet_i in alljetinfos
]

# implement the Run 2 pairing algorithm
# TODO: extend to 5 jets cases (more comb idx)
comb_idx = [[(0, 1), (2, 3)], [(0, 2), (1, 3)], [(0, 3), (1, 2)]]

higgs_candidates_unflatten_order = [reco_higgs(j, comb_idx) for j in jet]
distance = [distance_pt_func(higgs, 1.04)[0] for higgs in higgs_candidates_unflatten_order]
max_pt = [distance_pt_func(higgs, 1.04)[1] for higgs in higgs_candidates_unflatten_order]

dist_order_idx = [ak.argsort(d, axis=1, ascending=True) for d in distance]
dist_order = [ak.sort(d, axis=1, ascending=True) for d in distance]

pt_order_idx = [ak.argsort(pt, axis=1, ascending=False) for pt in max_pt]
# if the distance between the two best candidates is less than 30, we do not consider the event
min_idx = [
    ak.where(d[:, 1] - d[:, 0] > 30, d_idx[:, 0], pt_idx[:, 0])
    for d, d_idx, pt_idx in zip(dist_order, dist_order_idx, pt_order_idx)
]

comb_idx = [
    np.tile(comb_idx, (len(m), 1, 1, 1)) for m in min_idx
]
# given the min_idx, select the correct combination corresponding to the index
comb_idx_min = [
    comb[np.arange(len(m)), m] for comb, m in zip(comb_idx, min_idx)
]
allrun2_idx_fully_matched = [
    ak.Array(comb)[m]
    for comb, m in zip(comb_idx_min, mask_fully_matched)
]

if not args.data:
    # compute efficiencies for fully matched events for Run 2 pairing
    frac_fully_matched, efficiencies_run2, total_efficiencies_run2, matching_eval_run2 = calculate_efficiencies(alltrue_idx_fully_matched, allrun2_idx_fully_matched, mask_fully_matched, run2_dataset, kl_values, all_name_list, "run2")

# Reconstruct the Higgs boson candidates with the efficiency_fully_matched_run2 = (
# of the jets considering the true pairings, the spanet pairings
# and the run2 pairings
jet_fully_matched = [j[m] for j, m in zip(jet, mask_fully_matched)]
run2_higgs_fully_matched = [best_reco_higgs(j, idx) for j, idx in zip(jet_fully_matched, allrun2_idx_fully_matched)]
if not args.data:
    true_higgs_fully_matched = [best_reco_higgs(j, idx) for j, idx in zip(jet_fully_matched, alltrue_idx_fully_matched)]
    true_hh_fully_matched = [true_h_matched[:, 0] + true_h_matched[:, 1] for true_h_matched in true_higgs_fully_matched]

if not args.data:
    # Differential efficiency
    eff_dict = {
        "diff_eff_run2": [],
        "unc_diff_eff_run2": [],
        "total_diff_eff_run2": [],
        "total_unc_diff_eff_run2": [],
    }
    for true_hh, matched_run2, mask_matched in zip(
            true_hh_fully_matched, matching_eval_run2, mask_fully_matched
            ):
        temp = {k: [] for k in eff_dict.keys()}
        for i in range(1, len(mhh_bins)):
            mask = (true_hh.mass > mhh_bins[i - 1]) & (true_hh.mass < mhh_bins[i])

            eff_run2, unc_eff_run2, total_eff_run2, unc_total_eff_run2 = calculate_diff_efficiencies(matched_run2, mask, mask_matched)
            temp["diff_eff_run2"].append(eff_run2)
            temp["unc_diff_eff_run2"].append(unc_eff_run2)
            temp["total_diff_eff_run2"].append(total_eff_run2)
            temp["total_unc_diff_eff_run2"].append(unc_total_eff_run2)
        for key in eff_dict.keys():
            eff_dict[key].append(temp[key])

r2_model = {
        "file_dict": file_dict,
        "run2_higgs_fully_matched": run2_higgs_fully_matched,
        }
if args.klambda and truefile_klambda != "none":
    r2_model = r2_model | {
            "kl_values": kl_values,
            }
if not args.data:
    r2_model = r2_model | {
            "efficiencies_fully_matched_run2": efficiencies_run2,
            "total_efficiencies_fully_matched_run2": total_efficiencies_run2,
            # Parameters for the diff_eff plots
            "diff_eff_run2": eff_dict["diff_eff_run2"],
            "unc_diff_eff_run2": eff_dict["unc_diff_eff_run2"],
            "total_diff_eff_run2": eff_dict["total_diff_eff_run2"],
            "total_unc_diff_eff_run2": eff_dict["total_unc_diff_eff_run2"],
            "true_hh_fully_matched":  true_hh_fully_matched,
            "true_higgs_fully_matched": true_higgs_fully_matched,
            }

# Plotting begins here
if not args.data:
    logger.info("\n")
    logger.info("Plotting efficiencies fully matched for all klambda values")
    # We are adding the run2 of the chosen element (defined in efficiency_calibrations) as last element
    logger.info(f"All datasets: {df_collection.keys()}")
    logger.info(f"Run2 set: {run2_dataset}")
    plot_diff_eff_klambda(
        [model["efficiencies_fully_matched"][1:] for model in df_collection.values()] + [r2_model["efficiencies_fully_matched_run2"][1:]],
        [model["kl_values"] for model in df_collection.values()] + [r2_model["kl_values"]],
        [model["file_dict"]["label"] for model in df_collection.values()] + [r"$D_{HH}$-method"],
        [model["file_dict"]["color"] for model in df_collection.values()] + ["yellowgreen"],
        "eff_fully_matched_allklambda",
        plot_dir,
    )
    plot_diff_eff_klambda(
        [model["total_efficiencies_fully_matched"][1:] for model in df_collection.values()] + [r2_model["total_efficiencies_fully_matched_run2"][1:]],
        [model["kl_values"] for model in df_collection.values()] + [r2_model["kl_values"]],
        [model["file_dict"]["label"] for model in df_collection.values()] + [r"$D_{HH}$-method"],
        [model["file_dict"]["color"] for model in df_collection.values()] + ["yellowgreen"],
        "tot_eff_fully_matched_allklambda",
        plot_dir,
    )

    logger.info("Plotting differential efficiencies")
    plot_diff_eff(
        mhh_bins,
        [model["diff_eff_spanet"][0] for model in df_collection.values()] + [r2_model["diff_eff_run2"][0]],
        [model["unc_diff_eff_spanet"][0] for model in df_collection.values()] + [r2_model["unc_diff_eff_run2"][0]],
        [model["file_dict"]["label"] for model in df_collection.values()] + [r"$D_{HH}$-method"],
        [model["file_dict"]["color"] for model in df_collection.values()] + ["yellowgreen"],
        plot_dir,
        "diff_eff_spanet",
    )
    plot_diff_eff(
        mhh_bins,
        [model["total_diff_eff_spanet"][0] for model in df_collection.values()] + [r2_model["total_diff_eff_run2"][0]],
        [model["total_unc_diff_eff_spanet"][0] for model in df_collection.values()] + [r2_model["total_unc_diff_eff_run2"][0]],
        [model["file_dict"]["label"] for model in df_collection.values()] + [r"$D_{HH}$-method"],
        [model["file_dict"]["color"] for model in df_collection.values()] + ["yellowgreen"],
        plot_dir,
        "total_diff_eff_spanet",
    )

    logger.info("Plotting mhh")
    plot_mhh(
        mhh_bins,
        list(df_collection.values())[0]["true_hh_fully_matched"][0].mass,
        plot_dir,
        "mhh_fully_matched",
    )

logger.info("Plotting higgs 1d all events")
for bins, name in zip([mh_bins, mh_bins_peak], ["", "_peak"]):
    for number in [1, 2]:
        plot_histos_1d(
            bins,
            [model["spanet_higgs_fully_matched"][0][:, number - 1].mass for model in df_collection.values()],  # spanet values
            r2_model["run2_higgs_fully_matched"][0][:, number - 1].mass,  # run2 values
            r2_model["true_higgs_fully_matched"][0][:, number - 1].mass if not args.data else None,  # true values
            [model["file_dict"]["label"] for model in df_collection.values()],
            [model["file_dict"]["color"] for model in df_collection.values()],
            number,
            name=name,
            plot_dir=plot_dir,
        )
