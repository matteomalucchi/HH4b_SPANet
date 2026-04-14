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
   "some_model_of_matteo": {
       "file": "/eos/home-m/mmalucch/spanet_infos/dnn_roc/DNN_AN_1e-3_e20drop75_minDelta1em5_SPANet_newUpdates_newLeptonVeto_3L1Cut_UpdateJetVetoMap_postEE_thierry/tpr_fpr.npz",
       "label": "some_model_of_matteo",
       "color": "pink",
   },
}


spanet_dir_kevin = "/eos/user/k/kehrler/semester_project/HH4b_SPANet/predictions/"
spanet_dict = {
#    "spanet_dict_example_model_from_thierry": {
#        "true": "true_dict_example_model_from_thierry",
#        "file": f"{spanet_dir_kevin}example_model_from_thierry/example_model_from_thierry.h5",
#        "label": "example_model_from_thierry",
#        "color": "pink",
#    },

#     "spanet_dict_hh4b_classification_trial": {
#         "file": f"{spanet_dir_kevin}hh4b_classification_trial/hh4b_classification_trial.h5",
#         "label": "hh4b_classification_trial",
#         "true": "true_dict_hh4b_classification_trial",
#         "color": "pink",
#    },

#     "spanet_dict_hh4b_classification_5jetinput": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_5jetinput/hh4b_classification_5jetinput.h5",
#        "true": "true_dict_hh4b_classification_5jetinput",
#        "label": "hh4b_classification_5jetinput",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_btagPNetB_5wp": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_btagPNetB_5wp/hh4b_classification_btagPNetB_5wp.h5",
#        "true": "true_dict_hh4b_classification_btagPNetB_5wp",
#        "label": "hh4b_classification_btagPNetB_5wp",
#        "color": "pink",
#    },

#     "spanet_dict_hh4b_classification_AN23_184_incomplete": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_AN23_184_incomplete/hh4b_classification_AN23_184_incomplete.h5",
#        "true": "true_dict_hh4b_classification_AN23_184_incomplete",
#        "label": "hh4b_classification_AN23_184_incomplete",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_AN23_184": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_AN23_184/hh4b_classification_AN23_184.h5",
#        "true": "true_dict_hh4b_classification_AN23_184",
#        "label": "hh4b_classification_AN23_184",
#        "color": "tab:blue",
#    },

#    "spanet_dict_hh4b_classification_var000000": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000000/hh4b_classification_var000000.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000000",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000001": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000001/hh4b_classification_var000001.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000001",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000002": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000002/hh4b_classification_var000002.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000002",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000003": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000003/hh4b_classification_var000003.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000003",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000004": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000004/hh4b_classification_var000004.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000004",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000005": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000005/hh4b_classification_var000005.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000005",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000006": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000006/hh4b_classification_var000006.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000006",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000007": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000007/hh4b_classification_var000007.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000007",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000008": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000008/hh4b_classification_var000008.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000008",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000009": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000009/hh4b_classification_var000009.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000009",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000010": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000010/hh4b_classification_var000010.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000010",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000011": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000011/hh4b_classification_var000011.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000011",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000012": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000012/hh4b_classification_var000012.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000012",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000013": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000013/hh4b_classification_var000013.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000013",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000014": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000014/hh4b_classification_var000014.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000014",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000015": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000015/hh4b_classification_var000015.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000015",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000016": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000016/hh4b_classification_var000016.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000016",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000017": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000017/hh4b_classification_var000017.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000017",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000018": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000018/hh4b_classification_var000018.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000018",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000019": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000019/hh4b_classification_var000019.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000019",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000020": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000020/hh4b_classification_var000020.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000020",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000021": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000021/hh4b_classification_var000021.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000021",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000022": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000022/hh4b_classification_var000022.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000022",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000023": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000023/hh4b_classification_var000023.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000023",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000024": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000024/hh4b_classification_var000024.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000024",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000025": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000025/hh4b_classification_var000025.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000025",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000026": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000026/hh4b_classification_var000026.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000026",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000027": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000027/hh4b_classification_var000027.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000027",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000028": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000028/hh4b_classification_var000028.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000028",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000029": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000029/hh4b_classification_var000029.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000029",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000030": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000030/hh4b_classification_var000030.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000030",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000031": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000031/hh4b_classification_var000031.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000031",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000032": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000032/hh4b_classification_var000032.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000032",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000033": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000033/hh4b_classification_var000033.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000033",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000034": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000034/hh4b_classification_var000034.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000034",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000035": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000035/hh4b_classification_var000035.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000035",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000036": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000036/hh4b_classification_var000036.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000036",
#        "color": "tab:purple",
#    },

#    "spanet_dict_hh4b_classification_var000037": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000037/hh4b_classification_var000037.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000037",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000038": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000038/hh4b_classification_var000038.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000038",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000039": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000039/hh4b_classification_var000039.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000039",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000040": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000040/hh4b_classification_var000040.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000040",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000041": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000041/hh4b_classification_var000041.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000041",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000042": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000042/hh4b_classification_var000042.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000042",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000043": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000043/hh4b_classification_var000043.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000043",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000044": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000044/hh4b_classification_var000044.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000044",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000045": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000045/hh4b_classification_var000045.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000045",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000046": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000046/hh4b_classification_var000046.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000046",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000047": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000047/hh4b_classification_var000047.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000047",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000048": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000048/hh4b_classification_var000048.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000048",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000049": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000049/hh4b_classification_var000049.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000049",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000050": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000050/hh4b_classification_var000050.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000050",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000051": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000051/hh4b_classification_var000051.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000051",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000052": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000052/hh4b_classification_var000052.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000052",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000053": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000053/hh4b_classification_var000053.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000053",
#        "color": "pink",
#    },

#    "spanet_dict_hh4b_classification_var000054": {
#        "file": f"{spanet_dir_kevin}hh4b_classification_var000054/hh4b_classification_var000054.h5",
#        "true": "true_dict_hh4b_classification_var0000##",
#        "label": "hh4b_classification_var000054",
#        "color": "pink",
#    },

    "spanet_dict_hh4b_classification_var000055": {
       "file": f"{spanet_dir_kevin}hh4b_classification_var000055/hh4b_classification_var000055.h5",
       "true": "true_dict_hh4b_classification_var0000##",
       "label": "hh4b_classification_var000055",
       "color": "pink",
   },
}


true_path_thierry = "/eos/user/t/tharte/Analysis_data/spanet_samples/classification/"
true_dict = {
       "true_dict_example_model_from_thierry": {
       "name": f"{true_path_thierry}conversion_with_vbf/columns_for_classifier_test.h5"
    },

       "true_dict_hh4b_classification_trial": {
       "name": f"{true_path_thierry}conversion_with_vbf/columns_for_classifierJetGoodFromHiggsOrdered_test.h5"
    },

       "true_dict_hh4b_classification_5jetinput": {
       "name": f"{true_path_thierry}1_15_8_jetgoodfromhiggsordered5jets/columns_for_classifierJetGoodFromHiggsOrdered5Jets_test.h5"
    },

        "true_dict_hh4b_classification_btagPNetB_5wp": {
        "name": f"{true_path_thierry}1_15_8_jetgoodfromhiggsordered5jets/columns_for_classifierJetGoodFromHiggsOrdered5Jets_test.h5"
       },

       "true_dict_hh4b_classification_AN23_184_incomplete": {
       "name": f"{true_path_thierry}1_15_8_jetgoodfromhiggsordered5jets/columns_for_classifierJetGoodFromHiggsOrdered5Jets_test.h5"
   },

    "true_dict_hh4b_classification_AN23_184": {
        "name": f"{true_path_thierry}1_15_9_jetgoodfromhiggsordered5jets_additional_parameters/columns_for_sig_bkg_classifierJetGoodFromHiggsOrdered5Jets_test.h5"
    },

    "true_dict_hh4b_classification_var0000##": {
        "name": f"{true_path_thierry}1_15_9_jetgoodfromhiggsordered5jets_additional_parameters/columns_for_sig_bkg_classifierJetGoodFromHiggsOrdered5Jets_test.h5"
    },
}