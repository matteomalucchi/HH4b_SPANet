#!/usr/bin/env python3
"""Plot SPANet training metrics from PyTorch Lightning output.

Reads the metrics.csv saved automatically by PyTorch Lightning alongside
the TensorBoard event files, then produces HEPPlotter-styled plots of all
relevant training quantities.  Each metric gets its own file; training and
validation curves are overlaid on the same plot with solid/dashed lines.

Usage examples
--------------
# Latest version of a single run (auto-detected):
    python plot_training_metrics.py -d /eos/spanet_outputs/my_run

# Specific version directory:
    python plot_training_metrics.py -d /eos/spanet_outputs/my_run/version_3

# All seeds in a run directory overlaid (seed variability study):
    python plot_training_metrics.py -d /eos/spanet_outputs/my_run --all-versions

# Compare two configurations on the same plots:
    python plot_training_metrics.py \\
        -d /eos/run_A /eos/run_B -l "Config A" "Config B"

# Auto-discover multiple models inside a parent directory:
    python plot_training_metrics.py -d /eos/spanet_outputs/

# Save plots in category subfolders (losses/, accuracy/, …):
    python plot_training_metrics.py -d /eos/my_run --subfolders

# Apply smoothing (EMA factor 0–1; same scale as TensorBoard slider):
    python plot_training_metrics.py -d /eos/my_run --smooth 0.9
"""

import argparse
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils_configs.plot.HEPPlotter import HEPPlotter


# ---------------------------------------------------------------------------
# Colour palette  (matches the style used elsewhere in HH4b_SPANet)
# ---------------------------------------------------------------------------
_COLORS = [
    "#1f77b4",  # blue
    "#ff7f0e",  # orange
    "#2ca02c",  # green
    "#d62728",  # red
    "#9467bd",  # purple
    "#8c564b",  # brown
    "#e377c2",  # pink
    "#7f7f7f",  # grey
    "#bcbd22",  # olive
    "#17becf",  # teal
]


# ---------------------------------------------------------------------------
# Directory helpers
# ---------------------------------------------------------------------------

def _version_index(p: Path) -> int:
    m = re.match(r"version_(\d+)$", p.name)
    return int(m.group(1)) if m else -1


def find_version_dirs(base: Path) -> List[Path]:
    """Return sorted version_N subdirs of *base*, or [base] if none exist."""
    if not base.is_dir():
        return []
    vs = [p for p in base.iterdir() if p.is_dir() and re.match(r"version_\d+$", p.name)]
    return sorted(vs, key=_version_index) if vs else [base]


def _is_multi_model_dir(base: Path) -> bool:
    """True when *base* has no direct version_N dirs but its children do.

    This detects the layout::

        parent_dir/
          model_A/version_0/
          model_B/version_0/
    """
    if not base.is_dir():
        return False
    if any(re.match(r"version_\d+$", p.name) for p in base.iterdir() if p.is_dir()):
        return False  # already a single-model dir
    for child in base.iterdir():
        if child.is_dir() and not child.name.startswith("."):
            if any(re.match(r"version_\d+$", p.name) for p in child.iterdir() if p.is_dir()):
                return True
    return False


# ---------------------------------------------------------------------------
# Metric loading
# ---------------------------------------------------------------------------

def _load_from_csv(version_dir: Path) -> Optional[pd.DataFrame]:
    p = version_dir / "metrics.csv"
    if not p.exists():
        return None
    df = pd.read_csv(p)
    return df.loc[:, ~df.columns.str.match(r"^Unnamed")]


def _infer_epochs(df: pd.DataFrame) -> pd.Series:
    """Infer epoch numbers from step values when no explicit epoch column exists.

    Prefers metrics whose names guarantee once-per-epoch logging (validation_*,
    REGRESSION/*, …) as epoch-end markers; falls back to the min-count metric
    otherwise (requiring ≥ 2 data points to ignore stray once-only scalars).
    """
    steps = df["step"].values
    metric_cols = [c for c in df.columns if c != "step"]

    _VAL_PREFIXES = (
        "validation_", "REGRESSION/", "CLASSIFICATION/",
        "Purity/", "jet/", "particle/",
    )
    per_epoch_cols = [c for c in metric_cols if c.startswith(_VAL_PREFIXES)]

    if per_epoch_cols:
        ref_col = max(per_epoch_cols, key=lambda c: df[c].notna().sum())
    else:
        counts = {c: df[c].notna().sum() for c in metric_cols}
        eligible = {c: n for c, n in counts.items() if n >= 2}
        if not eligible:
            return pd.Series(0, index=df.index)
        ref_col = min(eligible, key=lambda c: eligible[c])

    epoch_steps = np.sort(df.loc[df[ref_col].notna(), "step"].unique())
    if len(epoch_steps) == 0:
        return pd.Series(0, index=df.index)

    epochs = np.searchsorted(epoch_steps, steps, side="left")
    return pd.Series(np.clip(epochs, 0, len(epoch_steps) - 1), index=df.index)


def _load_from_tfevents(version_dir: Path) -> Optional[pd.DataFrame]:
    """Fallback: parse TensorBoard event files via the tensorboard package."""
    try:
        from tensorboard.backend.event_processing.event_accumulator import EventAccumulator
    except ImportError:
        return None

    if not list(version_dir.glob("events.out.tfevents.*")):
        return None

    ea = EventAccumulator(str(version_dir))
    ea.Reload()
    tags = ea.Tags().get("scalars", [])
    if not tags:
        return None

    per_tag = []
    for tag in tags:
        events = ea.Scalars(tag)
        t = pd.DataFrame({"step": [e.step for e in events], tag: [e.value for e in events]})
        # Deduplicate steps (DDP / checkpoint resume can log the same step twice)
        per_tag.append(t.groupby("step", sort=True)[tag].mean())

    df = pd.concat(per_tag, axis=1).reset_index()
    df["epoch"] = _infer_epochs(df)
    return df


def load_metrics(version_dir: Path) -> Optional[pd.DataFrame]:
    """Load training metrics, preferring metrics.csv over TensorBoard files."""
    df = _load_from_csv(version_dir)
    if df is None:
        df = _load_from_tfevents(version_dir)
    if df is None:
        print(f"  WARNING: no metrics found in {version_dir}")
    return df


# ---------------------------------------------------------------------------
# Smoothing
# ---------------------------------------------------------------------------

def ema_smooth(y: np.ndarray, factor: float) -> np.ndarray:
    """Exponential moving average — identical to TensorBoard's smoothing slider.

    *factor* is in [0, 1]:  0 = no smoothing,  ~0.9 = heavy smoothing.
    """
    if factor <= 0.0 or len(y) < 2:
        return y
    out = np.empty_like(y, dtype=float)
    out[0] = y[0]
    for i in range(1, len(y)):
        out[i] = factor * out[i - 1] + (1.0 - factor) * y[i]
    return out


# ---------------------------------------------------------------------------
# Series extraction
# ---------------------------------------------------------------------------

def _epoch_series(df: pd.DataFrame, col: str) -> Tuple[np.ndarray, np.ndarray]:
    """Per-epoch mean of *col* (handles metrics logged multiple times per epoch)."""
    if col not in df.columns or "epoch" not in df.columns:
        return np.array([]), np.array([])
    sub = df[["epoch", col]].dropna()
    if sub.empty:
        return np.array([]), np.array([])
    g = sub.groupby("epoch")[col].mean()
    return g.index.values.astype(float), g.values.astype(float)


def _step_series(df: pd.DataFrame, col: str) -> Tuple[np.ndarray, np.ndarray]:
    """Step-level (non-aggregated) series for *col*."""
    if col not in df.columns or "step" not in df.columns:
        return np.array([]), np.array([])
    sub = df[["step", col]].dropna()
    if sub.empty:
        return np.array([]), np.array([])
    return sub["step"].values.astype(float), sub[col].values.astype(float)


# ---------------------------------------------------------------------------
# Metric classification
# ---------------------------------------------------------------------------

# DeviceStatsMonitor columns — skip these entirely
_DEVICE_RE = re.compile(
    r"^(GPU|CPU|TPU)\s*[\d_]"
    r"|^(cpu|gpu|tpu)_"
    r"|memory_used|memory_free|memory_total"
    r"|sm_utilization|gpu_utilization|mem_utilization"
    r"|gpu_temp|power_draw|fan_speed|clock_speed"
    r"|MemAllocated|MemReserved|MemActive|MemPinned",
    re.IGNORECASE,
)


def _is_device_stat(col: str) -> bool:
    return bool(_DEVICE_RE.search(col))


def _get_category(col: str) -> str:
    """Return the subfolder category for a column."""
    if col.startswith("loss/") or col.startswith("validation_loss/"):
        return "losses"
    if col in ("validation_accuracy", "validation_average_jet_accuracy"):
        return "accuracy"
    if col.startswith("jet/") or col.startswith("particle/"):
        return "accuracy"
    if col.startswith("Purity/"):
        return "purity"
    if col.startswith("REGRESSION/"):
        return "regression"
    if col.startswith("CLASSIFICATION/"):
        return "classification"
    if re.match(r"lr[-/]|learning_rate", col, re.IGNORECASE):
        return "learning_rate"
    return "other"


def _get_plot_key(col: str) -> str:
    """Canonical plot identifier.

    Training metric ``loss/X`` and validation metric ``validation_loss/X``
    share the same key ``X`` so they are drawn on the same plot.
    All other metrics use their full tag name as the key.
    """
    if col.startswith("validation_loss/"):
        return col[len("validation_loss/"):]
    if col.startswith("loss/"):
        return col[len("loss/"):]
    return col


def _is_train(col: str) -> bool:
    """True for training-time metrics (loss/*, lr-*)."""
    return col.startswith("loss/") or bool(
        re.match(r"lr[-/]|learning_rate", col, re.IGNORECASE)
    )


def _is_lr(col: str) -> bool:
    return bool(re.match(r"lr[-/]|learning_rate", col, re.IGNORECASE))


def _sanitize(s: str) -> str:
    return re.sub(r"[^\w]", "_", s).strip("_")


def _get_ylabel(plot_key: str, category: str) -> str:
    if "percent_error" in plot_key:
        return "Percent Error"
    if "absolute_error" in plot_key:
        return "Absolute Error"
    if "accuracy" in plot_key:
        return "Accuracy"
    if category == "purity" or "purity" in plot_key.lower():
        return "Purity"
    if category == "losses":
        return "Loss"
    if category == "learning_rate":
        return "Learning Rate"
    last = plot_key.split("/")[-1]
    return last.replace("_", " ").title()


# ---------------------------------------------------------------------------
# Core plot renderer
# ---------------------------------------------------------------------------

def _hepplot(
    series_dict: dict,
    xlabel: str,
    ylabel: str,
    output_path: str,
    cmstext: str = "Private Work",
    lumitext: str = "(13.6 TeV)",
    figsize: Tuple[int, int] = (10, 8),
) -> None:
    if not series_dict:
        return
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    (
        HEPPlotter("CMS")
        .set_output(output_path)
        .set_labels(xlabel=xlabel, ylabel=ylabel)
        .set_data(series_dict, plot_type="graph")
        .set_options(
            legend=True,
            legend_font_size=14,
            legend_loc="best",
            grid=True,
            set_ylim=False,
        )
        .set_plot_config(
            cmstext=cmstext,
            lumitext=lumitext,
            figsize=list(figsize),
        )
        .run()
    )


# ---------------------------------------------------------------------------
# Main plot generation
# ---------------------------------------------------------------------------

def plot_all_metrics(
    dfs: Dict[str, pd.DataFrame],
    output_dir: Path,
    smooth: float = 0.0,
    subfolders: bool = False,
    cmstext: str = "Private Work",
    lumitext: str = "(13.6 TeV)",
) -> None:
    """Generate one plot file per metric from one or more labelled DataFrames.

    Training and validation curves for the same underlying metric are drawn on
    the same axes (solid = training, dashed = validation).  Each metric that
    does not share a logical counterpart still gets its own file.

    Parameters
    ----------
    dfs:
        Ordered dict  {legend_label → metrics DataFrame}.
    output_dir:
        Root directory where plot files are written.
    smooth:
        EMA smoothing factor in [0, 1].  0 = off.
    subfolders:
        When True, create category subdirectories (losses/, accuracy/, …).
    """
    multi = len(dfs) > 1
    label_colors: Dict[str, str] = {
        label: _COLORS[i % len(_COLORS)] for i, label in enumerate(dfs)
    }

    # ── Collect (category, plot_key) → [(label, col), …] mappings ───────────
    plot_map: Dict[Tuple[str, str], List[Tuple[str, str]]] = defaultdict(list)
    for label, df in dfs.items():
        for col in df.columns:
            if col in ("epoch", "step"):
                continue
            if _is_device_stat(col):
                continue
            plot_map[(_get_category(col), _get_plot_key(col))].append((label, col))

    # ── One plot per (category, plot_key) ────────────────────────────────────
    n_plots = 0
    for (cat, plot_key), entries in sorted(plot_map.items()):

        has_train = any(_is_train(col) for _, col in entries)
        has_val   = any(not _is_train(col) for _, col in entries)
        is_lr_plot = all(_is_lr(col) for _, col in entries)

        series: dict = {}
        for label, col in entries:
            df = dfs[label]
            x, y = (_step_series if is_lr_plot else _epoch_series)(df, col)
            if not len(x):
                continue

            y = ema_smooth(y, smooth)
            color     = label_colors[label]
            is_train  = _is_train(col)
            linestyle = "-" if is_train else "--"

            # ── Legend label ─────────────────────────────────────────────
            if multi:
                # Multiple models: colour = model, style = train/val
                if has_train and has_val:
                    tv_tag = "Train" if is_train else "Val"
                    tag = f"{label}  [{tv_tag}]"
                else:
                    tag = label
            else:
                # Single model: if both directions exist, say Train / Val
                if has_train and has_val:
                    tag = "Train" if is_train else "Val"
                else:
                    # Only one direction — use a clean short name
                    inner = col
                    for pfx in ("validation_loss/", "loss/", "validation_",
                                "REGRESSION/", "CLASSIFICATION/",
                                "Purity/", "jet/", "particle/"):
                        if inner.startswith(pfx):
                            inner = inner[len(pfx):]
                            break
                    tag = inner.replace("_", " ")

            series[tag] = {
                "data":  {"x": [x, None], "y": [y, None]},
                "style": {"marker": "", "linestyle": linestyle, "color": color},
            }

        if not series:
            continue

        # ── Output path ─────────────────────────────────────────────────────
        filename = _sanitize(plot_key)
        if subfolders:
            dest = output_dir / cat / filename
        else:
            dest = output_dir / filename

        xlabel = "Step" if is_lr_plot else "Epoch"
        ylabel = _get_ylabel(plot_key, cat)

        _hepplot(series, xlabel, ylabel, str(dest),
                 cmstext=cmstext, lumitext=lumitext)
        n_plots += 1

    print(f"  Generated {n_plots} plots in {output_dir}")


# ---------------------------------------------------------------------------
# CLI helpers
# ---------------------------------------------------------------------------

def _resolve_dirs(path: Path, all_versions: bool) -> List[Tuple[Path, str]]:
    """Return a list of *(version_dir, auto_label)* pairs for *path*.

    Handles three layouts:
    1. ``path`` is already a ``version_N`` directory.
    2. ``path`` is a single-model directory containing ``version_N`` subdirs.
    3. ``path`` is a multi-model directory whose children each contain
       ``version_N`` subdirs (auto-detected).
    """
    # Case 1 — explicit version directory
    if re.match(r"version_\d+$", path.name):
        return [(path, f"{path.parent.name}/{path.name}")]

    # Case 3 — multi-model parent directory
    if _is_multi_model_dir(path):
        result: List[Tuple[Path, str]] = []
        for child in sorted(path.iterdir()):
            if not child.is_dir() or child.name.startswith("."):
                continue
            versions = find_version_dirs(child)
            if not versions:
                continue
            selected = versions if all_versions else [versions[-1]]
            for v in selected:
                lbl = child.name if not all_versions else f"{child.name}/{v.name}"
                result.append((v, lbl))
        return result

    # Case 2 — single-model directory
    versions = find_version_dirs(path)
    if not versions:
        return []
    selected = versions if all_versions else [versions[-1]]
    return [
        (v, f"{v.parent.name}/{v.name}" if re.match(r"version_\d+$", v.name) else v.name)
        for v in selected
    ]


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Plot SPANet training metrics.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "-d", "--dirs", nargs="+", required=True, metavar="DIR",
        help="Training output directory/directories. Accepts: a version_N dir, "
             "a single-model dir (auto-selects latest version), a multi-model "
             "parent dir (each subdir treated as a separate model), or multiple "
             "paths for explicit comparison.",
    )
    parser.add_argument(
        "-l", "--labels", nargs="*", default=None, metavar="LABEL",
        help="Legend labels for each entry resolved from -d "
             "(default: derived from directory names).",
    )
    parser.add_argument(
        "-o", "--output-dir", default=None, metavar="OUT",
        help="Root directory for plots (default: <first resolved dir>/training_plots/).",
    )
    parser.add_argument(
        "--all-versions", action="store_true",
        help="Include ALL version_N subdirs instead of just the latest. "
             "Useful for seed variability studies.",
    )
    parser.add_argument(
        "--smooth", type=float, default=0.0, metavar="FACTOR",
        help="Exponential moving average smoothing factor in [0, 1]. "
             "0 = no smoothing (default), ~0.9 = heavy smoothing. "
             "Uses the same formula as TensorBoard's smoothing slider.",
    )
    parser.add_argument(
        "--subfolders", action="store_true",
        help="Organise plots into category subfolders: "
             "losses/, accuracy/, regression/, classification/, purity/, "
             "learning_rate/, other/.",
    )
    parser.add_argument(
        "--cmstext", default="Private Work",
        help="CMS label text on every plot (default: 'Private Work').",
    )
    parser.add_argument(
        "--lumitext", default="(13.6 TeV)",
        help="Luminosity / energy label on every plot (default: '(13.6 TeV)').",
    )
    args = parser.parse_args()

    # ── Resolve version directories ─────────────────────────────────────────
    raw_labels: List[str] = args.labels or []
    version_dirs: List[Path] = []
    auto_labels:  List[str] = []

    label_idx = 0
    for raw in args.dirs:
        resolved = _resolve_dirs(Path(raw), args.all_versions)
        if not resolved:
            print(f"WARNING: no training directories found under {raw}")
        for vd, auto_lbl in resolved:
            version_dirs.append(vd)
            # User-supplied label overrides auto label, one-to-one
            if label_idx < len(raw_labels):
                auto_labels.append(raw_labels[label_idx])
                label_idx += 1
            else:
                auto_labels.append(auto_lbl)

    if not version_dirs:
        print("No training directories to process. Exiting.")
        return

    # ── Load metrics DataFrames ─────────────────────────────────────────────
    dfs: Dict[str, pd.DataFrame] = {}
    for vd, lbl in zip(version_dirs, auto_labels):
        print(f"Loading  {vd} …")
        df = load_metrics(vd)
        if df is None:
            continue
        unique, n = lbl, 1
        while unique in dfs:
            unique = f"{lbl}_{n}"; n += 1
        dfs[unique] = df
        n_metrics = len([c for c in df.columns if c not in ("epoch", "step")])
        print(f"  → {len(df)} rows, {n_metrics} metrics")

    if not dfs:
        print("No metrics loaded. Exiting.")
        return

    # ── Output directory ─────────────────────────────────────────────────────
    output_dir = Path(args.output_dir) if args.output_dir else version_dirs[0] / "training_plots"
    output_dir.mkdir(parents=True, exist_ok=True)
    smooth_info = f", smooth={args.smooth}" if args.smooth > 0 else ""
    print(f"\nSaving plots to {output_dir}  (subfolders={args.subfolders}{smooth_info})\n")

    # ── Generate plots ────────────────────────────────────────────────────────
    plot_all_metrics(
        dfs,
        output_dir,
        smooth=args.smooth,
        subfolders=args.subfolders,
        cmstext=args.cmstext,
        lumitext=args.lumitext,
    )

    n_png = sum(1 for _ in output_dir.rglob("*.png"))
    print(f"\nDone — {n_png} PNG file(s) in {output_dir}")


if __name__ == "__main__":
    main()
