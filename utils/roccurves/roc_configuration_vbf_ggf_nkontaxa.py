"""Script with configurations for ROC studies.

There are three dictionaries:
- spanet_dict: prediction files and plotting metadata
- true_dict: matching truth files
- roc_dict: optional externally stored ROC arrays
"""

spanet_dict = {}
true_dict = {}
roc_dict = {}


spanet_dir_nestor = "/eos/user/n/nkontaxa/semester_project/spanet_outputs/"
true_dir_nestor = "/eos/user/m/mmalucch/spanet_infos/spanet_inputs/"

spanet_dict.update({
    # AllKlambda 7 jets
    # "predictions_allKlambda_7jets": {
    #     "file": f"{spanet_dir_nestor}vbf/predictions_allKlambda_7jets_JetTotalSPANETPadded.h5",
    #     "true": "true_7jets_allklambda",
    #     "label": "SPANet 7j all_Klambda",
    #     "color": "royalblue",
    #     "vbf": True,
    # },

    # 500 epochs all_Klambda 9 jets
    # "predictions_allKlambda_500epochs": {
    #     "file": f"{spanet_dir_nestor}vbf/predictions_allKlambda_500epochs.h5",
    #     "true": "true_9jets_allklambda",
    #     "label": "SPANet 9j all_Klambda 500e",
    #     "color": "blue",
    #     "vbf": True,
    # },

    # 200 epochs all_Klambda 9 jets
    # "predictions_allKlambda_200epochs": {
    #     "file": f"{spanet_dir_nestor}vbf/predictions_allKlambda_200epochs.h5",
    #     "true": "true_9jets_allklambda",
    #     "label": "SPANet 9j all_Klambda 200e",
    #     "color": "magenta",
    #     "vbf": True,
    # },

    # allKlambda_DetaMjj_NNGW_extravars_extreme_classlossweights
    #"predictions_allKlambda_DetaMjj_extravars_NNGW_extreme_classlossweights": {
    #    "file": f"{spanet_dir_nestor}vbf/predictions_allKlambda_DetaMjj_extravars_Non-NormGenWeights_extreme_classlossweights.h5",
    #    "true": "true_detamjj_nngw",
    #    "label": "SPANet DetaMjj NNGW extravars extreme classlossweights",
    #    "color": "brown",
    #    "vbf": True,
    #},

    #allKlambda_VBFPairing 100e
    #"predictions_allKlambda_vbfpairing.h5": {
    #    "file": f"{spanet_dir_nestor}vbf/predictions_allKlambda_vbfpairing.h5",
    #    "true": "true_allklambda_VBFPairing",
    #    "label": "allKlambda VBFPairing 100e",
    #    "color": "purple",
    #    "vbf": True,
    #},

    # 100 epochs all_Klambda 9 jets extreme_classlossweights
    #"predictions_allKlambda_extreme_classlossweights": {
    #    "file": f"{spanet_dir_nestor}vbf/predictions_allKlambda_extreme_classlossweights.h5",
    #    "true": "true_9jets_allklambda",
    #    "label": "SPANet 9j all_Klambda ExtremeClassLossWeights",
    #    "color": "darkgreen",
    #    "vbf": True,
    #},

    # allKlambda_DetaMjj_NGW_noextravars
    # "predictions_allKlambda_DetaMjj_novars_NGW": {
    #     "file": f"{spanet_dir_nestor}vbf/predictions_allKlambda_DetaMjj_novars_NormGenWeights.h5",
    #     "true": "true_detamjj_ngw",
    #     "label": "SPANet DetaMjj NGW noextravars (nkontaxa)",
    #     "color": "black",
    #     "vbf": True,
    # },

    # allKlambda_DetaMjj_NNGW_noextravars
    # "predictions_allKlambda_DetaMjj_novars_NNGW": {
    #     "file": f"{spanet_dir_nestor}vbf/predictions_allKlambda_DetaMjj_novars_Non-NormGenWeights.h5",
    #     "true": "true_detamjj_nngw",
    #     "label": "SPANet DetaMjj NNGW noextravars (nkontaxa)",
    #     "color": "green",
    #     "vbf": True,
    # },

    # allKlambda_DetaMjj_NNGW_extravars
    #"predictions_allKlambda_DetaMjj_extravars_NNGW_200e": {
    #    "file": f"{spanet_dir_nestor}vbf/predictions_allKlambda_DetaMjj_extravars_Non-NormGenWeights.h5",
    #    "true": "true_detamjj_nngw",
    #    "label": "SPANet DetaMjj NNGW extravars 200e",
    #    "color": "yellow",
    #    "vbf": True,
    #},

#100 epochs all_Klambda 9 jets extreme_classlossweights remake
    f"vbf/predictions_allKlambda_extreme_classlossweights_5.h5": {
        "file": f"{spanet_dir_nestor}vbf/predictions_allKlambda_extreme_classlossweights_5.h5",
       "true": "true_9jets_allklambda",
        "label": "9j all_Klambda ECLW (5.0) remake",
        "color": "blue",
        "vbf": True,
    },

#100 epochs all_Klambda 9 jets extreme_classlossweights remake
    f"vbf/predictions_allKlambda_extreme_classlossweights_3.h5": {
        "file": f"{spanet_dir_nestor}vbf/predictions_allKlambda_extreme_classlossweights_3.h5",
       "true": "true_9jets_allklambda",
        "label": "9j all_Klambda ECLW (3.0)",
        "color": "darkblue",
        "vbf": True,
    },

#100 epochs all_Klambda 9 jets extreme_classlossweights remake
    f"vbf/predictions_allKlambda_extreme_classlossweights_7.h5": {
        "file": f"{spanet_dir_nestor}vbf/predictions_allKlambda_extreme_classlossweights_7.h5",
       "true": "true_9jets_allklambda",
        "label": "9j all_Klambda ECLW (7.0)",
        "color": "darkgreen",
        "vbf": True,
    },

#100 epochs all_Klambda 9 jets extreme_classlossweights
    "predictions_allKlambda_extreme_classlossweights_10.h5": {
       "file": f"{spanet_dir_nestor}vbf/predictions_allKlambda_extreme_classlossweights_10.h5",
       "true": "true_9jets_allklambda",
        "label": "9j all_Klambda ECLW (10.0)",
        "color": "purple",
        "vbf": True,
    },

    # AllKlambda 9 jets
    "predictions_allKlambda_100e": {
        "file": f"{spanet_dir_nestor}vbf/predictions_allKlambda.h5",
        "true": "true_9jets_allklambda",
        "label": "9j all_Klambda 100e",
        "color": "red",
        "vbf": True,
    },
})

true_dict.update({
    "true_7jets_allklambda": {
        "name": f"{true_dir_nestor}vbf/vbf_all_Klambda/7jets_JetTotalSPANetPadded_test.h5",
        "klambda": "postEE",
        "vbf": True,
    },

    "true_9jets_allklambda": {
        "name": f"{true_dir_nestor}vbf/vbf_all_Klambda/JetTotalSPANetPadded_kl_combined_EVENT_test.h5",
        "klambda": "postEE",
        "vbf": True,
    },

    "true_detamjj_ngw": {
        "name": f"{true_dir_nestor}vbf/vbf_all_Klambda_DetaMjj/SaveMjjDeta_NormGenWeights_JetTotalSPANetPadded_test.h5",
        "klambda": "postEE",
        "vbf": True,
    },

    "true_detamjj_nngw": {
        "name": f"{true_dir_nestor}vbf/vbf_all_Klambda_DetaMjj/SaveMjjDeta_JetTotalSPANetPadded_test.h5",
        "klambda": "postEE",
        "vbf": True,
    },

    "true_ptFlattenMatchedHiggs_detamjj": {
        "name": f"{true_dir_nestor}vbf/vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjj/JetTotalSPANetPadded_kl_combined_EVENT_test.h5",
        "klambda": "postEE",
        "vbf": True,
    },

    "true_ptFlattenMatchedHiggs_addVBFJetOrder": {
        "name": f"{true_dir_nestor}vbf/vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjj_AddVBFJetPtOrder/AllKlambda_DetaMjj_AddVBFJetPtOrder_JetTotalSPANetPadded_test.h5",
        "klambda": "postEE",
        "vbf": True,
    },

    "true_ptFlattenMatchedHiggs_separateHiggsVBF": {
        "name": f"{true_dir_nestor}vbf/vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjj_SeparateHiggsVBF_MergedCollections_FixNoneJets/AllKlambda_DetaMjj_SeparateHiggsVBFMergeColl_JetTotalSPANetSeparateProvHiggsVBFPadded_test.h5",
        "klambda": "postEE",
        "vbf": True,
    },

    "true_allklambda_HiggsPairing": {
        "name": f"{true_dir_nestor}vbf/vbf_ggf_all_Klambda_HiggsPairing/AllKlambda_VBFggF_HiggsPairing_JetGood_test.h5",
        "klambda": "postEE",
        "vbf": True,
    },

    "true_allklambda_VBFPairing": {
        "name": f"{true_dir_nestor}vbf/vbf_ggf_all_Klambda_DetaMjjCentrality_VBFPairingAfterHiggsPairing/AllKlambda_VBFggF_VBFPairingAfterHiggsPairing_JetGoodVBFMergedProvVBFPadded_test.h5",
        "klambda": "postEE",
        "vbf": True,
    },

    "true_allklambda_DetaMjjCentrality": {
        "name": f"{true_dir_nestor}vbf/vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjjCentrality_AddVBFJetPtOrder/AllKlambda_DetaMjjCentrality_AddVBFJetPtOrder_JetTotalSPANetPadded_test.h5",
        "klambda": "postEE",
        "vbf": True,
    },
})

# Optional external ROC arrays
roc_dict.update({
    # "reference_model_name": {
    #     "file": "/full/path/to/reference_roc_arrays.npz",
    #     "label": "Reference ROC",
    #     "color": "black",
    # },
})

# =============================================================================
# END MODIFICATIONS SECTION
# =============================================================================

roc_dict={}