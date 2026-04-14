"""Script with configurations for ROC studies.

There are three dictionaries:
- spanet_dict: prediction files and plotting metadata
- true_dict: matching truth files
- roc_dict: optional externally stored ROC arrays
"""

spanet_dict = {}
true_dict = {}
roc_dict = {}

# =============================================================================
# (nkontaxa) MODIFICATIONS below
# =============================================================================

spanet_dir_nestor = "/eos/user/n/nkontaxa/semester_project/spanet_outputs/"
true_dir_nestor = "/eos/user/m/mmalucch/spanet_infos/spanet_inputs/"

spanet_dict.update({
    # AllKlambda 7 jets
    "predictions_allKlambda_7jets": {
        "file": f"{spanet_dir_nestor}vbf/predictions_allKlambda_7jets_JetTotalSPANETPadded.h5",
        "true": "true_7jets_allklambda",
        "label": "SPANet 7j all_Klambda 100e",
        "color": "royalblue",
        "vbf": True,
    },

    # 500 epochs all_Klambda 9 jets
    "predictions_allKlambda_500epochs": {
        "file": f"{spanet_dir_nestor}vbf/predictions_allKlambda_500epochs.h5",
        "true": "true_9jets_allklambda",
        "label": "SPANet 9j all_Klambda 500e",
        "color": "cyan",
        "vbf": True,
    },

    # AllKlambda 9 jets, 100 epochs
    "predictions_allKlambda_100epochs": {
        "file": f"{spanet_dir_nestor}vbf/predictions_allKlambda.h5",
        "true": "true_9jets_allklambda",
        "label": "SPANet 9 jets all_Klambda 100e",
        "color": "red",
        "vbf": True,
    },

    # Optional entries below: uncomment when needed

    # "predictions_allKlambda_DetaMjj_novars_NormGenWeights": {
    #     "file": f"{spanet_dir_nestor}vbf/predictions_allKlambda_DetaMjj_novars_NormGenWeights.h5",
    #     "true": "true_detamjj_ngw",
    #     "label": "SPANet DetaMjj NGW noextravars (nkontaxa)",
    #     "color": "black",
    #     "vbf": True,
    # },

    # "predictions_allKlambda_DetaMjj_novars_NonNormGenWeights": {
    #     "file": f"{spanet_dir_nestor}vbf/predictions_allKlambda_DetaMjj_novars_Non-NormGenWeights.h5",
    #     "true": "true_detamjj_nngw",
    #     "label": "SPANet DetaMjj NNGW noextravars (nkontaxa)",
    #     "color": "green",
    #     "vbf": True,
    # },

    # "predictions_allKlambda_DetaMjj_extravars_NonNormGenWeights": {
    #     "file": f"{spanet_dir_nestor}vbf/predictions_allKlambda_DetaMjj_extravars_Non-NormGenWeights.h5",
    #     "true": "true_detamjj_nngw",
    #     "label": "SPANet DetaMjj NNGW extravars (nkontaxa)",
    #     "color": "yellow",
    #     "vbf": True,
    # },

    # "predictions_ptFlattenMatchedHiggs_DetaMjj": {
    #     "file": f"{spanet_dir_nestor}vbf/predictions_vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjj.h5",
    #     "true": "true_ptFlattenMatchedHiggs_detamjj",
    #     "label": "SPANet ptFlattenedMatchedHiggs DetaMjj (nkontaxa)",
    #     "color": "lightblue",
    #     "vbf": True,
    # },

    # "predictions_ptFlattenMatchedHiggs_DetaMjj_AddVBFJetOrder": {
    #     "file": f"{spanet_dir_nestor}vbf/predictions_vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjj_AddVBFJetOrder.h5",
    #     "true": "true_ptFlattenMatchedHiggs_addVBFJetOrder",
    #     "label": "SPANet ptFlattenedMatchedHiggs DetaMjj AddVBFJetOrder (nkontaxa)",
    #     "color": "pink",
    #     "vbf": True,
    # },

    # "predictions_ptFlattenMatchedHiggs_DetaMjj_SeparateHiggsVBF_1": {
    #     "file": f"{spanet_dir_nestor}vbf/predictions_vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjj_SeparateHiggsVBF_MergedCollections_1.h5",
    #     "true": "true_ptFlattenMatchedHiggs_separateHiggsVBF",
    #     "label": "SPANet ptFlattenedMatchedHiggs DetaMjj SeparateHiggsVBF (nkontaxa)",
    #     "color": "brown",
    #     "vbf": True,
    # },

    # "predictions_ptFlattenMatchedHiggs_DetaMjj_SeparateHiggsVBF_2": {
    #     "file": f"{spanet_dir_nestor}vbf/predictions_vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjj_SeparateHiggsVBF_MergedCollections_2.h5",
    #     "true": "true_ptFlattenMatchedHiggs_separateHiggsVBF",
    #     "label": "SPANet ptFlattenedMatchedHiggs DetaMjj SeparateHiggsVBF OnlyHiggsFlattening (nkontaxa)",
    #     "color": "lightgrey",
    #     "vbf": True,
    # },
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
        "name": f"{true_dir_nestor}vbf/vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjj/AllKlambda_DetaMjjJetTotalSPANetPtFlattenHiggsMatchedPadded_test.h5",
        "klambda": "postEE",
        "vbf": True,
    },

    "true_ptFlattenMatchedHiggs_addVBFJetOrder": {
        "name": f"{true_dir_nestor}vbf/vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjj_AddVBFJetPtOrder/AllKlambda_DetaMjj_AddVBFJetPtOrder_JetTotalSPANetPtFlattenPadded_test.h5",
        "klambda": "postEE",
        "vbf": True,
    },

    "true_ptFlattenMatchedHiggs_separateHiggsVBF": {
        "name": f"{true_dir_nestor}vbf/vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjj_SeparateHiggsVBF_MergedCollections/AllKlambda_DetaMjj_SeparateHiggsVBFMergeColl_JetTotalSPANetSeparateProvHiggsVBFPadded_test.h5",
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