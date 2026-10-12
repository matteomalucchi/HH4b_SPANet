#!/usr/bin/env python3
"""
Plot the input variables of a SPANet h5 file separately for every kl sample
and every class.

Every dataset under INPUTS/ is plotted:
  * 1-D datasets (global inputs, e.g. INPUTS/Event/mjj..., INPUTS/HH/mass)
    give one plot per class;
  * 2-D datasets (sequential inputs, e.g. INPUTS/JetVBF/pt with shape
    (N, n_jets)) give one plot per class and per object index (jet 0, jet 1,
    ...), using the MASK of the collection to drop padded entries; with
    --flatten-sequential all the (unmasked) objects are put in a single
    histogram instead.
Entries equal to one of the --padding-values (default 9999 and -999, the
padding values of the h5 conversion) are dropped in all cases.

The samples are distinguished by the event variable INPUTS/Event/kl (for the
VBF samples this field holds C2V) and by the class stored in
CLASSIFICATIONS/EVENT/class.  Each plot (made with HEPPlotter) contains one
class, with one histogram per kl value, normalized to unit area, so that the
shapes of the different samples can be compared.  Under/overflows are added
to the first/last bin.  With --weighted the histograms are filled with
WEIGHTS/weight.

Output: <output-dir>/<class>/<group>/<variable>[_<index>].png  (+ .pdf with --pdf)

Usage:
    python3 utils/dataset/plot_h5_inputs_per_kl.py -i <file.h5> -o <output_dir>
        [--class-names 0:ggF 1:VBF] [--param-names 0:kl 1:C2V] [--weighted]
        [--vars <regex> ...] [--max-objects 4] [--flatten-sequential]
        [--max-events N] [--log] [--pdf]

Options:
    -i/--input            input SPANet h5 file (train or test)
    -o/--output-dir       directory where the plots are saved
    --class-names         mapping class index -> name, as idx:name
                          (default 0:ggF 1:VBF, the convention of the ggF/VBF h5 files)
    --param-names         mapping class index -> name of the coupling stored in
                          INPUTS/Event/kl, used in the legend (default 0:kl 1:C2V)
    --weighted            fill the histograms with WEIGHTS/weight
    --vars                only plot variables whose "<group>/<name>" matches one of
                          these regular expressions (default: all)
    --skip                regular expressions of variables to skip
                          (default: MASK, kl, event, era, year)
    --padding-values      values treated as padding and dropped (default 9999 -999)
    --max-objects         maximum number of objects plotted per sequential collection
                          (default: all)
    --flatten-sequential  one histogram with all the objects of a sequential collection
                          instead of one per object index
    --max-events          read only the first N events (faster on EOS)
    --bins                number of bins (default 50)
    --log                 logarithmic y axis
    --pdf                 also save the plots as pdf
"""
import argparse
import os
import re

import h5py
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import mplhep as hep  # noqa: E402
import numpy as np  # noqa: E402
from hist import Hist  # noqa: E402
from utils_configs.plot.HEPPlotter import HEPPlotter  # noqa: E402

DEFAULT_SKIP = [r"/MASK$", r"^Event/kl$", r"^Event/event$", r"^Event/era$", r"^Event/year$"]
CMS_COLORS = [cycle["color"] for cycle in hep.style.CMS["axes.prop_cycle"]]


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("-i", "--input", required=True)
    p.add_argument("-o", "--output-dir", required=True)
    p.add_argument("--class-names", nargs="+", default=["0:ggF", "1:VBF"])
    p.add_argument("--param-names", nargs="+", default=["0:kl", "1:C2V"])
    p.add_argument("--weighted", action="store_true")
    p.add_argument("--vars", nargs="+", default=None)
    p.add_argument("--skip", nargs="+", default=DEFAULT_SKIP)
    p.add_argument("--padding-values", nargs="*", type=float, default=[9999.0, -999.0])
    p.add_argument("--max-objects", type=int, default=None)
    p.add_argument("--flatten-sequential", action="store_true")
    p.add_argument("--max-events", type=int, default=None)
    p.add_argument("--bins", type=int, default=50)
    p.add_argument("--log", action="store_true")
    p.add_argument("--pdf", action="store_true")
    return p.parse_args()


def parse_mapping(items):
    """["0:ggF", "1:VBF"] -> {0: "ggF", 1: "VBF"}"""
    return {int(s.split(":")[0]): s.split(":", 1)[1] for s in items}


def binning(values, nbins):
    """Common binning for all the samples: integer-like variables get unit bins,
    otherwise the 0.5-99.5 percentile range."""
    if len(values) == 0:
        return None
    uniq = np.unique(values)
    if len(uniq) <= 30 and np.allclose(uniq, np.round(uniq)):
        return np.arange(uniq.min() - 0.5, uniq.max() + 1.5, 1.0)
    lo, hi = np.percentile(values, [0.5, 99.5])
    if lo == hi:
        lo, hi = lo - 0.5, hi + 0.5
    return np.linspace(lo, hi, nbins + 1)


def sample_label(param, k, padding_values):
    if any(np.isclose(k, pv) for pv in padding_values):
        return "no coupling"
    return f"{param}={k:g}"


def plot_variable(name, values, valid, cls, kl, w, class_names, param_names, kl_colors, args):
    """values/valid/cls/kl/w are 1-D arrays of the same length.
    Make one plot per class, with one normalized histogram per kl value."""
    sel = valid & np.isfinite(values)
    for pv in args.padding_values:
        sel &= ~np.isclose(values, pv)
    bins = binning(values[sel], args.bins)
    if bins is None:
        return 0

    n_plots = 0
    for c in sorted(class_names):
        mc = sel & (cls == c)
        if not mc.any():
            continue
        series = {}
        max_frac, min_frac = 0.0, np.inf
        for k in np.unique(kl[mc]):
            m = mc & np.isclose(kl, k)
            if w[m].sum() <= 0:
                continue
            h = Hist.new.Var(bins, name=name, flow=False).Weight()
            # put under/overflows in the first/last bin
            h.fill(np.clip(values[m], bins[0], bins[-1]), weight=w[m])
            frac = h.values() / h.values().sum()
            max_frac = max(max_frac, frac.max())
            if np.any(frac > 0):
                min_frac = min(min_frac, frac[frac > 0].min())
            label = f"{sample_label(param_names.get(c, 'kl'), k, args.padding_values)} (N={m.sum()})"
            series[label] = {
                "data": h,
                "style": {"color": kl_colors[k], "histtype": "step", "linewidth": 2, "plot_errors": False},
            }
        if not series:
            continue

        out = os.path.join(args.output_dir, class_names[c], name)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        options = dict(normalize_1d_histo=True, legend=True, legend_loc="upper right", grid=True)
        if args.log:
            options.update(y_log=True, ylim_top_value=max_frac * 1e2, ylim_bottom_value=min_frac * 0.5)
        (
            HEPPlotter("CMS")
            .set_output(out)
            .set_data(series, plot_type="1d")
            .set_labels(xlabel=name, ylabel="a.u. (unit area)")
            .set_options(**options)
            .set_plot_config(cmstext="Private", data_formats=["png", "pdf"] if args.pdf else ["png"])
            .add_annotation(0.03, 0.97, class_names[c], ha="left", va="top", fontsize=18)
            .run()
        )
        n_plots += 1
    return n_plots


def main():
    args = parse_args()
    class_names = parse_mapping(args.class_names)
    param_names = parse_mapping(args.param_names)
    sl = slice(None) if args.max_events is None else slice(0, args.max_events)

    with h5py.File(args.input, "r") as f:
        cls = f["CLASSIFICATIONS/EVENT/class"][sl]
        kl = f["INPUTS/Event/kl"][sl]
        w = f["WEIGHTS/weight"][sl] if args.weighted else np.ones(len(cls))
        unknown = sorted(set(np.unique(cls).tolist()) - set(class_names))
        for c in unknown:
            class_names[int(c)] = f"class {int(c)}"
        if unknown:
            print(f"warning: classes {unknown} not in --class-names, using generic names")

        # summary of the samples
        print(f"{'class':>8} {'kl':>8} {'N':>9} {'sumw':>12}")
        for c in sorted(class_names):
            for k in np.unique(kl[cls == c]):
                m = (cls == c) & np.isclose(kl, k)
                print(f"{class_names[c]:>8} {k:8.3f} {m.sum():9d} {w[m].sum():12.4g}")

        # same colour for the same kl value in all the plots
        all_kl = np.unique(kl)
        if len(all_kl) <= len(CMS_COLORS):
            colors = CMS_COLORS
        else:
            cmap = plt.get_cmap("tab20")
            colors = [cmap(i % cmap.N) for i in range(len(all_kl))]
        kl_colors = {k: colors[i] for i, k in enumerate(all_kl)}

        datasets = []
        f["INPUTS"].visititems(lambda n, o: datasets.append(n) if isinstance(o, h5py.Dataset) else None)

        n_plots = 0
        for name in sorted(datasets):
            if any(re.search(s, name) for s in args.skip):
                continue
            if args.vars and not any(re.search(v, name) for v in args.vars):
                continue
            data = f["INPUTS"][name][sl]
            common = (class_names, param_names, kl_colors, args)
            if data.ndim == 1:
                n_plots += plot_variable(name, data.astype(float), np.ones(len(data), bool), cls, kl, w, *common)
            elif data.ndim == 2:
                group = name.rsplit("/", 1)[0]
                mask_name = f"{group}/MASK"
                mask = f["INPUTS"][mask_name][sl].astype(bool) if mask_name in f["INPUTS"] else np.ones(data.shape, bool)
                n_obj = data.shape[1] if args.max_objects is None else min(args.max_objects, data.shape[1])
                if args.flatten_sequential:
                    rep = lambda a: np.repeat(a, n_obj)  # noqa: E731
                    n_plots += plot_variable(name, data[:, :n_obj].astype(float).ravel(), mask[:, :n_obj].ravel(),
                                             rep(cls), rep(kl), rep(w), *common)
                else:
                    for j in range(n_obj):
                        n_plots += plot_variable(f"{name}_{j}", data[:, j].astype(float), mask[:, j],
                                                 cls, kl, w, *common)
            else:
                print(f"skipping {name}: ndim={data.ndim}")
    print(f"saved {n_plots} plots in {args.output_dir}")


if __name__ == "__main__":
    main()
