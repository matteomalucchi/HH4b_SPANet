"""Script with configurations for each of the datasets that are to be tested for efficiency.

There are two dictionaries; one is a dictionary showing the actual datasets and the other is a list of true data, to which compare the predictions.
"""


# uncomment the configurations that you want to use

run2_dataset_MC = "true_9jets_allklambda"
run2_dataset_DATA = ""

spanet_dict = {}
true_dict = {}


spanet_dir_nestor = "/eos/user/n/nkontaxa/semester_project/spanet_outputs/"
true_dir_nestor = "/eos/user/m/mmalucch/spanet_infos/spanet_inputs/"

spanet_dict.update({

#AllKlambda 9 jets 100e
    #f"{spanet_dir_nestor}vbf/predictions_allKlambda.h5": {
    #    "file": f"{spanet_dir_nestor}vbf/predictions_allKlambda.h5",
    #    "true": "true_9jets_allklambda",
    #    "label": "9j all_Klambda 100e",
    #    "color": "red",
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

#allKlambda_DetaMjj_NGW_noextravars
    f"{spanet_dir_nestor}vbf/predictions_allKlambda_DetaMjj_novars_NormGenWeights.h5": {
        "file": f"{spanet_dir_nestor}vbf/predictions_allKlambda_DetaMjj_novars_NormGenWeights.h5",
        "true": "true_detamjj_ngw",
        "label": "DetaMjj NGW noextravars 200e",
        "color": "black",
        "vbf": True,
    },

#allKlambda_DetaMjj_NNGW_noextravars
    f"{spanet_dir_nestor}vbf/predictions_allKlambda_DetaMjj_novars_Non-NormGenWeights.h5": {
        "file": f"{spanet_dir_nestor}vbf/predictions_allKlambda_DetaMjj_novars_Non-NormGenWeights.h5",
        "true": "true_detamjj_nngw",
        "label": "DetaMjj NNGW noextravars 200e",
        "color": "green",
        "vbf": True,
    },

#allKlambda_DetaMjj_NNGW_extravars
    #f"{spanet_dir_nestor}vbf/predictions_allKlambda_DetaMjj_extravars_Non-NormGenWeights.h5": {
    #    "file": f"{spanet_dir_nestor}vbf/predictions_allKlambda_DetaMjj_extravars_Non-NormGenWeights.h5",
    #    "true": "true_detamjj_nngw",
    #    "label": "DetaMjj NNGW extravars 200e",
    #    "color": "yellow",
    #    "vbf": True,
    #},

#allKlambda_DetaMjj_NNGW_extravars_extreme_classlossweights
    #f"{spanet_dir_nestor}vbf/predictions_allKlambda_DetaMjj_extravars_Non-NormGenWeights_extreme_classlossweights.h5": {
    #    "file": f"{spanet_dir_nestor}vbf/predictions_allKlambda_DetaMjj_extravars_Non-NormGenWeights_extreme_classlossweights.h5",
    #    "true": "true_detamjj_nngw",
    #   "label": "DetaMjj NNGW extravars ECLW (5.0)",
    #    "color": "brown",
    #    "vbf": True,
    #},

#allKlambda_HiggsPairing 100e
    ##f"{spanet_dir_nestor}vbf/predictions_allKlambda_HiggsPairing.h5": {
    ##    "file": f"{spanet_dir_nestor}vbf/predictions_allKlambda_HiggsPairing.h5",
    ##    "true": "true_allklambda_HiggsPairing",
    ##    "label": "allKlambda HiggsPairing 100e",
    ##   "color": "orange",
    ##    "vbf": True,
    ##},

#allKlambda_VBFPairing 100e
    ##f"{spanet_dir_nestor}vbf/predictions_allKlambda_vbfpairing.h5": {
    ##    "file": f"{spanet_dir_nestor}vbf/predictions_allKlambda_vbfpairing.h5",
    ##    "true": "true_allklambda_VBFPairing",
    ##    "label": "allKlambda VBFPairing 100e",
    ##    "color": "purple",
    ##    "vbf": True,
    ##},

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