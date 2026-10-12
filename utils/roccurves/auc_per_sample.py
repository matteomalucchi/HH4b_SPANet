#!/usr/bin/env python3
"""
Per-sample AUC of a ggF/VBF SPANet classifier.

For every value of INPUTS/Event/kl in the signal class (for VBF samples this
field holds C2V, so each value is one VBF coupling sample) the script computes
the unweighted AUC of that sample against the background class restricted to
--bkg-kl (default kl=1, i.e. SM ggF), plus the inclusive AUC (all signal vs all
background). Several prediction files of the same test file can be compared
side by side (e.g. a model trained on 2024 vs one trained on 2022).

The true class and the kl labels are read from the test file (the SPANet input
h5); the score is CLASSIFICATIONS/EVENT/class[:, 1] of each prediction file.
The prediction files must have the same event order as the test file (checked
via INPUTS/Event/event).

Usage:
    python3 utils/roccurves/auc_per_sample.py -t <test.h5> \
        -p <predict_A.h5> <predict_B.h5> -l "train24" "train22" [--bkg-kl 1] [--weighted]

Options:
    -t/--test-file   SPANet input h5 used for the prediction (truth + kl + weights)
    -p/--predict     one or more prediction h5 files (output of spanet.predict)
    -l/--labels      labels for the prediction files (default: file names)
    --bkg-kl         kl value of the background class used for the per-sample AUCs
                     (default 1.0; pass "all" to use the full background class)
    --sig-class      index of the signal class (default 1)
    --weighted       use WEIGHTS/weight of the test file in the AUC
"""
import argparse
import h5py
import numpy as np


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


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("-t", "--test-file", required=True)
    p.add_argument("-p", "--predict", nargs="+", required=True)
    p.add_argument("-l", "--labels", nargs="+", default=None)
    p.add_argument("--bkg-kl", default="1.0")
    p.add_argument("--sig-class", type=int, default=1)
    p.add_argument("--weighted", action="store_true")
    a = p.parse_args()
    labels = a.labels or [f.split("/")[-1][:20] for f in a.predict]
    assert len(labels) == len(a.predict), "one label per prediction file"

    with h5py.File(a.test_file) as h:
        cls = h["CLASSIFICATIONS/EVENT/class"][:]
        kl = h["INPUTS/Event/kl"][:]
        ev = h["INPUTS/Event/event"][:]
        w = h["WEIGHTS/weight"][:] if a.weighted else np.ones(len(cls))

    scores = []
    for f in a.predict:
        with h5py.File(f) as h:
            if not np.array_equal(h["INPUTS/Event/event"][:], ev):
                raise RuntimeError(f"event order of {f} differs from the test file")
            scores.append(h["CLASSIFICATIONS/EVENT/class"][:, a.sig_class])

    sig = cls == a.sig_class
    bkg_all = ~sig
    bkg = bkg_all if a.bkg_kl == "all" else bkg_all & np.isclose(kl, float(a.bkg_kl))
    print(f"background: kl={a.bkg_kl}, N={bkg.sum()}  ({'weighted' if a.weighted else 'unweighted'} AUC)")
    print(f"{'sig kl':>8} {'N':>8} " + " ".join(f"{l:>12}" for l in labels))
    for k in np.unique(kl[sig]):
        m = sig & np.isclose(kl, k)
        vals = [auc(s[m], s[bkg], w[m], w[bkg]) for s in scores]
        print(f"{k:8.3f} {m.sum():8d} " + " ".join(f"{v:12.4f}" for v in vals))
    vals = [auc(s[sig], s[bkg_all], w[sig], w[bkg_all]) for s in scores]
    print(f"{'all sig vs all bkg':>17} " + " ".join(f"{v:12.4f}" for v in vals))


if __name__ == "__main__":
    main()
