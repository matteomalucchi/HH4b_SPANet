# spanet_dir = "/eos/home-r/ramellar/out_prediction_files/"
# spanet_dir = "/afs/cern.ch/user/m/mmalucch/public/out_prediction_files/"
spanet_dir = "/eos/home-m/mmalucch/spanet_inputs/out_prediction_files/"


# uncomment the configurations that you want to use
print(
    "WARNING: the naming has to follow the convetions in",
    " efficiency_functions.check_names function in order to work properly",
    " associating the spanet predicted files with the true files",
)
# uncomment the configurations that you want to use
spanet_dict = {
    "5_jets_ATLAS_ptreg": f"{spanet_dir}out_spanet_prediction_5jets_ptreg_ATLAS.h5",  # THIS
    # "5_jets_ATLAS_ptreg_5train_klambda0": f"{spanet_dir}out_spanet_prediction_5jets_klambda0.h5",
    # "5_jets_ATLAS_ptreg_5train_klambda2p45": f"{spanet_dir}out_spanet_prediction_5jets_klambda2p45.h5",
    # "5_jets_ATLAS_ptreg_5train_klambda5": f"{spanet_dir}out_spanet_prediction_5jets_klambda5.h5",
    #
    # "4_jets_ATLAS_ptreg_5train": f"{spanet_dir}out_spanet_prediction_5jets_ptreg_ATLAS.h5",  # THIS
    # "4_jets_ATLAS_ptreg_5train_klambda0": f"{spanet_dir}out_spanet_prediction_5jets_klambda0.h5",
    # "4_jets_ATLAS_ptreg_5train_klambda2p45": f"{spanet_dir}out_spanet_prediction_5jets_klambda2p45.h5",
    # "4_jets_ATLAS_ptreg_5train_klambda5": f"{spanet_dir}out_spanet_prediction_5jets_klambda5.h5",
    #
    # "4_jets_ATLAS_ptreg_5train": f"{spanet_dir}out_spanet_prediction_4jets_5training.h5", # THIS
    # "4_jets_ATLAS_ptreg_5train_klambda0": f"{spanet_dir}out_spanet_prediction_4jets_klambda0_5jetstrainig.h5",
    # "4_jets_ATLAS_ptreg_5train_klambda2p45": f"{spanet_dir}out_spanet_prediction_4jets_klambda2p45_5jetstrainig.h5",
    # "4_jets_ATLAS_ptreg_5train_klambda5": f"{spanet_dir}out_spanet_prediction_4jets_klambda5_5jetstrainig.h5",
    #
    "4_jets_5global_ATLAS_ptreg": f"{spanet_dir}out_9_spanet_prediction_4jets_5global_ATLAS_ptreg_klambda1.h5",  # THIS
    # "4_jets_5global_ATLAS_ptreg_klambda0": f"{spanet_dir}out_9_spanet_prediction_4jets_5global_ATLAS_ptreg_klambda0.h5",
    # "4_jets_5global_ATLAS_ptreg_klambda2p45": f"{spanet_dir}out_9_spanet_prediction_4jets_5global_ATLAS_ptreg_klambda2p45.h5",
    # "4_jets_5global_ATLAS_ptreg_klambda5": f"{spanet_dir}out_9_spanet_prediction_4jets_5global_ATLAS_ptreg_klambda5.h5",
    #
    # "5_jets_ATLAS_ptreg_allklambda_train_klinput": f"{spanet_dir}out_spanet_prediction_5jets_lr1e4_kl_300e.h5",
    # # "/work/mmalucch/out_hh4b/out_spanet/output_JetGood_test.h5",  # HERE
    # "5_jets_ATLAS_ptreg_allklambda_train": f"{spanet_dir}out_spanet_prediction_5jets_lr1e4_noevkl_300e.h5",
    # # "/work/mmalucch/out_hh4b/out_spanet/output_JetGood_test.h5",  # HERE
    # "5_jets_ATLAS_ptreg_allklambda_eval": f"{spanet_dir}out_spanet_prediction_SMtraining_lr1e4_evkl.h5",
    # "/work/mmalucch/out_hh4b/out_spanet/output_JetGood_test.h5",  # HERE
    #
    # "5_jets_ATLAS_ptreg_allklambda_train_klinput_newkl_newCuts_newCutsEval": f"{spanet_dir}spanet_prediction_nc_on_nc_300e.h5",
    # "5_jets_ATLAS_ptreg_allklambda_train_klinput_newkl_newCuts_oldCutsEval": f"{spanet_dir}spanet_prediction_nc_on_oc_kl3p5.h5",
    # "5_jets_ATLAS_ptreg_allklambda_train_klinput_newkl_oldCuts_oldCutsEval": f"{spanet_dir}spanet_prediction_oc_on_oc_kl3p5.h5",
    #
    # "4_jets":  f"{spanet_dir}out_0_spanet_prediction_4jets.h5",
    # "5_jets": f"{spanet_dir}out_1_spanet_prediction_5jets.h5",
    # "5_jets_btag_presel": f"{spanet_dir}out_2_spanet_prediction_5jets_btagpresel.h5",
    # "4_jets_ATLAS_ptreg_5train_btagpresel": f"{spanet_dir}out_spanet_prediction_4jets_5training_btag.h5", # THIS
    # "5_jets_btag_presel_ATLAS_ptreg": f"{spanet_dir}out_spanet_prediction_5jets_btagpresel_ptreg_ATLAS.h5", # THIS
    # "4_jets_5global": f"{spanet_dir}out_3_spanet_prediction_4jets_5global_9999pad.h5",
    # "4_jets_5global_btagpresel": f"{spanet_dir}out_4_spanet_prediction_4jets_5global_9999pad_btagpresel.h5",
    # "4_jets_5global_ATLAS":  f"{spanet_dir}out_5_spanet_prediction_ATLAS.h5",
    # "4_jets_5global_ptreg": f"{spanet_dir}out_7_spanet_prediction_4jets_5global_ptreg_klambda1.h5",
    # "4_jets_5global_ptreg_klambda0": f"{spanet_dir}out_7_spanet_prediction_4jets_5global_ptreg_klambda0.h5",
    # "4_jets_5global_ptreg_klambda2p45": f"{spanet_dir}out_7_spanet_prediction_4jets_5global_ptreg_klambda2p45.h5",
    # "4_jets_5global_ptreg_klambda5": f"{spanet_dir}out_7_spanet_prediction_4jets_5global_ptreg_klambda5.h5",
    # "4_jets_5global_ATLAS_ptreg_cos_sin_phi": f"{spanet_dir}out_01_spanet_prediction_ATLAS_4jets_5global_ptreg_cos_sin_phi.h5",
    # "4_jets_5global_ptreg_cos_sin_phi": f"{spanet_dir}out_01_spanet_prediction_4jets_5global_ptreg_cos_sin_phi.h5",
    #
    # "5_jets_ATLAS_ptreg_allklambda_train_klinput_newkl_oldCuts_newCutsEval": f"{spanet_dir}spanet_prediction_oc_kl3p5_on_nc.h5",
    # "5_jets_ATLAS_ptreg_allklambda_train_noklinput_newkl_oldCuts_newCutsEval": f"{spanet_dir}spanet_prediction_oc_kl3p5_noklinp_nc.h5",
    # "5_jets_ATLAS_ptreg_sm_train_allklambda_eval_noklinput_newkl_oldCuts_newCutsEval": f"{spanet_dir}spanet_prediction_sm_on_nc.h5",
    # "5_jets_ATLAS_ptreg_allklambda_train_noklinput_newkl_newCuts_newCutsEval": f"{spanet_dir}spanet_prediction_nc_noklinput_on_nc.h5",  # doesnt exist
    #
    # 2b data samples
    #
    # "4_jets_data_ATLAS_ptreg_5train": f"{spanet_dir}out_spanet_prediction_data_ev4jets_training5jet_ptreg_ATLAS.h5",
    # "4_jets_data_ATLAS_ptreg_5train": f"{spanet_dir}out_spanet_prediction_data_ev5jets_training5jet_ptreg_ATLAS.h5",
    # "4_jets_data_ATLAS_5global_ptreg": f"{spanet_dir}out_spanet_prediction_data_4jets_5global_ptreg_ATLAS.h5",
    # "5_jets_data_ATLAS_ptreg_5train": f"{spanet_dir}out_spanet_prediction_data_ev5jets_training5jet_ptreg_ATLAS.h5",
    # "5_jets_data_ATLAS_ptreg_5train_newlr_SMtrain_oldCuts_oldCutsEval": f"{spanet_dir}spanet_prediction_sm_on_data_oc.h5",
    # "5_jets_data_ATLAS_ptreg_5train_allklambda_klinput_oldCuts_newCutsEval": f"{spanet_dir}spanet_prediction_nc_on_data_oc.h5",
    # "5_jets_data_ATLAS_ptreg_5train_allklambda_newCuts_newCutsEval_FullyMatched": f"{spanet_dir}spanet_prediction_nc_noklinp_fm_on_data.h5",
    # "5_jets_data_ATLAS_ptreg_5train_allklambda_newCuts_oldCutsEval": f"{spanet_dir}spanet_prediction_nc_on_data_oc.h5",
    #
    # "5_jets_data_ATLAS_ptreg_5train_newlr_SMtrain_oldCuts_newCutsEval": f"{spanet_dir}spanet_prediction_sm_oc_on_data_nc.h5",
    # "5_jets_data_ATLAS_ptreg_5train_newlr_SMtrain_newCuts_newCutsEval": f"{spanet_dir}spanet_prediction_sm_nc_on_data_nc.h5",
    # "5_jets_data_ATLAS_ptreg_5train_allklambda_noklinput_oldCuts_newCutsEval": f"{spanet_dir}spanet_prediction_oc_kl3p5_noklinp_data_nc.h5",
    # "5_jets_data_ATLAS_ptreg_5train_allklambda_noklinput_newCuts_newCutsEval": f"{spanet_dir}spanet_prediction_nc_noklinp_on_data.h5",
}


# true_dir = "/eos/home-r/ramellar/out_prediction_files/true_files/"
# true_dir = "/afs/cern.ch/user/m/mmalucch/public/out_prediction_files/true_files/"
true_dir = "/eos/home-m/mmalucch/spanet_inputs/out_prediction_files/true_files/"

print(
    "WARNING: do not comment the items of this dictionary",
    " if you add a new true file you have to update the efficiency_functions.check_names",
    " and add a new if statement in the function",
)
true_dict = {
    "4 jets": f"{true_dir}output_JetGoodHiggs_test.h5",
    "5 jets": f"{true_dir}output_JetGood_test.h5",
    "5_jets_btag_presel": f"{true_dir}output_JetGood_btag_presel_test.h5",
    "4_jets_klambda0": f"{true_dir}kl0_output_JetGoodHiggs_test.h5",
    "4_jets_klambda2p45": f"{true_dir}kl2p45_output_JetGoodHiggs_test.h5",
    "4_jets_klambda5": f"{true_dir}kl5_output_JetGoodHiggs_test.h5",
    "5_jets_klambda0": f"{true_dir}kl0_output_JetGood_test.h5",
    "5_jets_klambda2p45": f"{true_dir}kl2p45_output_JetGood_test.h5",
    "5_jets_klambda5": f"{true_dir}kl5_output_JetGood_test.h5",
    "4_jets_data": f"{spanet_dir}out_spanet_prediction_data_ev4jets_training5jet_ptreg_ATLAS.h5",
    "5_jets_data": f"{spanet_dir}out_spanet_prediction_data_ev5jets_training5jet_ptreg_ATLAS.h5",
    "5_jets_data_oldCuts": f"{spanet_dir}spanet_prediction_sm_on_data_oc.h5",
    "5_jets_data_newCuts": f"{spanet_dir}spanet_prediction_nc_noklinp_on_data.h5",
    "4_jets_allklambda": f"{true_dir}output_JetGood_test_allkl_new_kl_newcuts.h5",  # output_JetGoodHiggs_allkl_test
    "5_jets_allklambda": f"{true_dir}output_JetGood_test_allkl_new_kl_newcuts.h5",  # output_JetGood_allkl_test
    "5_jets_allklambda_newkl_oldCuts": f"{true_dir}output_JetGood_test_allkl_new_kl_oldcuts.h5",  # "/work/mmalucch/out_hh4b/out_spanet/output_JetGood_test.h5",
    "5_jets_allklambda_newkl_newCuts": f"{true_dir}output_JetGood_test_allkl_new_kl_newcuts.h5",  # "/work/mmalucch/out_hh4b/out_spanet/output_JetGood_test.h5",
    "4_jets_allklambda_newkl_newCuts": f"{true_dir}output_JetGoodHiggs_test_allkl_new_kl_newcuts.h5",  # "/work/mmalucch/out_hh4b/out_spanet/output_JetGood_test.h5",
}


names_dict = {
    "total_diff_eff_spanet": "Total Pairing Efficiency",
    "diff_eff_spanet": "Pairing Efficiency",
    "total_diff_eff_mask30": r"Total Efficiency ($\Delta D_{HH} > 30$ GeV)",
    "diff_eff_mask30": r"Efficiency ($\Delta D_{HH} > 30$ GeV)",
    "5_jets_ATLAS_ptreg": "SPANet Lite 5 jets",
    "4_jets_ATLAS_ptreg_5train": "SPANet Lite 5 jets (4 jets eval)",
    "4_jets_5global_ATLAS_ptreg": "SPANet Lite 4 jets",
    "5_jets_data_ATLAS_ptreg_5train": "SPANet Lite 5 jets",
    "4_jets_data_ATLAS_ptreg_5train": "SPANet Lite 5 jets (4 jets eval)",
    "4_jets_data_ATLAS_5global_ptreg": "SPANet Lite 4 jets",
    "5_jets_ATLAS_ptreg_allklambda_train_klinput": r"SPANet Lite 5 jets all $\kappa_{\lambda}$ ($\kappa_{\lambda}$ inputs)",
    "5_jets_ATLAS_ptreg_allklambda_train_klinput_newkl_newCuts": r"SPANet Lite 5 jets new $\kappa_{\lambda}$ ($\kappa_{\lambda}$ inputs)",
    "5_jets_ATLAS_ptreg_allklambda_train": r"SPANet Lite 5 jets all $\kappa_{\lambda}$",
    "5_jets_ATLAS_ptreg_allklambda_eval": "SPANet Lite 5 jets SM",
    # "4_jets_allklambda": "Run 2",
    "eff_fully_matched_allklambda": "Pairing Efficiency",
    "tot_eff_fully_matched_allklambda": "Total Pairing Efficiency",
    "eff_fully_matched_mask30_allklambda": r"Pairing Efficiency ($\Delta D_{HH} > 30$ GeV)",
    "tot_eff_fully_matched_mask30_allklambda": r"Total Pairing Efficiency ($\Delta D_{HH} > 30$ GeV)",
    "5_jets_ATLAS_ptreg_allklambda_train_klinput_newkl_oldCuts_newCutsEval": r"SPANet - $\kappa_{\lambda}$ ($\kappa_{\lambda}$ inputs) - Tight Selection",
    "5_jets_ATLAS_ptreg_allklambda_train_noklinput_newkl_oldCuts_newCutsEval": r"SPANet - $\kappa_{\lambda}$ - Tight Selection",
    "5_jets_ATLAS_ptreg_sm_train_allklambda_eval_noklinput_newkl_oldCuts_newCutsEval": "SPANet - SM - Tight Selection",
    "5_jets_ATLAS_ptreg_allklambda_train_noklinput_newkl_newCuts_newCutsEval": r"SPANet - $\kappa_{\lambda}$ - Loose Selection",
    "5_jets_data_ATLAS_ptreg_5train_allklambda_noklinput_oldCuts_newCutsEval": r"SPANet - $\kappa_{\lambda}$ - Tight Selection",
    "5_jets_data_ATLAS_ptreg_5train_allklambda_noklinput_newCuts_newCutsEval": r"SPANet - $\kappa_{\lambda}$ - Loose Selection",
    "5_jets_allklambda_newkl_newCuts": "$D_{HH}$-method",
    "4_jets_allklambda_newkl_newCuts": "$D_{HH}$-method",
}


color_dict = {
    # "5_jets_ATLAS_ptreg_allklambda_train_klinput_newkl_oldCuts_newCutsEval": "tab:blue",
    # "5_jets_ATLAS_ptreg_allklambda_train_noklinput_newkl_oldCuts_newCutsEval": "tab:orange",
    # "5_jets_ATLAS_ptreg_sm_train_allklambda_eval_noklinput_newkl_oldCuts_newCutsEval": "tab:green",
    # "5_jets_ATLAS_ptreg_allklambda_train_noklinput_newkl_newCuts_newCutsEval": "purple",
    "5_jets_data_ATLAS_ptreg_5train_allklambda_noklinput_oldCuts_newCutsEval": "deepskyblue",
    "5_jets_data_ATLAS_ptreg_5train_allklambda_noklinput_newCuts_newCutsEval": "coral",
    "5_jets_allklambda_newkl_newCuts": "yellowgreen",
    "4_jets_allklambda_newkl_newCuts": "yellowgreen",
    "5_jets_ATLAS_ptreg_allklambda_train_noklinput_newkl_newCuts_newCutsEval": "coral",
    "5_jets_ATLAS_ptreg_allklambda_train_noklinput_newkl_oldCuts_newCutsEval": "deepskyblue",
    "5_jets_ATLAS_ptreg_allklambda_train_klinput_newkl_oldCuts_newCutsEval": "darkorange",
    "5_jets_ATLAS_ptreg_sm_train_allklambda_eval_noklinput_newkl_oldCuts_newCutsEval": "deeppink",
}
