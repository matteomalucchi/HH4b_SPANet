"""Script with configurations for each of the datasets that are to be tested for efficiency.

There are two dictionaries; one is a dictionary showing the actual datasets and the other is a list of true data, to which compare the predictions.
"""

spanet_dir = "/eos/user/t/tharte/Analysis_data/predictions/"
spanet_dir_matteo = (
    "/eos/user/m/mmalucch/spanet_infos/spanet_inputs/out_prediction_files/"
)
new_spanet_dir_matteo = (
    "/eos/user/m/mmalucch/spanet_infos/spanet_outputs/out_spanet_outputs/"
)

true_dir_thierry = "/eos/user/t/tharte/Analysis_data/spanet_samples/"
true_dir_matteo = (
    "/eos/user/m/mmalucch/spanet_infos/spanet_inputs/out_prediction_files/true_files/"
)
new_true_dir_matteo = "/eos/user/m/mmalucch/spanet_infos/spanet_inputs/"

spanet_dir_nestor = "/eos/user/n/nkontaxa/semester_project/spanet_outputs/"
true_dir_nestor = "/eos/user/m/mmalucch/spanet_infos/spanet_inputs/"


# uncomment the configurations that you want to use

run2_dataset_MC = "9_jets_vbf_ggf_all_Klambda"
# run2_dataset_MC = "9jets_all_Klambda_SeparateHiggsVBF_AddVBFJetPtOrder"

run2_dataset_DATA = ""

spanet_dict = {
    # --- Higgs pairing ---
    "5_jets_ptvary_btag_5wp_300e_3L1cuts_allklambda": {
        "file": f"/eos/user/t/tharte/Analysis_data/predictions/1_13_2_spanet_loose_MC_postEE_pt_vary_btagWP_s100_newLeptonVeto_3L1Cut_UpdateJetVetoMap_MC.h5",
        "true": "5_jets_pt_true_5wp_3L1cuts_allklambda",
        "label": "SPANet btag 5 WP - Flattened pt [0.3,1.7] - 3L1 triggers",
        "color": "firebrick",
        "higgs": True,
    },
    # allKlambda_HiggsPairing 100e
    f"{spanet_dir_nestor}vbf/predictions_allKlambda_HiggsPairing.h5": {
        "file": f"{spanet_dir_nestor}vbf/predictions_allKlambda_HiggsPairing.h5",
        "true": "true_allklambda_HiggsPairing",
        "label": "SPANet - ggF/VBF - HiggsPairing",
        "color": "orange",
        "higgs": True,
    },
    "hh4b_pairing_vbf_ggf_all_Klambda_HiggsPairing_2024": {
        "file": "/eos/user/m/mmalucch/spanet_infos/spanet_outputs/out_spanet_outputs/out_hh4b_pairing_vbf_ggf_all_Klambda_HiggsPairing_2024/out_seed_trainings_100/version_0/predict_ggF4kl_TotVBF_ggF4kl_TotVBF_NormWeights_AllKlambda_VBFggF_HIggsPairing_JetGoodProvHiggsPadded_test.h5",
        "true": "9jets_all_Klambda_HiggsPairing_2024",
        "label": "HiggsPairing - 2024 - ggF4kl_TotVBF",
        "color": "blue",
        "higgs": True,
        "vbf": False,
        "jet_coll_higgs": "Jet",
        "offset_jet_idx_higgs": 0,
        "resonances": "OLD_RESONANCES",
    },
    # --- VBF/ggF pairing ---
    "hh4b_pairing_vbf_ggf_pairing_allKalmbda": {
        "file": f"{new_spanet_dir_matteo}/out_hh4b_pairing_vbf_ggf_pairing_classification_allKlambda/out_seed_trainings_100/version_1/JetTotalSPANetPadded_kl_combined_test_vbf_all_Klambda_predicitons.h5",
        "true": "9_jets_vbf_ggf_all_Klambda",
        "label": "SPANet - baseline - pairing",
        "color": "blue",
        "vbf": True,
    },
    "hh4b_pairing_vbf_ggf_pairing_classification_allKalmbda": {
        "file": f"{new_spanet_dir_matteo}/out_hh4b_pairing_vbf_ggf_pairing_classification_allKlambda/out_seed_trainings_100/version_2/JetTotalSPANetPadded_kl_combined_EVENT_AllKlambda_classification_ptvarytraining_reverse_test.h5",
        "true": "9_jets_vbf_ggf_all_Klambda",
        "label": "SPANet - VBF/ggF - pairing+classification - 9 jets",
        "color": "dodgerblue",
        "vbf": True,
    },
    "hh4b_pairing_vbf_ggf_all_Klambda_VBFPairing_JetTotal_DNNVars_VBFNoKinCut_ClassLoss7_300e": {
        "file": f"{new_spanet_dir_matteo}/out_hh4b_pairing_vbf_ggf_all_Klambda_VBFPairing_JetTotal_DNNVars_VBFNoKinCut_ClassLoss7_300e/out_seed_trainings_100/version_0/predict_epoch78_FixMASK_AllKlambda_VBFggF_VBFPairingAfterHiggsPairing_DNNVars_vbfNoKinCutJetTotalSPANetPadded_test.h5",
        "true": "9jets_all_Klambda_VBFPairing_JetTotal_DNNVars_VBFNoKinCut",
        "label": "VBF pair+clas - JetTotal - DNN Vars - VBFNoKinCut Train - ClassLoss7 - 300e",
        "color": "dodgerblue",
        "vbf": True,
    },
    ##################################
    ## Separate JetHiggs and JetVBF ##
    ##################################
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
}


# The `klambda` parameter so far only determines, if there is different klambdas or not. The type if not `none` doesn't matter.
true_dict = {
    # --- ggF pairing ---
    "5_jets_pt_true_5wp_3L1cuts_allklambda": {
        "name": f"{true_dir_thierry}/1_13_2_loose_MC_postEE_pt_nominal_btagWP_newLeptonVeto_3L1Cut_UpdateJetVetoMap/output_JetGood_test.h5",
        "klambda": "postEE",
    },
    "9jets_all_Klambda_HiggsPairing_2024": {
        "name": "/eos/user/m/mmalucch/spanet_infos/spanet_inputs/vbf/out_ggf_vbf_spanet_input_AllKlambda_DetaMjjCentrality_VBFPairingAfterHiggsPairing_DNNVars_vbfregions_2024/ggF4kl_TotVBF_NormWeights_AllKlambda_VBFggF_HIggsPairing_JetGoodProvHiggsPadded_test.h5",
        "klambda": "postEE",
        "jet_coll_higgs": "Jet",
    },
    # --- VBF/ggF pairing ---
    "9_jets_vbf_ggf_all_Klambda": {
        "name": f"{new_true_dir_matteo}/vbf/vbf_all_Klambda/JetTotalSPANetPadded_kl_combined_test.h5",
        "klambda": "postEE",
        "vbf": True,
    },
    "true_allklambda_HiggsPairing": {
        "name": f"{true_dir_nestor}vbf/vbf_ggf_all_Klambda_HiggsPairing/AllKlambda_VBFggF_HiggsPairing_JetGood_test.h5",
        "klambda": "postEE",
        "vbf": True,
    },
    "9jets_all_Klambda_VBFPairing_JetTotal_DNNVars_VBFNoKinCut": {
        "name": f"{new_true_dir_matteo}/vbf/out_ggf_vbf_spanet_input_AllKlambda_DetaMjjCentrality_VBFPairingAfterHiggsPairing_DNNVars_vbfregions/FixMASK_AllKlambda_VBFggF_VBFPairingAfterHiggsPairing_DNNVars_vbfNoKinCutJetTotalSPANetPadded_test.h5",
        "klambda": "postEE",
    },
    "9jets_all_Klambda_SeparateHiggsVBF_AddVBFJetPtOrder": {
        "name": f"{new_true_dir_matteo}/vbf/vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjj_SeparateHiggsVBF_AddVBFJetPtOrder_Fix/AllKlambda_DetaMjj_SeparateHiggsVBF_AddVBFJetPtOrder_FixJetGoodProvHiggsPadded_JetGoodVBFMergedProvVBFPadded_test.h5",
        "klambda": "postEE",
        "jet_coll_higgs": "JetHiggs",
        "jet_coll_vbf": "JetVBF",
        "n_higgs_jets": 0,
        "resonances": "DEFAULT_RESONANCES",
    },
    "9jets_all_Klambda_VBFPairing_JetHiggsSeparate_DNNVars_VBFNoKinCut": {
        "name": f"{new_true_dir_matteo}/vbf/out_ggf_vbf_spanet_input_AllKlambda_DetaMjjCentrality_VBFPairingAfterHiggsPairing_DNNVars_vbfregions/FixMASK_AllKlambda_VBFggF_VBFPairingAfterHiggsPairing_DNNVars_vbfNoKinCut_JetGoodProvHiggsPaddedGlobal_JetGoodVBFMergedProvVBFPadded_JetGoodProvHiggsPadded_test.h5",
        "klambda": "postEE",
        "jet_coll_higgs": "JetHiggs",
        "jet_coll_vbf": "JetVBF",
        "n_higgs_jets": 0,
    },
}
