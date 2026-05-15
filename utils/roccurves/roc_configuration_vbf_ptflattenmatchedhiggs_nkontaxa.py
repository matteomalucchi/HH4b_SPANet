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
    # ptFlattenedMatchedHiggs_allKlambda_DetaMjj_SeparateHiggsVBF_MergedCollections_HiggsFlatten 100e
    ##"predictions_ptFlattenMatchedHiggs_DetaMjj_SeparateHiggsVBF_HiggsFlatten_100e": {
    ##    "file": f"{spanet_dir_nestor}vbf/predictions_vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjj_SeparateHiggsVBF_MergedCollections_HiggsFlatten_100e.h5",
    ##    "true": "true_ptFlattenMatchedHiggs_separateHiggsVBF",
    ##    "label": "SPANet ptFlattenedMatchedHiggs DetaMjj SeparateHiggsVBF HiggsFlatten",
    ##    "color": "brown",
    ##    "vbf": True,
    ##},

    # ptFlattenedMatchedHiggs_allKlambda_DetaMjj_SeparateHiggsVBF_MergedCollections_VBFHiggsFlatten 100e
    "predictions_ptFlattenMatchedHiggs_DetaMjj_SeparateHiggsVBF_VBFHiggsFlatten_100e": {
        "file": f"{spanet_dir_nestor}vbf/predictions_vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjj_SeparateHiggsVBF_MergedCollections_FixNoneJets_vbfhiggsFlatten_100e.h5",
        "true": "true_ptFlattenMatchedHiggs_separateHiggsVBF",
        "label": "ptFlattenedMatchedHiggs DetaMjj SeparateHiggsVBF VBFHiggsFlatten",
        "color": "darkgrey",
        "vbf": True,
    },

    # ptFlattenedMatchedHiggs_allKlambda_DetaMjj_SeparateHiggsVBF_MergedCollections_HiggsVBFFlatten 100e ECL = 0.5
    "predictions_ptFlattenMatchedHiggs_DetaMjj_SeparateHiggsVBF_HiggsVBFFlatten_CLW_0_5.h5": {
        "file": f"{spanet_dir_nestor}vbf/predictions_vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjj_SeparateHiggsVBF_HiggsVBFFLatten_CLW_0_5.h5",
        "true": "true_ptFlattenMatchedHiggs_separateHiggsVBF",
        "label": "ptFlattenedMatchedHiggs DetaMjj SeparateHiggsVBF HiggsFlatten CLW = 0.5",
        "color": "grey",
        "vbf": True,
    },

    # ptFlattenedMatchedHiggs_allKlambda_DetaMjj_SeparateHiggsVBF_MergedCollections_VBFHiggsFlatten 100e ECL = 2.0
    "predictions_ptFlattenMatchedHiggs_DetaMjj_SeparateHiggsVBF_VBFHiggsFlatten_CLW_2.h5": {
        "file": f"{spanet_dir_nestor}vbf/predictions_vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjj_SeparateHiggsVBF_HiggsVBFFLatten_CLW_2.h5",
        "true": "true_ptFlattenMatchedHiggs_separateHiggsVBF",
        "label": "ptFlattenedMatchedHiggs DetaMjj SeparateHiggsVBF VBFHiggsFlatten CLW = 2.0",
        "color": "black",
        "vbf": True,
    },

    # vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjjCentrality 100e
    #"predictions_ptFlattenMatchedHiggs_DetaMjjCentrality_100e": {
    #    "file": f"{spanet_dir_nestor}vbf/predictions_vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjjCentrality.h5",
    #    "true": "true_allklambda_DetaMjjCentrality",
    #    "label": "SPANet ptFlattenMatchedHiggs DetaMjj Centrality 100e",
    #    "color": "orange",
    #    "vbf": True,
    #},

    # vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjjCentrality 100e ECLW (0.5)
    #"predictions_ptFlattenMatchedHiggs_DetaMjjCentrality_ECL_0_5.h5": {
    #    "file": f"{spanet_dir_nestor}vbf/predictions_vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjjCentrality_ECL_0_5.h5",
    #    "true": "true_allklambda_DetaMjjCentrality",
    #    "label": "ptFlattenMatchedHiggs DetaMjj Centrality 100e CLW = 0.5",
    #    "color": "yellow",
    #    "vbf": True,
    #},

    # vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjjCentrality 100e ECLW (2)
    #"predictions_ptFlattenMatchedHiggs_DetaMjjCentrality_ECL_2.h5": {
    #    "file": f"{spanet_dir_nestor}vbf/predictions_vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjjCentrality_ECL_2.h5",
    #    "true": "true_allklambda_DetaMjjCentrality",
    #    "label": "ptFlattenMatchedHiggs DetaMjj Centrality 100e CLW = 2.0",
    #   "color": "brown",
    #    "vbf": True,
    #},

    # ptFlattenedMatchedHiggs_allKlambda_DetaMjj
    #"predictions_ptFlattenMatchedHiggs_DetaMjj": {
    #    "file": f"{spanet_dir_nestor}vbf/predictions_vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjj.h5",
    #    "true": "true_ptFlattenMatchedHiggs_detamjj",
    #    "label": "SPANet ptFlattenedMatchedHiggs DetaMjj",
    #    "color": "black",
    #    "vbf": True,
    #},

    # ptFlattenedMatchedHiggs_allKlambda_DetaMjj_AddVBFJetOrder
    #"predictions_ptFlattenMatchedHiggs_DetaMjj_AddVBFJetOrder": {
    #    "file": f"{spanet_dir_nestor}vbf/predictions_vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjj_AddVBFJetOrder.h5",
    #    "true": "true_ptFlattenMatchedHiggs_addVBFJetOrder",
    #    "label": "SPANet ptFlattenedMatchedHiggs DetaMjj AddVBFJetOrder",
    #    "color": "pink",
    #    "vbf": True,
    #},

    # ptFlattenedMatchedHiggs_allKlambda_DetaMjj_SeparateHiggsVBF_MergedCollections_FixNoneJets_1
    # "predictions_ptFlattenMatchedHiggs_DetaMjj_SeparateHiggsVBF_BothFlatten_200e": {
    #     "file": f"{spanet_dir_nestor}vbf/predictions_vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjj_SeparateHiggsVBF_MergedCollections_FixNoneJets_1.h5",
    #     "true": "true_ptFlattenMatchedHiggs_separateHiggsVBF",
    #     "label": "SPANet ptFlattenedMatchedHiggs DetaMjj SeparateHiggsVBF BothFlatten 200e",
    #     "color": "brown",
    #     "vbf": True,
    # },

    # ptFlattenedMatchedHiggs_allKlambda_DetaMjj_SeparateHiggsVBF_MergedCollections_2
    # "predictions_ptFlattenMatchedHiggs_DetaMjj_SeparateHiggsVBF_OnlyHiggsFlatten_200e": {
    #     "file": f"{spanet_dir_nestor}vbf/predictions_vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjj_SeparateHiggsVBF_MergedCollections_FixNoneJets_2.h5",
    #     "true": "true_ptFlattenMatchedHiggs_separateHiggsVBF",
    #     "label": "SPANet ptFlattenedMatchedHiggs DetaMjj SeparateHiggsVBF OnlyHiggsFlatten 200e",
    #     "color": "darkgrey",
    #     "vbf": True,
    # },

    # AllKlambda 9 jets
    "predictions_allKlambda_100e": {
        "file": f"{spanet_dir_nestor}vbf/predictions_allKlambda.h5",
        "true": "true_9jets_allklambda",
        "label": "SPANet 9j all_Klambda 100e",
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