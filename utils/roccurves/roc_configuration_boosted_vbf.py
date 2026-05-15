"""Script with configurations for each of the datasets that are to be tested for efficiency."""

import logging

# logger = logging.getLogger(__name__)
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s | %(levelname)s | %(funcName)s | %(message)s",
#     datefmt="%d-%b-%y %H-%M-%S",
# )
logger = logging.getLogger(__name__)


roc_dict = {
#    "some_model_of_matteo": {
#        "file": "/eos/home-m/mmalucch/spanet_infos/dnn_roc/DNN_AN_1e-3_e20drop75_minDelta1em5_SPANet_newUpdates_newLeptonVeto_3L1Cut_UpdateJetVetoMap_postEE_thierry/tpr_fpr.npz",
#        "label": "some_model_of_matteo",
#        "color": "pink",
#    },
}


spanet_dir_thierry = "/eos/user/t/tharte/Analysis_data/predictions/"
spanet_dict = {
    "1_16_3_ggf_vbf_classifier_first_full_training": {
       "file": f"{spanet_dir_thierry}/boosted_ggf_vbf/1_16_3_boosted_vbf_ggf_classification_vbfjets.h5",
       "true": "boosted_vbf_ggf_jetobjects",
       "label": "mixed data with btag and PD",
       "color": "purple",
   },
}


true_path_thierry = "/eos/user/t/tharte/Analysis_data/spanet_samples/ggf_vbf_boosted/"
true_dict = {
       "boosted_vbf_ggf_jetobjects": {
       "name": f"{true_path_thierry}/1_16_3_ggf_vbf_boosted_jetobjects/JetGoodVBF_test.h5",
       "jet_coll": "JetVBF",
    },
}
