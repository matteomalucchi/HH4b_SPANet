KEEP_TOGETHER_COLLECTIONS = ["add_jet1pt"]

jet_collections_dict = {
    "JET_COLLECTIONS_SEPARATE_HIGGS_VBF": [
        {
            "JetGoodProvHiggsPtFlattenPadded": {
                "saved_name": "JetHiggs",
                "max_num_jets": 4,
                "resonances": ["h1", "h2"],
            },
            "JetGoodVBFMergedProvVBFPtFlattenPadded": {
                "saved_name": "JetVBF",
                "max_num_jets": 5,
                "resonances": ["vbf"],
            },
        },
        {
            "JetGoodProvHiggsPtFlattenPadded": {
                "saved_name": "JetHiggs",
                "max_num_jets": 4,
                "resonances": ["h1", "h2"],
            },
            "JetGoodVBFMergedProvVBFPadded": {
                "saved_name": "JetVBF",
                "max_num_jets": 5,
                "resonances": ["vbf"],
            },
        },
        {
            "JetGoodProvHiggsPadded": {
                "saved_name": "JetHiggs",
                "max_num_jets": 4,
                "resonances": ["h1", "h2"],
            },
            "JetGoodVBFMergedProvVBFPadded": {
                "saved_name": "JetVBF",
                "max_num_jets": 5,
                "resonances": ["vbf"],
            },
        },
    ],
    "JET_COLLECTIONS_SEPARATE_HIGGS_VBF_MERGED_COLL": [
        {
            "JetTotalSPANetSeparateProvHiggsVBFPtFlattenPadded": {
                "saved_name": "Jet",
                "max_num_jets": 9,
                "resonances": ["h1", "h2", "vbf"],
            },
        },
        {
            "JetTotalSPANetSeparateProvHiggsVBFPtFlattenOnlyHiggsPadded": {
                "saved_name": "Jet",
                "max_num_jets": 9,
                "resonances": ["h1", "h2", "vbf"],
            },
        },
        {
            "JetTotalSPANetSeparateProvHiggsVBFPadded": {
                "saved_name": "Jet",
                "max_num_jets": 9,
                "resonances": ["h1", "h2", "vbf"],
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
