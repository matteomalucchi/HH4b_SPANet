"""Script with configurations for each of the datasets that are to be tested for efficiency.

There are two dictionaries; one is a dictionary showing the actual datasets and the other is a list of true data, to which compare the predictions.
"""


# uncomment the configurations that you want to use

run2_dataset_MC = "true_9jets_allklambda"
run2_dataset_DATA = ""

spanet_dict = {}


# The `klambda` parameter so far only determines, if there is different klambdas or not. The type if not `none` doesn't matter.
true_dict = {}


# =============================================================================
# (nkontaxa) MODIFICATIONS below
# =============================================================================
spanet_dir_nestor = "/eos/user/n/nkontaxa/semester_project/spanet_outputs/"
true_dir_nestor = "/eos/user/m/mmalucch/spanet_infos/spanet_inputs/"

spanet_dict.update({

    #ptFlattenedMatchedHiggs_allKlambda_DetaMjj
        f"{spanet_dir_nestor}vbf/predictions_vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjj.h5": {
            "file": f"{spanet_dir_nestor}vbf/predictions_vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjj.h5",
            "true": "true_ptFlattenMatchedHiggs_detamjj",
            "label": "TMHF 200e",
            "color": "black",
            "vbf": True,
        },

    #ptFlattenedMatchedHiggs_allKlambda_DetaMjj_AddVBFJetOrder
        f"{spanet_dir_nestor}vbf/predictions_vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjj_AddVBFJetOrder.h5": {
           "file": f"{spanet_dir_nestor}vbf/predictions_vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjj_AddVBFJetOrder.h5",
           "true": "true_ptFlattenMatchedHiggs_addVBFJetOrder",
            "label": "AddVBFJetOrder 200e",
            "color": "pink",
            "vbf": True,
        },

    #ptFlattenedMatchedHiggs_allKlambda_DetaMjj_SeparateHiggsVBF_MergedCollections_FixNoneJets_1
    #    f"{spanet_dir_nestor}vbf/predictions_vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjj_SeparateHiggsVBF_MergedCollections_FixNoneJets_1.h5": {
    #        "file": f"{spanet_dir_nestor}vbf/predictions_vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjj_SeparateHiggsVBF_MergedCollections_FixNoneJets_1.h5",
    #        "true": "true_ptFlattenMatchedHiggs_separateHiggsVBF",
    #        "label": "SeparateHiggsVBF HiggsVBFFlatten 200e",
    #        "color": "brown",
    #        "vbf": True,
    #    },

    #ptFlattenedMatchedHiggs_allKlambda_DetaMjj_SeparateHiggsVBF_MergedCollections_FixNoneJets_2
    #    f"{spanet_dir_nestor}vbf/predictions_vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjj_SeparateHiggsVBF_MergedCollections_FixNoneJets_2.h5": {
    #        "file": f"{spanet_dir_nestor}vbf/predictions_vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjj_SeparateHiggsVBF_MergedCollections_FixNoneJets_2.h5",
    #        "true": "true_ptFlattenMatchedHiggs_separateHiggsVBF",
    #        "label": "SeparateHiggsVBF HiggsFlatten 200e",
    #        "color": "darkgrey",
    #        "vbf": True,
    #    },

#ptFlattenedMatchedHiggs_allKlambda_DetaMjj_SeparateHiggsVBF_MergedCollections_HiggsFlatten 100e
    ##f"{spanet_dir_nestor}vbf/predictions_vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjj_SeparateHiggsVBF_MergedCollections_HiggsFlatten_100e.h5": {
    ##    "file": f"{spanet_dir_nestor}vbf/predictions_vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjj_SeparateHiggsVBF_MergedCollections_HiggsFlatten_100e.h5",
    ##    "true": "true_ptFlattenMatchedHiggs_separateHiggsVBF",
    ##    "label": "ptFlattenedMatchedHiggs DetaMjj SeparateHiggsVBF HiggsFlatten",
    ##    "color": "purple",
    ##   "vbf": True,
    ##},

#ptFlattenedMatchedHiggs_allKlambda_DetaMjj_SeparateHiggsVBF_MergedCollections_VBFHiggsFlatten 100e
    ##f"{spanet_dir_nestor}vbf/predictions_vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjj_SeparateHiggsVBF_MergedCollections_FixNoneJets_vbfhiggsFlatten_100e.h5": {
    ##    "file": f"{spanet_dir_nestor}vbf/predictions_vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjj_SeparateHiggsVBF_MergedCollections_FixNoneJets_vbfhiggsFlatten_100e.h5",
    ##    "true": "true_ptFlattenMatchedHiggs_separateHiggsVBF",
    ##    "label": "ptFlattenedMatchedHiggs DetaMjj SeparateHiggsVBF VBFHiggsFlatten",
    ##    "color": "darkgrey",
    ##    "vbf": True,
    ##},

#ptFlattenedMatchedHiggs_allKlambda_DetaMjj_SeparateHiggsVBF_MergedCollections_VBFHiggsFlatten_extreme_classlossweights 100e
    ##f"{spanet_dir_nestor}vbf/predictions_vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjj_SeparateHiggsVBF_MergedCollections_HiggsVBFFlatten_extreme_classlossweights.h5": {
    ##    "file": f"{spanet_dir_nestor}vbf/predictions_vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjj_SeparateHiggsVBF_MergedCollections_HiggsVBFFlatten_extreme_classlossweights.h5",
    ##    "true": "true_ptFlattenMatchedHiggs_separateHiggsVBF",
    ##    "label": "ptFlattenedMatchedHiggs DetaMjj SeparateHiggsVBF VBFHiggsFlatten CLW = 5.0",
    ##    "color": "darkgreen",
    ##    "vbf": True,
    ##},

#ptFlattenedMatchedHiggs_allKlambda_DetaMjj_SeparateHiggsVBF_MergedCollections_VBFHiggsFlatten_extreme_classlossweights 100e 0.5
    ##f"{spanet_dir_nestor}vbf/predictions_vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjj_SeparateHiggsVBF_HiggsVBFFLatten_CLW_0_5.h5": {
    ##    "file": f"{spanet_dir_nestor}vbf/predictions_vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjj_SeparateHiggsVBF_HiggsVBFFLatten_CLW_0_5.h5",
    ##    "true": "true_ptFlattenMatchedHiggs_separateHiggsVBF",
    ##    "label": "ptFlattenedMatchedHiggs DetaMjj SeparateHiggsVBF VBFHiggsFlatten CLW = 0.5",
    ##    "color": "grey",
    ##    "vbf": True,
    ##},

#ptFlattenedMatchedHiggs_allKlambda_DetaMjj_SeparateHiggsVBF_MergedCollections_VBFHiggsFlatten_extreme_classlossweights 100e 2
    ##f"{spanet_dir_nestor}vbf/predictions_vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjj_SeparateHiggsVBF_HiggsVBFFLatten_CLW_2.h5": {
    ##    "file": f"{spanet_dir_nestor}vbf/predictions_vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjj_SeparateHiggsVBF_HiggsVBFFLatten_CLW_2.h5",
    ##    "true": "true_ptFlattenMatchedHiggs_separateHiggsVBF",
    ##    "label": "ptFlattenedMatchedHiggs DetaMjj SeparateHiggsVBF VBFHiggsFlatten CLW = 2.0",
    ##    "color": "black",
    ##    "vbf": True,
    ##},

#vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjjCentrality 100e
    ##f"{spanet_dir_nestor}vbf/predictions_vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjjCentrality.h5": {
    ##    "file": f"{spanet_dir_nestor}vbf/predictions_vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjjCentrality.h5",
    ##    "true": "true_allklambda_DetaMjjCentrality",
    ##    "label": "9j SPANet + Centrality 100e",
    ##   "color": "orange",
    ##   "vbf": True,
    ##},

#vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjjCentrality 100e
    #f"{spanet_dir_nestor}vbf/predictions_vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjjCentrality_ECL_0_5.h5": {
    #    "file": f"{spanet_dir_nestor}vbf/predictions_vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjjCentrality_ECL_0_5.h5",
    #    "true": "true_allklambda_DetaMjjCentrality",
    #    "label": "9j SPANet + Centrality 100e CLW = 0.5",
    #    "color": "yellow",
    #    "vbf": True,
    #},

#vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjjCentrality 100e
    #f"{spanet_dir_nestor}vbf/predictions_vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjjCentrality_ECL_2.h5": {
    #    "file": f"{spanet_dir_nestor}vbf/predictions_vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjjCentrality_ECL_2.h5",
    #    "true": "true_allklambda_DetaMjjCentrality",
    #    "label": "9j SPANet + Centrality 100e CLW = 2.0",
    #    "color": "brown",
    #    "vbf": True,
    #},

#AllKlambda 9 jets 200e
    f"{spanet_dir_nestor}vbf/predictions_allKlambda_200epochs.h5": {
        "file": f"{spanet_dir_nestor}vbf/predictions_allKlambda_200epochs.h5",
        "true": "true_9jets_allklambda",
        "label": "9j all_Klambda 200e",
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
        "name": f"{true_dir_nestor}vbf/vbf_ptFlattenMatchedHiggs_all_Klambda_DetaMjj/AllKlambda_DetaMjjJetTotalSPANetPtFlattenHiggsMatchedPadded_test.h5",
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