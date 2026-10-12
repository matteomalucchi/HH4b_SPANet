#!/usr/bin/env python3
"""
Per-sample AUC of a ggF/VBF SPANet classifier.

For every value of INPUTS/Event/kl in the signal class (for VBF samples this
field holds C2V, so each value is one VBF coupling sample) the script computes
the AUC of that sample against the background class restricted to --bkg-kl
(default kl=1, i.e. SM ggF), plus the inclusive AUC (all signal vs all
background). Several prediction files of the same test file can be compared
side by side (e.g. a model trained on 2024 vs one trained on 2022).

The true class and the kl labels are read from the test file (the SPANet input
h5); the score is CLASSIFICATIONS/EVENT/class[:, --sig-class] of each
prediction file. The prediction files must have the same event order as the
test file: the number of events is always checked, and INPUTS/Event/event is
compared when it is present in both files (spanet.predict copies all the
INPUTS of the test file into the prediction file).

Optionally (--plot-dir) the per-sample AUCs are plotted as a function of the
signal kl (C2V) value, one graph per prediction file.

Usage:
    python3 utils/roccurves/auc_per_sample.py -t <test.h5> \
        -p <predict_A.h5> <predict_B.h5> -l "train24" "train22" [--bkg-kl 1] [--weighted] \
        [--plot-dir <dir>]

Options:
    -t/--test-file   SPANet input h5 used for the prediction (truth + kl + weights)
    -p/--predict     one or more prediction h5 files (output of spanet.predict)
    -l/--labels      labels for the prediction files (default: file names)
    --bkg-kl         kl value of the background class used for the per-sample AUCs
                     (default 1.0; pass "all" to use the full background class)
    --sig-class      index of the signal class (default 1)
    --weighted       use WEIGHTS/weight of the test file in the AUC
    --plot-dir       if given, save the plot of the AUC vs signal kl in this directory
    --xlabel         x-axis label of the plot
"""
import argparse
import os
import sys

import h5py
import mplhep as hep
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils_configs.plot.HEPPlotter import HEPPlotter

CMS_COLORS = [cycle["color"] for cycle in hep.style.CMS["axes.prop_cycle"]]


def auc(s, b, ws=None, wb=None):
    """(Weighted) AUC = P(score_sig > score_bkg), ties counted 1/2."""
    if ws is None:
        ws = np.ones(len(s))
    if wb is None:
        wb = np.ones(len(b))
    order = np.argsort(b)
    b, wb = b[order], wb[order]
    cwb = np.concatenate([[0.0], np.cumsum(wb)])
    lo = np.searchsorted(b, s, side="left")
    hi = np.searchsorted(b, s, side="right")
    below = cwb[lo] + 0.5 * (cwb[hi] - cwb[lo])
    return np.sum(ws * below) / (ws.sum() * wb.sum())


def plot_auc_vs_kl(sig_kls, aucs, aucs_incl, labels, a):
    """Graph of the per-sample AUC vs the signal kl, one series per prediction file."""
    series = {}
    for i, (label, vals, v_incl) in enumerate(zip(labels, aucs, aucs_incl)):
        series[label] = {
            "data": {"x": sig_kls, "y": vals},
            "style": {
                "color": CMS_COLORS[i % len(CMS_COLORS)],
                "fmt": "o",
                "linestyle": "-",
                "markersize": 8,
                "legend_name": f"{label} | incl. AUC={v_incl:.3f}",
            },
        }
    os.makedirs(a.plot_dir, exist_ok=True)
    bkg_string = a.bkg_kl if a.bkg_kl == "all" else f"{float(a.bkg_kl):.2f}"
    (
        HEPPlotter("CMS")
        .set_output(
            os.path.join(a.plot_dir, f"auc_per_sample_bkg_kl_{bkg_string.replace('-', 'm').replace('.', 'p')}")
        )
        .set_data(series, plot_type="graph")
        .set_labels(xlabel=a.xlabel, ylabel="AUC")
        .set_options(legend=True, legend_font_size=16, grid=True, set_ylim=False)
        .set_plot_config(cmstext="Private", data_formats=["png", "pdf"])
        .add_annotation(0.03, 0.97, rf"bkg $\kappa_\lambda$ = {bkg_string}", ha="left", va="top", fontsize=14)
        .add_annotation(
            0.03, 0.91, "weighted" if a.weighted else "unweighted", ha="left", va="top", fontsize=14
        )
        .run()
    )
    print(f"saved AUC plot in {a.plot_dir}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("-t", "--test-file", required=True)
    p.add_argument("-p", "--predict", nargs="+", required=True)
    p.add_argument("-l", "--labels", nargs="+", default=None)
    p.add_argument("--bkg-kl", default="1.0")
    p.add_argument("--sig-class", type=int, default=1)
    p.add_argument("--weighted", action="store_true")
    p.add_argument("--plot-dir", default=None)
    p.add_argument("--xlabel", default=r"Signal sample $\kappa_\lambda$ ($C_{2V}$ for VBF)")
    a = p.parse_args()
    labels = a.labels or [f.split("/")[-1][:20] for f in a.predict]
    if len(labels) != len(a.predict):
        p.error("one label per prediction file")

    with h5py.File(a.test_file, "r") as h:
        cls = h["CLASSIFICATIONS/EVENT/class"][:]
        kl = h["INPUTS/Event/kl"][:]
        ev = h["INPUTS/Event/event"][:] if "INPUTS/Event/event" in h else None
        w = h["WEIGHTS/weight"][:] if a.weighted else np.ones(len(cls))

    scores = []
    for f in a.predict:
        with h5py.File(f, "r") as h:
            score = h["CLASSIFICATIONS/EVENT/class"][:, a.sig_class]
            if len(score) != len(cls):
                raise RuntimeError(f"{f} has {len(score)} events, the test file has {len(cls)}")
            if ev is not None and "INPUTS/Event/event" in h:
                if not np.array_equal(h["INPUTS/Event/event"][:], ev):
                    raise RuntimeError(f"event order of {f} differs from the test file")
            else:
                print(f"warning: INPUTS/Event/event missing, cannot check the event order of {f}")
            scores.append(score)

    sig = cls == a.sig_class
    bkg_all = ~sig
    bkg = bkg_all if a.bkg_kl == "all" else bkg_all & np.isclose(kl, float(a.bkg_kl))
    if not sig.any():
        raise RuntimeError(f"no events of class {a.sig_class} in the test file")
    if not bkg.any():
        raise RuntimeError(
            f"no background events with kl={a.bkg_kl}; available: {np.unique(kl[bkg_all])}"
        )

    print(f"background: kl={a.bkg_kl}, N={bkg.sum()}  ({'weighted' if a.weighted else 'unweighted'} AUC)")
    print(f"{'sig kl':>8} {'N':>8} " + " ".join(f"{l:>12}" for l in labels))
    sig_kls = np.unique(kl[sig])
    aucs = [[] for _ in scores]
    for k in sig_kls:
        m = sig & np.isclose(kl, k)
        vals = [auc(s[m], s[bkg], w[m], w[bkg]) for s in scores]
        for i, v in enumerate(vals):
            aucs[i].append(v)
        print(f"{k:8.3f} {m.sum():8d} " + " ".join(f"{v:12.4f}" for v in vals))
    aucs_incl = [auc(s[sig], s[bkg_all], w[sig], w[bkg_all]) for s in scores]
    print(f"{'all':>8} {sig.sum():8d} " + " ".join(f"{v:12.4f}" for v in aucs_incl)
          + f"   (all signal vs all background, N_bkg={bkg_all.sum()})")

    if a.plot_dir:
        plot_auc_vs_kl(sig_kls, aucs, aucs_incl, labels, a)


if __name__ == "__main__":
    main()
