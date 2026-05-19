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

    #100 epochs all_Klambda 9 jets extreme_classlossweights 
    f"vbf/predictions_allKlambda_extreme_classlossweights_7.h5": {
        "file": f"{spanet_dir_nestor}vbf/predictions_allKlambda_extreme_classlossweights_7.h5",
       "true": "true_9jets_allklambda",
        "label": "9j all_Klambda ECLW (7.0)",
        "color": "yellow",
        "vbf": True,
    },

    # allKlambda_DetaMjj_NNGW_extravars_extreme_classlossweights
    #"predictions_allKlambda_DetaMjj_extravars_NNGW_extreme_classlossweights": {
    #    "file": f"{spanet_dir_nestor}vbf/predictions_allKlambda_DetaMjj_extravars_Non-NormGenWeights_extreme_classlossweights.h5",
    #    "true": "true_detamjj_nngw",
    #    "label": "SPANet DetaMjj NNGW extravars extreme classlossweights",
    #    "color": "brown",
    #    "vbf": True,
    #},

    # allKlambda_DetaMjj_NGW_noextravars
    # "predictions_allKlambda_DetaMjj_novars_NGW": {
    #     "file": f"{spanet_dir_nestor}vbf/predictions_allKlambda_DetaMjj_novars_NormGenWeights.h5",
    #     "true": "true_detamjj_ngw",
    #     "label": "DetaMjj NGW noextravars",
    #     "color": "black",
    #     "vbf": True,
    # },

    # allKlambda_DetaMjj_NNGW_extravars
    #"predictions_allKlambda_DetaMjj_extravars_NNGW_200e": {
    #    "file": f"{spanet_dir_nestor}vbf/predictions_allKlambda_DetaMjj_extravars_Non-NormGenWeights.h5",
    #    "true": "true_detamjj_nngw",
    #    "label": "DetaMjj NNGW extravars 200e",
    #    "color": "yellow",
    #    "vbf": True,
    #},

    #allKlambda_VBFPairing 100e
    "predictions_allKlambda_vbfpairing_remake.h5": {
        "file": f"{spanet_dir_nestor}vbf/predictions_allKlambda_vbfpairing_remake.h5",
        "true": "true_allklambda_VBFPairing",
        "label": "allKlambda VBFPairing 100e remake",
        "color": "purple",
        "vbf": True,
    },

    #allKlambda_VBFPairing 100e extravars
    "predictions_allKlambda_vbfpairing_extravars.h5": {
        "file": f"{spanet_dir_nestor}vbf/predictions_allKlambda_vbfpairing_extravars.h5",
        "true": "true_allklambda_VBFPairing",
        "label": "allKlambda VBFPairing 100e extravars",
        "color": "darkblue",
        "vbf": True,
    },

    # allKlambda_DetaMjj_NGW_extravars 150e 
     "predictions_allKlambda_DetaMjj_NGW_extravars_150e": {
         "file": f"{spanet_dir_nestor}vbf/predictions_allKlambda_DetaMjj_NGW_extravars_150e.h5",
         "true": "true_detamjj_ngw",
         "label": "DetaMjj NGW extravars 150e",
         "color": "darkgreen",
         "vbf": True,
     },

    #vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjjCentrality 150e ECLW=2
    "predictions_vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjjCentrality_extravars_150e_ECLW_2.h5": {
        "file": f"{spanet_dir_nestor}vbf/predictions_vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjjCentrality_extravars_150e_ECLW_2.h5",
        "true": "true_allklambda_DetaMjjCentrality",
        "label": "ptFlattenMatchedHiggs DetaMjj Centrality 150e ECLW = 2.0",
        "color": "brown",
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