import os
import argparse
from collections import defaultdict

import numpy as np
import awkward as ak

import vector
import matplotlib.pyplot as plt

vector.register_numba()
vector.register_awkward()

from coffea.util import load
from coffea.processor.accumulator import column_accumulator
from coffea.processor import accumulate

# Read arguments from command line: input file and output directory. Description: script to convert ntuples from coffea file to parquet file.
parser = argparse.ArgumentParser(
    description="Convert awkward ntuples in coffea files to parquet files."
)
parser.add_argument("-i", "--input", type=str, required=True, help="Input coffea file")
parser.add_argument("-o", "--output", type=str, default="", help="Output directory")
parser.add_argument(
    "-c",
    "--cat",
    type=str,
    default="inclusive",
    required=False,
    help="Event category",
)
parser.add_argument(
    "-s",
    "--sample",
    type=str,
    default="",
    required=False,
    help="Sample to consider. If not specified, all the samples are considered.",
)
parser.add_argument(
    "-k",
    "--kl",
    type=str,
    default="",
    required=False,
    help="kl coefficient to consider. If not specified, all the kl coefficients are considered.",
)
parser.add_argument(
    "-r",
    "--reduce",
    default=False,
    action="store_true",
    help="Reduce the number of events in the dataset.",
)

parser.add_argument(
    "--oversample",
    default=False,
    action="store_true",
    help="Oversample the dataset.",
)
parser.add_argument(
    "--novars",
    action="store_true",
    help="If true, old save format without saved variations is expected",
    default=False,
)

args = parser.parse_args()

NUMBER_QCD_4B= 121529 #NOTE: this has changed
NUMBER_QCD_2B= 4424846
NUMBER_DATA_2B= 5913750
idx = np.random.RandomState(seed=42).permutation(NUMBER_QCD_2B)


## Loading the exported dataset
# We open the .coffea file and read the output accumulator. The ntuples for the training are saved under the key `columns`.

if not os.path.exists(args.input):
    raise ValueError(f"Input file {args.input} does not exist.")
main_dir = args.output if args.output else os.path.dirname(args.input)
if not os.path.exists(main_dir):
    os.makedirs(main_dir)

df = load(args.input)

print(df["cutflow"].keys())
if not args.cat in df["cutflow"].keys():
    raise ValueError(f"Event category `{args.cat}` not found in the input file.")

# Dictionary of features to be used for the training
# The dictionary has two levels: the first level is common to all the samples, the second level is specific for a given sample.
# For each of these levels, the dictionary contains the name of the collection (e.g. `JetGood`) and the features to be used for the training (e.g. `pt`, `eta`, `phi`, `mass`, `btag`).
# For each feature, the dictionary contains the name of the feature in the coffea file (e.g. `provenance`) and the name of the feature in the parquet file (e.g. `prov`).

features = {
    "common": {
        # "bQuark": {
        #     "pt": "pt",
        #     "eta": "eta",
        #     "phi": "phi",
        #     # "mass" : "mass",
        #     "pdgId": "pdgId",
        #     "prov": "provenance",
        # },
        # "bQuarkHiggsMatched": {
        #     "pt": "pt",
        #     "eta": "eta",
        #     "phi": "phi",
        #     # "mass" : "mass",
        #     "pdgId": "pdgId",
        #     "prov": "provenance",
        # },
        "JetGood": {
            "pt": "pt",
            "eta": "eta",
            "phi": "phi",
            "mass": "mass",
            "btag": "btagPNetB",
            "btag_wp": "btagPNetB_5wp",
            # "ptPnetRegNeutrino": "ptPnetRegNeutrino",
        },
        "JetGoodHiggs": {
            "pt": "pt",
            "eta": "eta",
            "phi": "phi",
            "mass": "mass",
            "btag": "btagPNetB",
            "btag_wp": "btagPNetB_5wp",
            # "ptPnetRegNeutrino": "ptPnetRegNeutrino",
        },
        "JetGoodHiggsMatched": {
            "pt": "pt",
            "eta": "eta",
            "phi": "phi",
            "mass": "mass",
            "btag": "btagPNetB",
            "btag_wp": "btagPNetB_5wp",
            # "ptPnetRegNeutrino": "ptPnetRegNeutrino",
            "prov": "provenance",
            # "pdgId" : "pdgId",
            # "hadronFlavour" : "hadronFlavour"
        },
        "JetGoodMatched": {
            "pt": "pt",
            "eta": "eta",
            "phi": "phi",
            "mass": "mass",
            "btag": "btagPNetB",
            "btag_wp": "btagPNetB_5wp",
            # "ptPnetRegNeutrino": "ptPnetRegNeutrino",
            "prov": "provenance",
            # "pdgId" : "pdgId",
            # "hadronFlavour" : "hadronFlavour"
        },
        # TODO add the new variables
    },
    "by_sample": {},
}

norm_xsec = {
    "QCD-4Jets": (
        1.968e06
        + 1.000e05
        + 1.337e04
        + 3.191e03
        + 8.997e02
        + 3.695e02
        + 1.272e02
        + 2.514e01
    ),
    "GluGlutoHHto4B_kl-1p00": 0.02964,
}

kl_dict = {
    "kl-1p00": 1.00,
    "kl-0p00": 0.00,
    "kl-2p45": 2.45,
    "kl-5p00": 5.00,
    "kl-m2p00": -2.00,
    "kl-m1p00": -1.00,
    "kl-0p50": 0.50,
    "kl-1p50": 1.50,
    "kl-2p00": 2.00,
    "kl-3p00": 3.00,
    "kl-4p00": 4.00,
    "kl-3p50": 3.50,
}

sig_bkg_dict = {
    "QCD-4Jets": 0,
    "2022_postEE_EraE": 0,
    "GluGlutoHHto4B_kl-1p00": 1,
}

# Dictionary of features to pad with a default value
features_pad = {
    "common": {
        # "JetGood" : {
        #     "m" : 0
        # },
        # "JetGoodHiggs" : {
        #     "m" : 0
        # },
        # "JetGoodHiggsMatched" : {
        #     "m" : 0
        # },
    },
    "by_sample": {},
}

awkward_collections = list(features["common"].keys())
matched_collections_dict = {
    # "bQuark": "bQuarkHiggsMatched",
    "JetGoodHiggs": "JetGoodHiggsMatched",
    "JetGood": "JetGoodMatched",
}

samples = df["columns"].keys() if not args.sample else [args.sample]
print(df)
print("Full samples", df["columns"].keys())
print("Samples: ", samples)



for sample in samples:
    # Compose the features dictionary with common features and sample-specific features
    features_dict = features["common"].copy()
    if sample in features["by_sample"].keys():
        features_dict.update(features["by_sample"][sample])

    # Compose the dictionary of features to pad
    features_pad_dict = features_pad["common"].copy()
    if sample in features_pad["by_sample"].keys():
        features_pad_dict.update(features_pad["by_sample"][sample])

    # Create a default dictionary of dictionaries to store the arrays
    array_dict = {k: defaultdict(dict) for k in features_dict.keys()}
    datasets = df["columns"][sample].keys()

    # print("datasets", datasets)

    if args.kl:
        datasets = [dataset for dataset in datasets if args.kl in dataset]

    print("Datasets: ", datasets)

    if args.novars:
        dataset_lenght = [
            len(
                df["columns"][sample][dataset][args.cat][
                    f"{list(features_dict.keys())[0]}_N"
                ].value
            )
            for dataset in datasets
        ]
    else:
        dataset_lenght = [
            len(
                df["columns"][sample][dataset][args.cat]["nominal"][
                    f"{list(features_dict.keys())[0]}_N"
                ].value
            )
            for dataset in datasets
        ]

    print("dataset_lenght",  dataset_lenght)

    ## Normalize the genweights
    # Since the array `weight` is filled on the fly with the weight associated with the event, it does not take into account the overall scaling by the sum of genweights (`sum_genweights`).
    # In order to correct for this, we have to scale by hand the `weight` array dividing by the sum of genweights.
    for dataset in datasets:
        if args.novars:
            if "weight" in df["columns"][sample][dataset][args.cat].keys():
                weight = df["columns"][sample][dataset][args.cat]["weight"].value
                for x in norm_xsec.keys():
                    if x in dataset:
                        norm_factor = norm_xsec[x]
                        break
                    else:
                        norm_factor = 1.0

                if df["sum_genweights"].get(dataset, None):
                    weight_new = column_accumulator(
                        weight / df["sum_genweights"][dataset] / norm_factor
                    )
                else:
                    weight_new = column_accumulator(weight)
                df["columns"][sample][dataset][args.cat]["weight"] = weight_new
                print("weight_new",weight_new)
                plt.hist(weight_new.value, np.logspace(-9,-3,60))
                plt.yscale("log")
                plt.xscale("log")
                if not os.path.exists("weights_plots"):
                    os.makedirs("weights_plots")
                plt.savefig(f"./weights_plots/{dataset}")
            else:
                df["columns"][sample][dataset][args.cat]["weight"] = column_accumulator(
                    np.ones(dataset_lenght[list(datasets).index(dataset)])
                    / dataset_lenght[list(datasets).index(dataset)]
                )
        else:
            if "weight" in df["columns"][sample][dataset][args.cat]["nominal"].keys():
                weight = df["columns"][sample][dataset][args.cat]["nominal"]["weight"].value
                for x in norm_xsec.keys():
                    if x in dataset:
                        norm_factor = norm_xsec[x]
                        break
                    else:
                        norm_factor = 1.0

                if df["sum_genweights"].get(dataset, None):
                    weight_new = column_accumulator(
                        weight / df["sum_genweights"][dataset] / norm_factor
                    )
                else:
                    weight_new = column_accumulator(weight)
                df["columns"][sample][dataset][args.cat]["nominal"]["weight"] = weight_new
                print("weight_new",weight_new)
                plt.hist(weight_new.value, np.logspace(-9,-3,60))
                plt.yscale("log")
                plt.xscale("log")
                if not os.path.exists("weights_plots"):
                    os.makedirs("weights_plots")
                plt.savefig(f"./weights_plots/{dataset}")
            else:
                df["columns"][sample][dataset][args.cat]["weight"] = column_accumulator(
                    np.ones(dataset_lenght[list(datasets).index(dataset)])
                    / dataset_lenght[list(datasets).index(dataset)]
                )

    print("\nSamples colums:" , df["columns"].keys())
    print("Dataset columns: ", df["columns"][sample].keys())
    print("Category columns: ", df["columns"][sample][dataset].keys())
    ## Accumulate ntuples from different data-taking eras
    # In order to enlarge our training sample, we merge ntuples coming from different data-taking eras.
    if args.novars:
        cs = accumulate([df["columns"][sample][dataset][args.cat] for dataset in datasets])
    else:
        cs = accumulate([df["columns"][sample][dataset][args.cat]["nominal"] for dataset in datasets])
    print(cs["JetGoodHiggsMatched_provenance"])

    kl_list = [-999.0] * len(datasets)
    for i, dataset in enumerate(datasets):
        for kl in kl_dict.keys():
            if kl in dataset:
                kl_list[i] = kl_dict[kl]
                break
    #print("kl_list: ", kl_list)

    sb_list = [-999.0] * len(datasets)
    for i, dataset in enumerate(datasets):
        for sb in sig_bkg_dict.keys():
     #       print("keys sb", sig_bkg_dict.keys())
     #       print("\n dataset sb", dataset)
            if sb in dataset:
                sb_list[i] = sig_bkg_dict[sb]
                break
    #print("sb_list: ", sb_list)

    # print("dataset_lenght: ", dataset_lenght)
    kl_dataset = np.repeat(kl_list, dataset_lenght)
    # print("kl_dataset: ", kl_dataset)
    # print("kl_dataset shape: ", kl_dataset.shape)
    sb_dataset = np.repeat(sb_list, dataset_lenght)
    # print("sb_dataset: ", sb_dataset)
    # print("sb_dataset shape: ", sb_dataset.shape)

    ## Build the Momentum4D arrays for the jets, partons, leptons, met and higgs
    # In order to get the numpy array from the column_accumulator, we have to access the `value` attribute.
    for collection, variables in features_dict.items():
        for key_feature, key_coffea in variables.items():
            # if (collection == "JetGoodHiggsMatched") & (key_coffea == "provenance"):
            #     array_dict[collection][key_feature] = cs[f"bQuarkHiggsMatched_{key_coffea}"].value
            # else:
            array_dict[collection][key_feature] = cs[f"{collection}_{key_coffea}"].value
        print(array_dict["JetGoodHiggsMatched"]["prov"])

        # Add padded features to the array, according to the features dictionary
        if collection in features_pad_dict.keys():
            for key_feature, value in features_pad_dict[collection].items():
                array_dict[collection][key_feature] = value * np.ones_like(
                    cs[f"{collection}_pt"].value
                )

    # The awkward arrays are zipped together to form the Momentum4D arrays.
    # If the collection is not a Momentum4D array, it is zipped as it is,
    # otherwise the Momentum4D arrays are zipped together and unflattened depending on the number of objects in the collection.
    zipped_dict = {}
    for collection in array_dict.keys():
        if collection in awkward_collections:
            zipped_dict[collection] = ak.unflatten(
                ak.zip(array_dict[collection], with_name="Momentum4D"),
                cs[f"{collection}_N"].value,
            )
        else:
            zipped_dict[collection] = ak.zip(
                array_dict[collection], with_name="Momentum4D"
            )
        print(f"Collection: {collection}")
        print("Fields: ", zipped_dict[collection].fields)
        if "prov" in zipped_dict[collection].fields:
            print(zipped_dict[collection]["prov"])

    for collection in zipped_dict.keys():
        # Pad the matched collections with None if there is no matching
        if collection in matched_collections_dict.keys():
            matched_collection = matched_collections_dict[collection]
            masked_arrays = ak.mask(
                zipped_dict[matched_collection],
                zipped_dict[matched_collection].pt == -999,
                valid_when=False,
            )
            print("masked_arrays: ", masked_arrays)
            print("zipped_values:", zipped_dict[matched_collection].pt)
            # zipped_dict[matched_collection] = masked_arrays
            print(ak.count_nonzero(zipped_dict["JetGoodHiggsMatched"]["prov"]))
            # Add the matched flag and the provenance to the matched jets
            if collection == "JetGoodHiggs" or collection == "JetGood":
                print(
                    "Adding the matched flag and the provenance to the matched jets..."
                )
                is_matched = ~ak.is_none(masked_arrays, axis=1)
                print("is_matched: ", is_matched)
                print("zipped: ", zipped_dict[collection].pt, zipped_dict[collection])
                zipped_dict[collection] = ak.with_field(
                    zipped_dict[collection], is_matched, "matched"
                )
                zipped_dict[collection] = ak.with_field(
                    zipped_dict[collection],
                    ak.fill_none(masked_arrays.prov, -1),
                    "prov",
                    )
                ## Add the kl coefficient to the dataset
    # The kl coefficient is added to the dataset as a new feature.
    print(cs)
    try:
        zipped_dict["event"] = ak.zip(
                {"kl": kl_dataset, "sb": sb_dataset, "weight": cs["weight"].value, "random_pt_weights": cs["events_random_pt_weights"].value},
            with_name="Momentum4D",
        )
    except:
        zipped_dict["event"] = ak.zip(
            {"kl": kl_dataset, "sb": sb_dataset, "weight": cs["weight"].value},
            with_name="Momentum4D",
        )

    if "GluGlutoHHto4B" not in samples and args.reduce :
        print("sample loop", samples)
        for collection, _ in zipped_dict.items():
            print("\n collection", collection)
            print("zip", zipped_dict[collection])
            print("dataset", dataset)
            print("len zip", len(zipped_dict[collection]))

            # NOTE: for 2b data we are just shuffling the dataset up to the
            # index given by the length of the 2b QCD dataset
            # but this is still fine!
            zipped_dict[collection]= zipped_dict[collection][idx]
            print("new_zipped_1", len(zipped_dict[collection]))
            zipped_dict[collection]= zipped_dict[collection][: NUMBER_QCD_4B]
            print("new_zipped",zipped_dict[collection])
            print(len(zipped_dict["event"]["weight"]))
            print("len new_zipped", len(zipped_dict[collection]))



    if "GluGlutoHHto4B" not in samples and args.oversample:
        for collection, _ in zipped_dict.items():
            number = int(NUMBER_DATA_2B / len(zipped_dict[collection]))
            print("number", number)
            all_shuffled_data = []

            for i in range(number):
                idx = np.random.RandomState(seed= (42 + i) ).permutation(len(zipped_dict[collection]))
                shuffled_idx = ak.Array(zipped_dict[collection])[idx]
                all_shuffled_data.append(shuffled_idx)

            oversampled_data = ak.concatenate(all_shuffled_data, axis=0)
            print("len 1",len(oversampled_data))
            left_events= NUMBER_DATA_2B - (number*len(zipped_dict[collection]))
            print("left events", left_events)
            idx = np.random.RandomState().permutation(len(zipped_dict[collection]))
            last_events= zipped_dict[collection][idx][:left_events]
            zipped_dict[collection] =  ak.concatenate([oversampled_data, last_events], axis=0)
            print("len 2",len(zipped_dict[collection]))


    print("Check fields", zipped_dict[collection].fields)
    print("Zipped len", len(zipped_dict[collection]) )   
    print("Zipped ", zipped_dict )

    # The Momentum4D arrays are zipped together to form the final dictionary of arrays.
    print("Zipping the collections into a single dictionary...")
    df_out = ak.zip(zipped_dict, depth_limit=1)
    filename = os.path.join(main_dir, f"{sample}_{args.cat}{args.kl}.parquet")
    print(f"Saving the output dataset to file: {os.path.abspath(filename)}")
    ak.to_parquet(df_out, filename)
