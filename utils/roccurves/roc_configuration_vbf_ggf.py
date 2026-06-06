"""Script with configurations for each of the datasets that are to be tested for efficiency.

There are two dictionaries; one is a dictionary showing the actual datasets and the other is a list of true data, to which compare the predictions.
"""

# uncomment the configurations that you want to use
new_spanet_dir_matteo = (
    "/eos/user/m/mmalucch/spanet_infos/spanet_outputs/out_spanet_outputs/"
)
new_true_dir_matteo = (
    "/eos/user/m/mmalucch/spanet_infos/spanet_inputs/"
)

spanet_dict = {
    # --- VBF/ggF pairing ---
    'hh4b_pairing_vbf_ggf_pairing_classification': {
        'file': f'{new_spanet_dir_matteo}/out_hh4b_pairing_vbf_ggf_pairing_classification/out_seed_trainings_100/version_2/predicitons.h5',
        'true': '9_jets_vbf_ggf_SM',
        'label': 'SPANet - VBF/ggF SM',
        'color': 'orange',
        'vbf': True,
    },
    'hh4b_pairing_vbf_ggf_pairing_classification_allKalmbda': {
        'file': f'{new_spanet_dir_matteo}/out_hh4b_pairing_vbf_ggf_pairing_classification_allKlambda/out_seed_trainings_100/version_2/JetTotalSPANetPadded_kl_combined_EVENT_AllKlambda_classification_ptvarytraining_reverse_test.h5',
        'true': '9_jets_vbf_ggf_all_Klambda',
        'label': 'SPANet - VBF/ggF',
        'color': 'blue',
        'vbf': True,
    },
    'hh4b_pairing_vbf_ggf_pairing_classification_allKalmbda_7jets_100e': {
        'file': f'{new_spanet_dir_matteo}/out_hh4b_pairing_vbf_ggf_pairing_classification_allKlambda_7jets/out_seed_trainings_100/version_1/predict_7jets_100e_JetTotalSPANetPadded_test.h5',
        'true': '7_jets_vbf_ggf_all_Klambda',
        'label': 'SPANet - VBF/ggF - 7 jets - 100 epochs',
        'color': 'dodgerblue',
        'vbf': True,
    },
    'hh4b_pairing_vbf_ggf_pairing_classification_allKalmbda_7jets_200e': {
        'file': f'{new_spanet_dir_matteo}/out_hh4b_pairing_vbf_ggf_pairing_classification_allKlambda_7jets/out_seed_trainings_100/version_0/predict_7jets_JetTotalSPANetPadded_test.h5',
        'true': '7_jets_vbf_ggf_all_Klambda',
        'label': 'SPANet - VBF/ggF - 7 jets - 200 epochs',
        'color': 'red',
        'vbf': True,
    },
}

true_dict = {
    # --- VBF/ggF pairing ---
    "9_jets_vbf_ggf_SM": {
        "name": f"{new_true_dir_matteo}/vbf/vbf_SM/JetTotalSPANetPtFlattenPadded_pad9999_test.h5",
        "klambda": "postEE",
        "vbf": True,
    },
    "9_jets_vbf_ggf_all_Klambda": {
        "name": f"{new_true_dir_matteo}/vbf/vbf_all_Klambda/JetTotalSPANetPadded_kl_combined_test.h5",
        "klambda": "postEE",
        "vbf": True,
    },
    "7_jets_vbf_ggf_all_Klambda": {
        "name": f"{new_true_dir_matteo}/vbf/vbf_all_Klambda/7jets_JetTotalSPANetPadded_test.h5",
        "klambda": "postEE",
        "vbf": True,
    },
}

roc_dict={}

