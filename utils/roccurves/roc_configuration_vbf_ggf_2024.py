"""Script with configurations for each of the datasets that are to be tested for efficiency.

There are two dictionaries; one is a dictionary showing the actual datasets and the other is a list of true data, to which compare the predictions.
"""

# uncomment the configurations that you want to use
new_spanet_dir_matteo = (
    "/eos/user/m/mmalucch/spanet_infos/spanet_outputs/out_spanet_outputs/"
)
new_true_dir_matteo = "/eos/user/m/mmalucch/spanet_infos/spanet_inputs/"

spanet_dir_nestor = "/eos/user/n/nkontaxa/semester_project/spanet_outputs/"
true_dir_nestor = "/eos/user/m/mmalucch/spanet_infos/spanet_inputs/"


spanet_dict = {
    # --- VBF/ggF pairing ---
    "hh4b_pairing_vbf_ggf_all_Klambda_VBFPairing_JetTotal_DNNVars_VBFNoKinCut_ClassLoss7": {
        "file": f"{new_spanet_dir_matteo}/out_hh4b_pairing_vbf_ggf_all_Klambda_VBFPairing_JetTotal_DNNVars_VBFNoKinCut_ClassLoss7/out_seed_trainings_100/version_0/predict_FixMASK_AllKlambda_VBFggF_VBFPairingAfterHiggsPairing_DNNVars_vbfNoKinCutJetTotalSPANetPadded_ClassLoss7_test.h5",
        "true": "9jets_all_Klambda_VBFPairing_JetTotal_DNNVars_VBFNoKinCut",
        "label": "VBF pair+clas - JetTotal - DNN Vars - VBFNoKinCut Train - ClassLoss7",
        "color": "brown",
        "vbf": True,
    },
    # "hh4b_pairing_vbf_ggf_all_Klambda_VBFPairing_JetTotal_DNNVars_VBFNoKinCut_ClassLoss7_FW_mom_0_11": {
    #     "file": f"{new_spanet_dir_matteo}/out_hh4b_pairing_vbf_ggf_all_Klambda_VBFPairing_JetTotal_DNNVars_VBFNoKinCut_ClassLoss7_FW_mom_0_11/out_seed_trainings_100/version_0/predict_AllKlambda_DetaMjj_VBFPairingAfterHiggsPairing_AddVBFJetPtOrder_FW_momenta_vbfNoKinCut_JetTotalSPANetPadded_test.h5",
    #     "true": "9jets_all_Klambda_VBFPairing_JetTotal_DNNVars_VBFNoKinCut_FW_mom_0_11",
    #     "label": "VBF pair+clas - JetTotal - DNN Vars - VBFNoKinCut Train - ClassLoss7 - FW - mom - 0 - 11",
    #     "color": "firebrick",
    #     "vbf": True,
    # },
    "hh4b_pairing_vbf_ggf_all_Klambda_VBFPairing_JetHiggsGlobal_DNNVars_VBFNoKinCut_ClassLoss7": {
        "file": f"{new_spanet_dir_matteo}/out_hh4b_pairing_vbf_ggf_all_Klambda_VBFPairing_JetHiggsGlobal_DNNVars_VBFNoKinCut_ClassLoss7/out_seed_trainings_100/version_0/predict_FixMASK_AllKlambda_VBFggF_VBFPairingAfterHiggsPairing_DNNVars_vbfNoKinCut_JetGoodProvHiggsPaddedGlobal_JetGoodVBFMergedProvVBFPadded_JetGoodProvHiggsPadded_test.h5",
        "true": "9jets_all_Klambda_VBFPairing_JetHiggsGlobal_DNNVars_VBFNoKinCut",
        "label": "VBF pair+clas - JetHiggsGlobal - DNN Vars - VBFNoKinCut Train - ClassLoss7",
        "color": "teal",
        "vbf": True,
        "jet_coll_higgs": "JetHiggs",
        "jet_coll_vbf": "JetVBF",
        "n_higgs_jets": 0,
        "offset_jet_idx_higgs": 0,
        "offset_jet_idx_vbf": -4,
        "resonances": "DEFAULT_RESONANCES",
    },
    "hh4b_pairing_vbf_ggf_all_Klambda_VBFPairing_JetHiggsSeparate_DNNVars_VBFNoKinCut_ClassLoss7": {
        "file": f"{new_spanet_dir_matteo}/out_hh4b_pairing_vbf_ggf_all_Klambda_VBFPairing_JetHiggsSeparate_DNNVars_VBFNoKinCut_ClassLoss7/out_seed_trainings_100/version_0/predict_FixMASK_AllKlambda_VBFggF_VBFPairingAfterHiggsPairing_DNNVars_vbfNoKinCut_JetGoodProvHiggsPaddedGlobal_JetGoodVBFMergedProvVBFPadded_JetGoodProvHiggsPadded_test.h5",
        "true": "9jets_all_Klambda_VBFPairing_JetHiggsSeparate_DNNVars_VBFNoKinCut",
        "label": "VBF pair+clas - JetHiggsSeparate - DNN Vars - VBFNoKinCut Train - ClassLoss7",
        "color": "darkorange",
        "vbf": True,
        "jet_coll_higgs": "JetHiggs",
        "jet_coll_vbf": "JetVBF",
        "n_higgs_jets": 0,
        "offset_jet_idx_higgs": 0,
        "offset_jet_idx_vbf": -4,
        "resonances": "DEFAULT_RESONANCES",
    },
    "hh4b_pairing_vbf_ggf_all_Klambda_VBFPairingAfterHiggsPairingWithZSamples_JetHiggsSeparate_DNNVars_VBFNoKinCut_ClassLoss7_2024_NoBtag": {
        "file": "/eos/user/m/mmalucch/php-plots/SPANet_studies/training_outputs/2026-10-06_out_hh4b_pairing_vbf_ggf_all_Klambda_VBFPairingAfterHiggsPairingWithZSamples_JetHiggsSeparate_DNNVars_VBFNoKinCut_ClassLoss7_2024_NoBtag/out_seed_trainings_100/version_0/predict_VBFPairingAfterHiggsPairingWithZSamples_DNNVars_vbfregions_2024SPANetHiggsTraining_parking_presel_JetGoodVBFMergedProvVBFPadded_JetGoodProvHiggsPadded_test.h5",
        "true": "9jets_all_Klambda_VBFPairingAfterHiggsPairingWithZSamples_JetHiggsSeparate_DNNVars_VBFNoKinCut_2024_NoBtag",
        "label": "VBFPairingAfterHiggsPairingWithZSamples - JetHiggsSeparate - DNN Vars - VBFNoKinCut "
        "Train - ClassLoss7 - 2024 - NoBtag",
        "color": "green",
        "higgs": False,
        "vbf": True,
        "jet_coll_higgs": "JetVBF",
        "n_higgs_jets": 0,
        "offset_jet_idx_vbf": -4,
        "resonances": "OLD_RESONANCES",
    },
}

true_dict = {
    # --- VBF/ggF pairing ---
    "9_jets_vbf_ggf_all_Klambda": {
        "name": f"{new_true_dir_matteo}/vbf/vbf_all_Klambda/JetTotalSPANetPadded_kl_combined_test.h5",
        "klambda": "postEE",
        "vbf": True,
    },
    "9jets_all_Klambda_VBFPairing_JetTotal_DNNVars_VBFNoKinCut": {
        "name": f"{new_true_dir_matteo}/vbf/out_ggf_vbf_spanet_input_AllKlambda_DetaMjjCentrality_VBFPairingAfterHiggsPairing_DNNVars_vbfregions/FixMASK_AllKlambda_VBFggF_VBFPairingAfterHiggsPairing_DNNVars_vbfNoKinCutJetTotalSPANetPadded_test.h5",
        "klambda": "postEE",
    },
    "9jets_all_Klambda_VBFPairing_JetTotal_DNNVars_VBFNoKinCut_FW_mom_0_11": {
        "name": f"{new_true_dir_matteo}/vbf/out_ggf_vbf_spanet_input_AllKlambda_DetaMjjCentrality_VBFPairingAfterHiggsPairing_DNNVars_FW_momenta_vbf_regions/AllKlambda_DetaMjj_VBFPairingAfterHiggsPairing_AddVBFJetPtOrder_FW_momenta_vbfNoKinCut_JetTotalSPANetPadded_test.h5",
        "klambda": "postEE",
    },
    "9jets_all_Klambda_VBFPairing_JetHiggsGlobal_DNNVars_VBFNoKinCut": {
        "name": f"{new_true_dir_matteo}/vbf/out_ggf_vbf_spanet_input_AllKlambda_DetaMjjCentrality_VBFPairingAfterHiggsPairing_DNNVars_vbfregions/FixMASK_AllKlambda_VBFggF_VBFPairingAfterHiggsPairing_DNNVars_vbfNoKinCut_JetGoodProvHiggsPaddedGlobal_JetGoodVBFMergedProvVBFPadded_JetGoodProvHiggsPadded_test.h5",
        "klambda": "postEE",
        "jet_coll_higgs": "JetHiggs",
        "jet_coll_vbf": "JetVBF",
        "n_higgs_jets": 0,
    },
    "9jets_all_Klambda_VBFPairing_JetHiggsSeparate_DNNVars_VBFNoKinCut": {
        "name": f"{new_true_dir_matteo}/vbf/out_ggf_vbf_spanet_input_AllKlambda_DetaMjjCentrality_VBFPairingAfterHiggsPairing_DNNVars_vbfregions/FixMASK_AllKlambda_VBFggF_VBFPairingAfterHiggsPairing_DNNVars_vbfNoKinCut_JetGoodProvHiggsPaddedGlobal_JetGoodVBFMergedProvVBFPadded_JetGoodProvHiggsPadded_test.h5",
        "klambda": "postEE",
        "jet_coll_higgs": "JetHiggs",
        "jet_coll_vbf": "JetVBF",
        "n_higgs_jets": 0,
    },
    "9jets_all_Klambda_VBFPairingAfterHiggsPairingWithZSamples_JetHiggsSeparate_DNNVars_VBFNoKinCut_2024_NoBtag": {
        "name": "/eos/user/m/mmalucch/spanet_infos/spanet_inputs/vbf/11_05_02_out_ggf_vbf_spanet_input_AllKlambda_DetaMjjCentrality_VBFPairingAfterHiggsPairingWithZSamples_DNNVars_vbfregions_2024SPANetHiggsTraining_parking_presel/VBFPairingAfterHiggsPairingWithZSamples_DNNVars_vbfregions_2024SPANetHiggsTraining_parking_presel_JetGoodVBFMergedProvVBFPadded_JetGoodProvHiggsPadded_test.h5",
        "klambda": "postEE",
        "jet_coll_higgs": "JetVBF",
        "n_higgs_jets": 0,
        "higgs": False,
        "vbf": True,
        "resonances": "OLD_RESONANCES",
    },
}

roc_dict = {}
