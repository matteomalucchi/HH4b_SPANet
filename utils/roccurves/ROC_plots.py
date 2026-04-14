"""Generate ROC curves to compare performance of different classifiers."""

import argparse
import logging
import os
import sys
import h5py
import vector
from hist import Hist
from sklearn.metrics import (
    auc,
    roc_curve,
    precision_recall_curve,
    average_precision_score,
)
import numpy as np

vector.register_numba()
vector.register_awkward()

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import helpers
from utils_configs.plot.HEPPlotter import HEPPlotter


parser = argparse.ArgumentParser()
parser.add_argument("-l", "--title", type=str, default="", help="Title of the plot")
parser.add_argument(
    "-pd",
    "--plot-dir",
    default="./ROC_plots",
    help="Directory to save the plots",
)
parser.add_argument(
    "-cut",
    "--fpr-cutoff",
    default=1e-2,
    help="In zoomed version, cutoff in fpr for AUC calculation",
)
parser.add_argument(
    "-nw",
    "--no-weights",
    action="store_true",
    default=False,
    help="Compute the ROC with weights",
)
parser.add_argument(
    "-r",
    "--region",
    default="inclusive",
    help="define evaluation region. If 'inclusive' no cuts are applied",
)
parser.add_argument(
    "-conf",
    "--configuration",
    default=None,
    help="Configuration with the models to consider",
)
args = parser.parse_args()


os.makedirs(args.plot_dir, exist_ok=True)
helpers.setup_logging(args.plot_dir)
logger = logging.getLogger(__name__)


if args.configuration:
    config = helpers.import_module_from_path(args.configuration)
    logger.info(f"Imported configuration: {config}")
    spanet_dict = config.spanet_dict
    true_dict = config.true_dict
    roc_dict = config.roc_dict
else:
    # from efficiency_configuration_cutscomparison import run2_dataset_DATA, run2_dataset_MC, spanet_dict, true_dict
    from roc_configuration import (
        spanet_dict,
        true_dict,
        roc_dict,
    )


def my_roc_auc(
    classes: np.ndarray, predictions: np.ndarray, sample_weight: np.ndarray = None
) -> float:
    """
    Calculating ROC AUC score as the probability of correct ordering
    """
    # based on https://github.com/SiLiKhon/my_roc_auc/blob/master/my_roc_auc.py

    if sample_weight is None:
        sample_weight = np.ones_like(predictions)

    assert len(classes) == len(predictions) == len(sample_weight)
    assert classes.ndim == predictions.ndim == sample_weight.ndim == 1
    class0, class1 = sorted(np.unique(classes))

    data = np.empty(
        shape=len(classes),
        dtype=[
            ("c", classes.dtype),
            ("p", predictions.dtype),
            ("w", sample_weight.dtype),
        ],
    )
    data["c"], data["p"], data["w"] = classes, predictions, sample_weight

    data = data[np.argsort(data["c"])]
    data = data[
        np.argsort(data["p"], kind="mergesort")
    ]  # here we're relying on stability as we need class orders preserved

    correction = 0.0
    # mask1 - bool mask to highlight collision areas
    # mask2 - bool mask with collision areas' start points
    mask1 = np.empty(len(data), dtype=bool)
    mask2 = np.empty(len(data), dtype=bool)
    mask1[0] = mask2[-1] = False
    mask1[1:] = data["p"][1:] == data["p"][:-1]
    if mask1.any():
        mask2[:-1] = ~mask1[:-1] & mask1[1:]
        mask1[:-1] |= mask1[1:]
        (ids,) = mask2.nonzero()
        correction = (
            sum(
                [
                    ((dsplit["c"] == class0) * dsplit["w"] * msplit).sum()
                    * ((dsplit["c"] == class1) * dsplit["w"] * msplit).sum()
                    for dsplit, msplit in zip(np.split(data, ids), np.split(mask1, ids))
                ]
            )
            * 0.5
        )

    weights_0 = data["w"] * (data["c"] == class0)
    weights_1 = data["w"] * (data["c"] == class1)
    cumsum_0 = weights_0.cumsum()

    return ((cumsum_0 * weights_1).sum() - correction) / (
        weights_1.sum() * cumsum_0[-1]
    )


def roc_curve_compare_weights(class_dict, roc_values_dict, plot_dir, fpr_cutoff, no_weights, kl, roc_info_dict):
    """Plot precision/recall curve from a dictionary fed into this function."""

    kl_string = kl if type(kl) == str else f"{kl:.2f}"
    kl_tag = kl_string.replace("-", "m").replace(".", "p")
    logger.info(f"Plotting roc curves for kl = {kl_string} ...")
    
    assert 1e-6 < fpr_cutoff < 1e-1

    series = {}
    
    for model_name, sub_dict in class_dict.items():
        kls = sub_dict["kls"]
        if kl == "all":
            mask_kl = np.ones_like(kls, dtype=bool)
        elif np.any(kls == float(kl)):
            mask_kl = (kls == float(kl)) | (kls == 9999.)  | (sub_dict["true_class"]==0)
        else:
            continue
        

        spanet_class = sub_dict["spanet_class"][mask_kl]
        true_class = sub_dict["true_class"][mask_kl]
        weights = sub_dict["weights"][mask_kl]

        if no_weights:
            fpr, tpr, threshold = roc_curve(true_class, spanet_class)
            auc_score = my_roc_auc(true_class, spanet_class)
        else:
            fpr, tpr, threshold = roc_curve(
                true_class, spanet_class, sample_weight=weights
            )
            auc_score = my_roc_auc(true_class, spanet_class, weights)

        # compute the auc for the zoomed roc curve
        # fpr_zoom = fpr[fpr <= fpr_cutoff]
        # tpr_zoom = tpr[: len(fpr_zoom)]
        # auc_score_zoom = auc(fpr_zoom, tpr_zoom)
        # auc_score = auc(fpr, tpr)

        name = f"{sub_dict['label']} | kl={kl_string} | AUC={auc_score:.3f}"

        series[name] = {
            "data": {"x": [tpr, None], "y": [fpr, None]},
            "style": {"color": sub_dict["color"], "linestyle": "-", "markersize": 0},
        }
        roc_info_dict[f"tpr_kl_{kl_string}_{model_name}"]=tpr
        roc_info_dict[f"fpr_kl_{kl_string}_{model_name}"]=fpr
    
    for model_name, sub_dict in roc_values_dict.items():
        if kl not in sub_dict:
            continue
        
        tpr_fpr_dict = sub_dict[kl]
        
        tpr = tpr_fpr_dict[f"tpr_kl_{kl}"]
        fpr = tpr_fpr_dict[f"fpr_kl_{kl}"]

        name = f"{tpr_fpr_dict['label']} | kl={kl_string}"

        series[name] = {
            "data": {"x": [tpr, None], "y": [fpr, None]},
            "style": {"color": tpr_fpr_dict["color"], "linestyle": "-", "markersize": 0},
        }
    
    if series != {}:
        os.makedirs(f"{plot_dir}/roc_curves/kl_{kl_tag}", exist_ok=True)
        for log in [False, True]:
            for zoom in [True, False]:
                (
                    HEPPlotter("CMS")
                    .set_output(
                        f"{plot_dir}/roc_curves/kl_{kl_tag}/ROC_curve_kl_{kl_tag}{'_zoomed' if zoom else ''}{'_log' if log else ''}"
                    )
                    .set_data(series, plot_type="graph")
                    .set_labels(
                        xlabel="True positive rate",
                        ylabel="False positive rate",
                    )
                    .set_options(
                        legend_font_size=16,
                        xlim_left_value=0,
                        xlim_right_value=0.4 if zoom else 0,
                        ylim_bottom_value=1e-6,
                        ylim_top_value=1e-1 if zoom else 1,
                        y_log=True if log else False,
                        legend=True,
                        grid=True,
                    )
                    .set_plot_config(
                        cmstext="Private"
                    )
                    .run()
                )


def precision_recall_curve_function(class_dict, plot_dir, no_weights, kl):
    """Plot precision/recall curve from a dictionary fed into this function."""
    
    kl_string = kl if type(kl) == str else f"{kl:.2f}"
    kl_tag = kl_string.replace("-", "m").replace(".", "p")
    logger.info(f"Plotting precision-recall curves for kl = {kl_string} ...")

    series = {}

    for model_name, sub_dict in class_dict.items():
        kls = sub_dict["kls"]
        if kl == "all":
            mask_kl = np.ones_like(kls, dtype=bool)
        elif np.any(kls == float(kl)):
            mask_kl = (kls == float(kl)) | (kls == 9999.)  | (sub_dict["true_class"]==0)
        else:
            continue

        spanet_class = sub_dict["spanet_class"][mask_kl]
        true_class = sub_dict["true_class"][mask_kl]
        weights = sub_dict["weights"][mask_kl]

        if no_weights:
            precision, recall, threshold = precision_recall_curve(
                true_class, spanet_class
            )
            ap_score = average_precision_score(true_class, spanet_class)

        else:
            precision, recall, threshold = precision_recall_curve(
                true_class, spanet_class, sample_weight=weights
            )
            ap_score = average_precision_score(
                true_class, spanet_class, sample_weight=weights
            )

        label = f"{sub_dict['label']} | kl={kl_string} | AP={ap_score:.3f}"

        series[label] = {
            "data": {"x": [recall, None], "y": [precision, None]},
            "style": {"color": sub_dict["color"], "linestyle": "-", "markersize": 0},
        }
    
    if series != {}:
        os.makedirs(f"{plot_dir}/precision_recall_curve/kl_{kl_tag}", exist_ok=True)
        for log in [False, True]:
            (
                HEPPlotter("CMS")
                .set_output(
                    f"{plot_dir}/precision_recall_curve/kl_{kl_tag}/precision_recall_curve_kl_{kl_tag}{'_log' if log else ''}"
                )
                .set_data(series, plot_type="graph")
                .set_labels(
                    xlabel="Recall",
                    ylabel="Precision",
                )
                .set_options(
                    legend_font_size=16,
                    xlim_left_value=0,
                    xlim_right_value=1,
                    ylim_bottom_value=1e-6,
                    ylim_top_value=1,
                    y_log=True if log else False,
                    legend=True,
                    grid=True,
                )
                .set_plot_config(
                    cmstext="Private"
                )
                .run()
            )


def signal_background_hist(class_dict, plot_dir, no_weights, kl):
    """Plot background/signal histogram from a dictionary fed into this function."""

    kl_string = kl if type(kl) == str else f"{kl:.2f}"
    kl_tag = kl_string.replace("-", "m").replace(".", "p")
    logger.info(f"Plotting score histogram for kl = {kl_string}...")
    
    series_all_models = {}

    for model_name, sub_dict in class_dict.items():
        kls = sub_dict["kls"]
        if kl == "all":
            mask_kl = np.ones_like(kls, dtype=bool)
        elif np.any(kls == float(kl)):
            mask_kl = (kls == float(kl)) | (kls == 9999.)  | (sub_dict["true_class"]==0)
        else:
            continue

        spanet_class = sub_dict["spanet_class"][mask_kl]
        true_class = sub_dict["true_class"][mask_kl]
        weights = sub_dict["weights"][mask_kl]

        mask_background = true_class == 0

        if no_weights:
            weights_bkg = None
            weights_sig = None
        else:
            weights_bkg = weights[mask_background]
            weights_sig = weights[~mask_background]

        hist_bkg = Hist.new.Regular(
            50, 0, 1, name="SPANet Classification Score", flow=False
        ).Weight()
        hist_bkg.fill(spanet_class[mask_background], weight=weights_bkg / (weights_bkg.sum() * hist_bkg.axes[0].widths[0]) if weights_bkg is not None else None)

        hist_sig = Hist.new.Regular(
            50, 0, 1, name="SPANet Classification Score", flow=False
        ).Weight()
        hist_sig.fill(spanet_class[~mask_background], weight=weights_sig / (weights_sig.sum() * hist_sig.axes[0].widths[0]) if weights_sig is not None else None)

        series = {
            f"Background - {sub_dict['label']}": {
                "data": hist_bkg,
                "style": {
                    "histtype": "step",
                    "alpha": 0.5,
                    "weights": weights_bkg,
                },
            },
            f"Signal (kl={kl_string}) - {sub_dict['label']}": {
                "data": hist_sig,
                "style": {
                    "histtype": "step",
                    "alpha": 0.5,
                    "weights": weights_sig,
                },
            },
        }

        series_all_models.update(series)
        
        if series != {}:
            os.makedirs(f"{plot_dir}/background_signal_hist/{model_name}/kl_{kl_tag}", exist_ok=True)
            for log in [False, True]:
                (
                    HEPPlotter("CMS")
                    .set_output(
                        f"{plot_dir}/background_signal_hist/{model_name}/kl_{kl_tag}/background_signal_hist_{model_name}_kl_{kl_tag}{'_log' if log else ''}"
                    )
                    .set_data(series)
                    .set_labels(
                        xlabel="SPANet Classification Score",
                        ylabel="Classification Probability Density",
                    )
                    .set_options(
                        set_ylim=False,
                        legend_font_size="16",
                        y_log=True if log else False,
                        legend=True,
                        grid=True,
                    )
                    .set_plot_config(
                        cmstext="Private"
                    )
                    .run()
                )
    
    if len(series_all_models) > 2: # to avoid plotting the combined plot with all the models if there's only one model
        os.makedirs(f"{plot_dir}/background_signal_hist/models_all/kl_{kl_tag}", exist_ok=True)
        for log in [False, True]:
            (
                HEPPlotter("CMS")
                .set_output(
                    f"{plot_dir}/background_signal_hist/models_all/kl_{kl_tag}/background_signal_hist_models_all_kl_{kl_tag}{'_log' if log else ''}"
                )
                .set_data(series_all_models)
                .set_labels(
                    xlabel="SPANet Classification Score",
                    ylabel="Classification Probability Density",
                )
                .set_options(
                    set_ylim=False,
                    legend_font_size=16,
                    y_log=True if log else False,
                    legend=True,
                    grid=True,
                )
                .set_plot_config(
                    cmstext="Private"
                )
                .run()
            )


def main():
    class_dict = {}
    roc_values_dict = {}

    for model_name, model_dict in spanet_dict.items():
        logger.info(f"Loading new file {model_name}")
        for key, val in model_dict.items():
            logger.info(f"{key}: {val}")

        spanetfile = h5py.File(model_dict["file"], "r")
        truefile = h5py.File(true_dict[model_dict["true"]]["name"], "r")

        model_dict.pop("file")
        model_dict.pop("true")

        mask_region_spanet = helpers.get_region_mask(args.region, spanetfile, True)
        
        spanet_class = spanetfile["CLASSIFICATIONS"]["EVENT"]["class"][:, 1][()][mask_region_spanet]
        true_class = truefile["CLASSIFICATIONS"]["EVENT"]["class"][()][mask_region_spanet]
        weights = truefile["WEIGHTS"]["weight"][()][mask_region_spanet]
        
        try:
            kls = spanetfile["INPUTS"]["Event"]["kl"][()][mask_region_spanet]            
        except KeyError:
            kls= np.ones_like(weights) * 9999.
        
        class_dict[model_name] = {
            "spanet_class": spanet_class,
            "true_class": true_class,
            "weights": weights,
            "kls": kls,
        } | model_dict
    
    for model_name, model_dict in roc_dict.items():
        logger.info(f"Loading new file {model_name}")
        for key, val in model_dict.items():
            logger.info(f"{key}: {val}")
        
        np_arrays=np.load(model_dict["file"])
        roc_values_dict[model_name] = {}
        model_dict.pop("file")
        
        for var_name in  np_arrays.keys():
            kl=var_name.split("kl_")[-1]
            if kl not in roc_values_dict[model_name]:
                roc_values_dict[model_name][kl]={}
            
            roc_values_dict[model_name][kl] |= {
                var_name: np_arrays[var_name],
            } | model_dict  

    kls_signal=list(np.unique(kls[true_class==1]))
    print(f"Separating kl for signal", kls_signal)
    roc_info_dict={}
    for kl in ["all"]+kls_signal:
        roc_curve_compare_weights(
            class_dict, roc_values_dict, args.plot_dir, args.fpr_cutoff, args.no_weights, kl, roc_info_dict
        )
        precision_recall_curve_function(class_dict, args.plot_dir, args.no_weights, kl)
        signal_background_hist(class_dict, args.plot_dir, args.no_weights, kl)

    # save the fpr and tpr in a npz file
    np.savez(
        f"{args.plot_dir}/roc_curves/tpr_fpr_all_kl_all_models.npz",
        **roc_info_dict
    )
    
if __name__ == "__main__":
    logger.debug(spanet_dict)
    logger.debug(true_dict)
    main()