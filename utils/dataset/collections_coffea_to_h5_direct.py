KEEP_TOGETHER_COLLECTIONS = ["add_jet1pt"]

jet_collections_dict = {
    "JET_GOOD_COLLECTIONS_HIGGS_PAIRING": [
        {
            "JetGoodProvHiggsPtFlattenPadded": {
                "saved_name": "Jet",
                "max_num_jets": 5,
                "resonances": ["h1", "h2"],
                "prov_key": "provenance",
                "min_num_jets": 4,
            },
        },
        {
            "JetGoodProvHiggsPadded": {
                "saved_name": "Jet",
                "max_num_jets": 5,
                "resonances": ["h1", "h2"],
                "prov_key": "provenance",
                "min_num_jets": 4,
            },
        },
    ],
    "JET_COLLECTIONS_SEPARATE_HIGGS_VBF": [
        {
            "JetGoodProvHiggsPtFlattenPadded": {
                "saved_name": "JetHiggs",
                "max_num_jets": 4,
                "resonances": ["h1", "h2"],
                "prov_key": "provenance",
                "min_num_jets": 4,
            },
            "JetGoodVBFMergedProvVBFPtFlattenPadded": {
                "saved_name": "JetVBF",
                "max_num_jets": 5,
                "resonances": ["vbf"],
                "prov_key": "provenance",
                "min_num_jets": 0,
            },
        },
        {
            "JetGoodProvHiggsPtFlattenPadded": {
                "saved_name": "JetHiggs",
                "max_num_jets": 4,
                "resonances": ["h1", "h2"],
                "prov_key": "provenance",
                "min_num_jets": 4,
            },
            "JetGoodVBFMergedProvVBFPadded": {
                "saved_name": "JetVBF",
                "max_num_jets": 5,
                "resonances": ["vbf"],
                "prov_key": "provenance",
                "min_num_jets": 0,
            },
        },
        {
            "JetGoodProvHiggsPadded": {
                "saved_name": "JetHiggs",
                "max_num_jets": 4,
                "resonances": ["h1", "h2"],
                "prov_key": "provenance",
                "min_num_jets": 4,
            },
            "JetGoodVBFMergedProvVBFPadded": {
                "saved_name": "JetVBF",
                "max_num_jets": 5,
                "resonances": ["vbf"],
                "prov_key": "provenance",
                "min_num_jets": 0,
            },
        },
    ],
    "JET_COLLECTIONS_SEPARATE_HIGGS_VBF_MERGED_COLL": [
        {
            "JetTotalSPANetSeparateProvHiggsVBFPtFlattenPadded": {
                "saved_name": "Jet",
                "max_num_jets": 9,
                "resonances": ["h1", "h2", "vbf"],
                "prov_key": "provenance",
            },
        },
        {
            "JetTotalSPANetSeparateProvHiggsVBFPtFlattenOnlyHiggsPadded": {
                "saved_name": "Jet",
                "max_num_jets": 9,
                "resonances": ["h1", "h2", "vbf"],
                "prov_key": "provenance",
            },
        },
        {
            "JetTotalSPANetSeparateProvHiggsVBFPadded": {
                "saved_name": "Jet",
                "max_num_jets": 9,
                "resonances": ["h1", "h2", "vbf"],
                "prov_key": "provenance",
            },
        },
    ],
    "JET_COLLECTIONS_SIG_BKG_CLASSIFIER": [
        {
            "JetGoodFromHiggsOrderedLeading": {
                "saved_name": "JetHiggsLeading",
                "max_num_jets": 2,
                "resonances": ["h1"],
                "prov_key": "reco_provenance",
                "min_num_jets": 2,
            },
            "JetGoodFromHiggsOrderedSubLeading": {
                "saved_name": "JetHiggsSubLeading",
                "max_num_jets": 2,
                "resonances": ["h2"],
                "prov_key": "reco_provenance",
                "min_num_jets": 2,
            },
            "add_jet1pt": {
                "saved_name": "Jet5th",
                "max_num_jets": 1,
                "resonances": ["add"],
                "prov_key": "reco_provenance",
                "min_num_jets": 0,
            },
        },
    ],
    "JET_COLLECTIONS_VBF_PAIRING_AFTER_HIGGS_PAIRING": [
        {
            "JetGoodVBFMergedProvVBFPadded": {
                "saved_name": "Jet",
                "max_num_jets": 5,
                "resonances": ["vbf"],
                "min_num_jets": 0,
                "prov_key": "provenance",
            },
        },
    ],
    "JET_COLLECTIONS_VBF_PAIRING_AFTER_HIGGS_PAIRING_TOTAL": [
        # {
        #     "JetGoodVBFMergedProvVBFPadded": {
        #         "saved_name": "Jet",
        #         "max_num_jets": 5,
        #         "resonances": ["vbf"],
        #         "min_num_jets": 0,
        #         "prov_key": "provenance_vbf",
        #     },
        # },
        {
            "JetGoodVBFMergedProvVBFPadded": {
                "saved_name": "JetVBF",
                "max_num_jets": 5,
                "resonances": ["vbf"],
                "min_num_jets": 0,
                "prov_key": "provenance_vbf",
            },
            "JetGoodProvHiggsPadded": {
                "saved_name": "JetHiggs",
                "max_num_jets": 4,
                "resonances": [],
                "min_num_jets": 4,
                "prov_key": "provenance_higgs",
            },
        },
        # {
        #     "JetTotalSPANetPadded": {
        #         "saved_name": "Jet",
        #         "max_num_jets": 9,
        #         "resonances": ["vbf"],
        #         "min_num_jets": 4,
        #         "prov_key": "provenance_vbf",
        #     },
        # },
    ],
    "JET_COLLECTION_VBF_BOOSTED": [
        {
            "JetGoodVBF": {
                "saved_name": "JetVBF",
                "resonances": ["vbf"],
                "min_num_jets": 0,
                "max_num_jets": 2,
                "prov_key": "provenance",
            },
            # "JetGoodVBFCandidates": {
            #     "saved_name": "JetVBFCandidates",
            #     "resources": ["vbf"],
            #     "min_num_jets": 0,
            #     "max_num_jets": 5,
            #     "prov_key": "provenance",
            # }
        }
    ]
}

jet_like_global_collections_dict = {
    "JET_LIKE_GLOBAL_HIGGS_ORDERED": [
        {
            "JetGoodProvHiggsPadded": {
                "saved_name_var": None,
                "n_var": None,  # flat 1D array of length N_events * max_jets, no count variable
                "max_jets": 4,
            },
        },
    ],
}

global_collections_dict = {
    "GLOBAL_COLLECTIONS_VBF": [
        {
            "events_mjjJetTotalSPANetPtFlattenPadded": {
                "saved_name_coll": "Event",
                "saved_name_var": "mjjVBF",
            },
            "events_detaJetTotalSPANetPtFlattenPadded": {
                "saved_name_coll": "Event",
                "saved_name_var": "detaVBF",
            },
            "events_centralityHiggsLeadingRun2JetTotalSPANetPtFlattenPadded": {
                "saved_name_coll": "Event",
                "saved_name_var": "centralityHiggsLeadingRun2VBF",
            },
            "events_centralityHiggsSubLeadingRun2JetTotalSPANetPtFlattenPadded": {
                "saved_name_coll": "Event",
                "saved_name_var": "centralityHiggsSubLeadingRun2VBF",
            },
        },
        {
            "events_mjjJetTotalSPANetPadded": {
                "saved_name_coll": "Event",
                "saved_name_var": "mjjVBF",
            },
            "events_detaJetTotalSPANetPadded": {
                "saved_name_coll": "Event",
                "saved_name_var": "detaVBF",
            },
            "events_centralityHiggsLeadingRun2JetTotalSPANetPadded": {
                "saved_name_coll": "Event",
                "saved_name_var": "centralityHiggsLeadingRun2VBF",
            },
            "events_centralityHiggsSubLeadingRun2JetTotalSPANetPadded": {
                "saved_name_coll": "Event",
                "saved_name_var": "centralityHiggsSubLeadingRun2VBF",
            },
        },
    ],
    "GLOBAL_COLLECTIONS_SEPARATE_HIGGS_VBF": [
        {
            "events_mjjJetGoodVBFMergedProvVBFPtFlattenPadded": {
                "saved_name_coll": "Event",
                "saved_name_var": "mjjVBF",
            },
            "events_detaJetGoodVBFMergedProvVBFPtFlattenPadded": {
                "saved_name_coll": "Event",
                "saved_name_var": "detaVBF",
            },
            "events_centralityHiggsLeadingJetGoodVBFMergedProvVBFPtFlattenPadded": {
                "saved_name_coll": "Event",
                "saved_name_var": "centralityHiggsLeadingVBF",
            },
            "events_centralityHiggsSubLeadingJetGoodVBFMergedProvVBFPtFlattenPadded": {
                "saved_name_coll": "Event",
                "saved_name_var": "centralityHiggsSubLeadingVBF",
            },
            "__save_all_remaining__": True,
        },
        {
            "events_mjjJetGoodVBFMergedProvVBFPadded": {
                "saved_name_coll": "Event",
                "saved_name_var": "mjjVBF",
            },
            "events_detaJetGoodVBFMergedProvVBFPadded": {
                "saved_name_coll": "Event",
                "saved_name_var": "detaVBF",
            },
            "events_centralityHiggsLeadingJetGoodVBFMergedProvVBFPadded": {
                "saved_name_coll": "Event",
                "saved_name_var": "centralityHiggsLeadingVBF",
            },
            "events_centralityHiggsSubLeadingJetGoodVBFMergedProvVBFPadded": {
                "saved_name_coll": "Event",
                "saved_name_var": "centralityHiggsSubLeadingVBF",
            },
            "__save_all_remaining__": True,
        },
        {
            "events_mjjJetGoodVBFMergedProvVBFPadded": {
                "saved_name_coll": "Event",
                "saved_name_var": "mjjVBF",
            },
            "events_detaJetGoodVBFMergedProvVBFPadded": {
                "saved_name_coll": "Event",
                "saved_name_var": "detaVBF",
            },
            "events_centralityHiggsLeadingJetGoodVBFMergedProvVBFPadded": {
                "saved_name_coll": "Event",
                "saved_name_var": "centralityHiggsLeadingVBF",
            },
            "events_centralityHiggsSubLeadingJetGoodVBFMergedProvVBFPadded": {
                "saved_name_coll": "Event",
                "saved_name_var": "centralityHiggsSubLeadingVBF",
            },
            "__save_all_remaining__": True,
        },
    ],
    "GLOBAL_COLLECTIONS_VBF_MERGED_COLL": [
        {
            "events_mjjJetGoodVBFMergedProvVBFPtFlattenPadded": {
                "saved_name_coll": "Event",
                "saved_name_var": "mjjVBF",
            },
            "events_detaJetGoodVBFMergedProvVBFPtFlattenPadded": {
                "saved_name_coll": "Event",
                "saved_name_var": "detaVBF",
            },
            "events_centralityHiggsLeadingRun2JetGoodVBFMergedProvVBFPtFlattenPadded": {
                "saved_name_coll": "Event",
                "saved_name_var": "centralityHiggsLeadingRun2VBF",
            },
            "events_centralityHiggsSubLeadingRun2JetGoodVBFMergedProvVBFPtFlattenPadded": {
                "saved_name_coll": "Event",
                "saved_name_var": "centralityHiggsSubLeadingRun2VBF",
            },
        },
        {
            "events_mjjJetGoodVBFMergedProvVBFPadded": {
                "saved_name_coll": "Event",
                "saved_name_var": "mjjVBF",
            },
            "events_detaJetGoodVBFMergedProvVBFPadded": {
                "saved_name_coll": "Event",
                "saved_name_var": "detaVBF",
            },
            "events_centralityHiggsLeadingRun2JetGoodVBFMergedProvVBFPadded": {
                "saved_name_coll": "Event",
                "saved_name_var": "centralityHiggsLeadingRun2VBF",
            },
            "events_centralityHiggsSubLeadingRun2JetGoodVBFMergedProvVBFPadded": {
                "saved_name_coll": "Event",
                "saved_name_var": "centralityHiggsSubLeadingRun2VBF",
            },
        },
        {
            "events_mjjJetGoodVBFMergedProvVBFPadded": {
                "saved_name_coll": "Event",
                "saved_name_var": "mjjVBF",
            },
            "events_detaJetGoodVBFMergedProvVBFPadded": {
                "saved_name_coll": "Event",
                "saved_name_var": "detaVBF",
            },
            "events_centralityHiggsLeadingRun2JetGoodVBFMergedProvVBFPadded": {
                "saved_name_coll": "Event",
                "saved_name_var": "centralityHiggsLeadingRun2VBF",
            },
            "events_centralityHiggsSubLeadingRun2JetGoodVBFMergedProvVBFPadded": {
                "saved_name_coll": "Event",
                "saved_name_var": "centralityHiggsSubLeadingRun2VBF",
            },
        },
    ],
    
}

# Special cases moving single global variables to a group of their own, on top
# of where they are saved otherwise (by `-g all` or by a `global_collections_dict`
# group). Chosen with `-gr <NAME>` (`global_regroup: <NAME>` in the dataset YAML).
#
# The global MASK (--global-mask) is one per group: a group is masked in an
# event only when all its variables are padded. Variables that are padded
# together, e.g. the ones of the VBF pair, which is not always found, have to be
# in a group of their own to be masked, instead of in `Event` next to variables
# that are always there.
#
# Each entry maps a coffea column name to
#   "saved_name_coll": the group, i.e. INPUTS/<saved_name_coll>/
#   "saved_name_var":  the variable name in it; None keeps the name it would
#                      have had otherwise
# Columns of an entry that are not in the coffea file are skipped, so the
# variants of a variable (e.g. the PtFlatten ones) can be listed together.
global_regroup_dict = {
    "VBF_PAIR_GLOBAL": {
        "events_mjjJetGoodVBFMergedProvVBFPadded": {
            "saved_name_coll": "VBFPair",
            "saved_name_var": None,
        },
        "events_detaJetGoodVBFMergedProvVBFPadded": {
            "saved_name_coll": "VBFPair",
            "saved_name_var": None,
        },
        "events_centralityHiggsLeadingJetGoodVBFMergedProvVBFPadded": {
            "saved_name_coll": "VBFPair",
            "saved_name_var": None,
        },
        "events_centralityHiggsSubLeadingJetGoodVBFMergedProvVBFPadded": {
            "saved_name_coll": "VBFPair",
            "saved_name_var": None,
        },
        "events_mjjJetGoodVBFMergedProvVBFPtFlattenPadded": {
            "saved_name_coll": "VBFPair",
            "saved_name_var": None,
        },
        "events_detaJetGoodVBFMergedProvVBFPtFlattenPadded": {
            "saved_name_coll": "VBFPair",
            "saved_name_var": None,
        },
        "events_centralityHiggsLeadingJetGoodVBFMergedProvVBFPtFlattenPadded": {
            "saved_name_coll": "VBFPair",
            "saved_name_var": None,
        },
        "events_centralityHiggsSubLeadingJetGoodVBFMergedProvVBFPtFlattenPadded": {
            "saved_name_coll": "VBFPair",
            "saved_name_var": None,
        },
    },
}
