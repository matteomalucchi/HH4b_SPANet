#!/usr/bin/env python3
"""Plot SPANet training metrics from PyTorch Lightning output.

Reads the metrics.csv saved automatically by PyTorch Lightning alongside
the TensorBoard event files, then produces HEPPlotter-styled plots of all
relevant training quantities.

Usage examples
--------------
# Plot the most recent version in a training run directory:
    python plot_training_metrics.py -d /eos/spanet_outputs/my_run

# Plot a specific version directory:
    python plot_training_metrics.py -d /eos/spanet_outputs/my_run/version_3

# Overlay all versions (e.g. seed studies):
    python plot_training_metrics.py -d /eos/spanet_outputs/my_run --all-versions

# Compare two different training configurations:
    python plot_training_metrics.py \\
        -d /eos/run_A /eos/run_B \\
        -l "Config A" "Config B"
"""

import argparse
import os
import re
import sys
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

def _version_index(path: Path) -> int:
    m = re.match(r"version_(\d+)$", path.name)
    return int(m.group(1)) if m else -1


def find_version_dirs(base: Path) -> List[Path]:
    """Return sorted version_N subdirs of *base*, or [base] if none exist."""
    if not base.is_dir():
        return []
    versions = [p for p in base.iterdir() if p.is_dir() and re.match(r"version_\d+$", p.name)]
    return sorted(versions, key=_version_index) if versions else [base]


# ---------------------------------------------------------------------------
# Metric loading
# ---------------------------------------------------------------------------

def _load_from_csv(version_dir: Path) -> Optional[pd.DataFrame]:
    csv_path = version_dir / "metrics.csv"
    if not csv_path.exists():
        return None
    df = pd.read_csv(csv_path)
    # Drop auto-generated index columns
    df = df.loc[:, ~df.columns.str.match(r"^Unnamed")]
    return df


def _infer_epochs(df: pd.DataFrame) -> pd.Series:
    """Infer epoch numbers from step values when no explicit epoch column exists.

    Metrics logged once per epoch (validation) have fewer rows than training
    metrics.  Their steps mark epoch boundaries; every step up to and including
    the n-th boundary is assigned to epoch n.
    """
    steps = df["step"].values
    # Find the metric column with the fewest non-NaN values — that is the
    # per-epoch (validation) metric, and its sorted unique steps are the
    # epoch-end markers.
    metric_cols = [c for c in df.columns if c not in ("step",)]
    counts = {c: df[c].notna().sum() for c in metric_cols}
    min_count = min(counts.values())
    ref_col = next(c for c, n in counts.items() if n == min_count)
    epoch_steps = np.sort(df.loc[df[ref_col].notna(), "step"].unique())
    # np.searchsorted with side='left': step <= epoch_steps[i] → epoch i
    epochs = np.searchsorted(epoch_steps, steps, side="left")
    # Clip so steps beyond the last boundary stay at the final epoch index
    return pd.Series(np.clip(epochs, 0, len(epoch_steps) - 1), index=df.index)


def _load_from_tfevents(version_dir: Path) -> Optional[pd.DataFrame]:
    """Fallback: parse TensorBoard event files via the tensorboard package."""
    try:
        from tensorboard.backend.event_processing.event_accumulator import EventAccumulator
    except ImportError:
        return None

    event_files = list(version_dir.glob("events.out.tfevents.*"))
    if not event_files:
        return None

    ea = EventAccumulator(str(version_dir))
    ea.Reload()
    tags = ea.Tags().get("scalars", [])
    if not tags:
        return None

    per_tag = []
    for tag in tags:
        events = ea.Scalars(tag)
        tag_df = pd.DataFrame({"step": [e.step for e in events], tag: [e.value for e in events]})
        # Deduplicate steps: multiple event files (DDP, checkpoint resume) can
        # produce the same step more than once — average the values.
        tag_df = tag_df.groupby("step", sort=True)[tag].mean()
        per_tag.append(tag_df)

    df = pd.concat(per_tag, axis=1).reset_index()
    df["epoch"] = _infer_epochs(df)
    return df


def load_metrics(version_dir: Path) -> Optional[pd.DataFrame]:
    """Load training metrics, preferring metrics.csv over TensorBoard files."""
    df = _load_from_csv(version_dir)
    if df is not None:
        return df
    df = _load_from_tfevents(version_dir)
    if df is None:
        print(f"  WARNING: no metrics found in {version_dir}")
    return df


# ---------------------------------------------------------------------------
# Series extraction
# ---------------------------------------------------------------------------

def _epoch_series(df: pd.DataFrame, col: str) -> Tuple[np.ndarray, np.ndarray]:
    """Per-epoch mean of *col* (handles metrics logged at every step)."""
    if col not in df.columns or "epoch" not in df.columns:
        return np.array([]), np.array([])
    sub = df[["epoch", col]].dropna()
    if sub.empty:
        return np.array([]), np.array([])
    grouped = sub.groupby("epoch")[col].mean()
    return grouped.index.values.astype(float), grouped.values.astype(float)


def _step_series(df: pd.DataFrame, col: str) -> Tuple[np.ndarray, np.ndarray]:
    """Step-level (non-aggregated) series for *col*."""
    if col not in df.columns or "step" not in df.columns:
        return np.array([]), np.array([])
    sub = df[["step", col]].dropna()
    if sub.empty:
        return np.array([]), np.array([])
    return sub["step"].values.astype(float), sub[col].values.astype(float)


def _graph_entry(x: np.ndarray, y: np.ndarray, color: str,
                 marker: str = "", linestyle: str = "-") -> dict:
    """Build a single series entry for HEPPlotter graph plots."""
    return {
        "data": {"x": [x, None], "y": [y, None]},
        "style": {"marker": marker, "linestyle": linestyle, "color": color},
    }


# ---------------------------------------------------------------------------
# Metric categorisation
# ---------------------------------------------------------------------------

def group_metrics(df: pd.DataFrame) -> Dict[str, List[str]]:
    """Partition metric column names into named groups."""
    cols = [c for c in df.columns if c not in ("epoch", "step")]
    groups: Dict[str, List[str]] = {}

    def _add(group: str, col: str) -> None:
        groups.setdefault(group, []).append(col)

    for c in cols:
        if c in ("loss/total_loss", "loss/total_loss_no_mdmm", "validation_loss/total_loss"):
            _add("total_loss", c)
        elif re.search(r"/assignment_loss$", c):
            _add("assignment_loss", c)
        elif re.search(r"/detection_loss$", c):
            _add("detection_loss", c)
        elif "symmetric_loss" in c:
            _add("symmetric_loss", c)
        elif c.startswith("loss/regression/") or c.startswith("validation_loss/regression/"):
            _add("regression_loss", c)
        elif c.startswith("loss/classification/") or c.startswith("validation_loss/classification/"):
            _add("classification_loss", c)
        elif c in ("validation_accuracy", "validation_average_jet_accuracy"):
            _add("validation_accuracy", c)
        elif c.startswith("jet/accuracy"):
            _add("jet_accuracy", c)
        elif c.startswith("particle/"):
            _add("particle_accuracy", c)
        elif c.startswith("Purity/"):
            _add("purity", c)
        elif c.startswith("REGRESSION/"):
            _add("regression_metrics", c)
        elif c.startswith("CLASSIFICATION/"):
            _add("classification_metrics", c)
        elif re.match(r"lr[-/]|learning_rate", c, re.IGNORECASE):
            _add("learning_rate", c)
        else:
            _add("other", c)

    return groups


def _short_name(col: str) -> str:
    """Strip common long prefixes for cleaner legend labels."""
    for prefix in ("loss/", "validation_loss/", "REGRESSION/", "CLASSIFICATION/", "Purity/"):
        if col.startswith(prefix):
            return col[len(prefix):]
    return col


# ---------------------------------------------------------------------------
# Core plot generator
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
    """Render one plot file via HEPPlotter; no-op when *series_dict* is empty."""
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


def _is_val_col(col: str) -> bool:
    return col.startswith("validation") or col.startswith("REGRESSION") or \
           col.startswith("CLASSIFICATION") or col.startswith("jet/") or \
           col.startswith("particle/") or col.startswith("Purity/")


def plot_all_metrics(
    dfs: Dict[str, pd.DataFrame],
    output_dir: Path,
    cmstext: str = "Private Work",
    lumitext: str = "(13.6 TeV)",
) -> None:
    """Generate all plot files from one or more labelled DataFrames.

    Parameters
    ----------
    dfs:
        Ordered dict mapping legend label -> metrics DataFrame.
    output_dir:
        Directory where plot files are written.
    """
    multi = len(dfs) > 1
    all_groups = {label: group_metrics(df) for label, df in dfs.items()}

    # ------------------------------------------------------------------
    # Colour assignment strategy
    #   single label  → each metric column gets a unique colour
    #   multi  label  → each label gets a base colour; train=solid val=dashed
    # ------------------------------------------------------------------
    label_colors: Dict[str, str] = {
        label: _COLORS[i % len(_COLORS)] for i, label in enumerate(dfs)
    }

    def _build_series(
        group_name: str,
        use_step: bool = False,
    ) -> dict:
        """Collect one series_dict for a given metric group."""
        series: dict = {}
        col_idx = 0  # used in single-label mode for unique colours

        for label, df in dfs.items():
            cols = all_groups[label].get(group_name, [])
            for col in cols:
                is_val = _is_val_col(col)
                x, y = (_step_series if use_step else _epoch_series)(df, col)
                if not len(x):
                    continue

                if multi:
                    color = label_colors[label]
                    linestyle = "--" if is_val else "-"
                    tag = f"{label} / {_short_name(col)}"
                else:
                    color = _COLORS[col_idx % len(_COLORS)]
                    linestyle = "--" if is_val else "-"
                    tag = _short_name(col)

                series[tag] = _graph_entry(x, y, color, linestyle=linestyle)
                col_idx += 1

        return series

    # ------------------------------------------------------------------
    # 1. Total loss  (training solid, validation dashed)
    # ------------------------------------------------------------------
    _hepplot(
        _build_series("total_loss"),
        xlabel="Epoch", ylabel="Total Loss",
        output_path=str(output_dir / "total_loss"),
        cmstext=cmstext, lumitext=lumitext,
    )

    # ------------------------------------------------------------------
    # 2. Assignment loss per particle
    # ------------------------------------------------------------------
    _hepplot(
        _build_series("assignment_loss"),
        xlabel="Epoch", ylabel="Assignment Loss",
        output_path=str(output_dir / "assignment_loss"),
        cmstext=cmstext, lumitext=lumitext,
    )

    # ------------------------------------------------------------------
    # 3. Detection loss per particle
    # ------------------------------------------------------------------
    _hepplot(
        _build_series("detection_loss"),
        xlabel="Epoch", ylabel="Detection Loss",
        output_path=str(output_dir / "detection_loss"),
        cmstext=cmstext, lumitext=lumitext,
    )

    # ------------------------------------------------------------------
    # 4. Symmetric (Jensen–Shannon) loss
    # ------------------------------------------------------------------
    _hepplot(
        _build_series("symmetric_loss"),
        xlabel="Epoch", ylabel="Symmetric KL Loss",
        output_path=str(output_dir / "symmetric_loss"),
        cmstext=cmstext, lumitext=lumitext,
    )

    # ------------------------------------------------------------------
    # 5. Regression auxiliary loss
    # ------------------------------------------------------------------
    _hepplot(
        _build_series("regression_loss"),
        xlabel="Epoch", ylabel="Regression Loss",
        output_path=str(output_dir / "regression_loss"),
        cmstext=cmstext, lumitext=lumitext,
    )

    # ------------------------------------------------------------------
    # 6. Classification auxiliary loss
    # ------------------------------------------------------------------
    _hepplot(
        _build_series("classification_loss"),
        xlabel="Epoch", ylabel="Classification Loss",
        output_path=str(output_dir / "classification_loss"),
        cmstext=cmstext, lumitext=lumitext,
    )

    # ------------------------------------------------------------------
    # 7. Validation accuracy  (primary checkpoint metric)
    # ------------------------------------------------------------------
    _hepplot(
        _build_series("validation_accuracy"),
        xlabel="Epoch", ylabel="Accuracy",
        output_path=str(output_dir / "validation_accuracy"),
        cmstext=cmstext, lumitext=lumitext,
    )

    # ------------------------------------------------------------------
    # 8. Jet assignment accuracy breakdown  (N-of-M completeness)
    # ------------------------------------------------------------------
    _hepplot(
        _build_series("jet_accuracy"),
        xlabel="Epoch", ylabel="Jet Assignment Accuracy",
        output_path=str(output_dir / "jet_accuracy"),
        cmstext=cmstext, lumitext=lumitext,
    )

    # ------------------------------------------------------------------
    # 9. Particle detection accuracy
    # ------------------------------------------------------------------
    _hepplot(
        _build_series("particle_accuracy"),
        xlabel="Epoch", ylabel="Particle Detection Accuracy",
        output_path=str(output_dir / "particle_accuracy"),
        cmstext=cmstext, lumitext=lumitext,
    )

    # ------------------------------------------------------------------
    # 10. Purity metrics
    # ------------------------------------------------------------------
    _hepplot(
        _build_series("purity"),
        xlabel="Epoch", ylabel="Purity",
        output_path=str(output_dir / "purity"),
        cmstext=cmstext, lumitext=lumitext,
    )

    # ------------------------------------------------------------------
    # 11. Regression evaluation metrics — one plot per regression key
    # ------------------------------------------------------------------
    # Collect all (label, col) pairs and group by regression variable name
    reg_by_key: Dict[str, List[Tuple[str, str]]] = {}
    for label in dfs:
        for col in all_groups[label].get("regression_metrics", []):
            inner = col.replace("REGRESSION/", "")
            m = re.match(r"^(.+?)_(percent_error|absolute_error)$", inner)
            rkey = m.group(1) if m else inner
            reg_by_key.setdefault(rkey, []).append((label, col))

    for rkey, entries in reg_by_key.items():
        series: dict = {}
        col_idx = 0
        for label, col in entries:
            df = dfs[label]
            x, y = _epoch_series(df, col)
            if not len(x):
                continue
            inner = col.replace("REGRESSION/", "")
            m = re.match(r"^(.+?)_(percent_error|absolute_error)$", inner)
            rtype = m.group(2) if m else inner
            tag = rtype if not multi else f"{label} / {rtype}"
            color = label_colors[label] if multi else _COLORS[col_idx % len(_COLORS)]
            series[tag] = _graph_entry(x, y, color)
            col_idx += 1
        safe = rkey.replace("/", "_")
        _hepplot(
            series,
            xlabel="Epoch", ylabel=f"Regression Error  ({rkey})",
            output_path=str(output_dir / f"regression_{safe}"),
            cmstext=cmstext, lumitext=lumitext,
        )

    # ------------------------------------------------------------------
    # 12. Classification evaluation metrics — one plot per class key
    # ------------------------------------------------------------------
    cls_by_key: Dict[str, List[Tuple[str, str]]] = {}
    for label in dfs:
        for col in all_groups[label].get("classification_metrics", []):
            inner = col.replace("CLASSIFICATION/", "")
            m = re.match(r"^(.+?)(_accuracy.*)$", inner)
            ckey = m.group(1) if m else inner
            cls_by_key.setdefault(ckey, []).append((label, col))

    for ckey, entries in cls_by_key.items():
        series = {}
        col_idx = 0
        for label, col in entries:
            df = dfs[label]
            x, y = _epoch_series(df, col)
            if not len(x):
                continue
            inner = col.replace("CLASSIFICATION/", "")
            m = re.match(r"^(.+?)(_accuracy.*)$", inner)
            suffix = m.group(2).lstrip("_") if m else "accuracy"
            tag = suffix if not multi else f"{label} / {suffix}"
            color = label_colors[label] if multi else _COLORS[col_idx % len(_COLORS)]
            series[tag] = _graph_entry(x, y, color)
            col_idx += 1
        safe = ckey.replace("/", "_")
        _hepplot(
            series,
            xlabel="Epoch", ylabel=f"Classification Accuracy  ({ckey})",
            output_path=str(output_dir / f"classification_{safe}"),
            cmstext=cmstext, lumitext=lumitext,
        )

    # ------------------------------------------------------------------
    # 13. Learning rate schedule
    # ------------------------------------------------------------------
    _hepplot(
        _build_series("learning_rate", use_step=True),
        xlabel="Step", ylabel="Learning Rate",
        output_path=str(output_dir / "learning_rate"),
        cmstext=cmstext, lumitext=lumitext,
    )

    # ------------------------------------------------------------------
    # 14. Miscellaneous / unrecognised metrics
    # ------------------------------------------------------------------
    other_series = _build_series("other")
    if other_series:
        _hepplot(
            other_series,
            xlabel="Step / Epoch", ylabel="Value",
            output_path=str(output_dir / "other_metrics"),
            cmstext=cmstext, lumitext=lumitext,
        )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _resolve_dirs(path: Path, all_versions: bool) -> List[Path]:
    """Expand *path* to a list of version directories to process."""
    # Already points to a version directory
    if re.match(r"version_\d+$", path.name):
        return [path]

    versions = find_version_dirs(path)
    if not versions:
        return []
    return versions if all_versions else [versions[-1]]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Plot SPANet training metrics.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "-d", "--dirs", nargs="+", required=True, metavar="DIR",
        help="Training output directory/directories (version_N dirs or their parents).",
    )
    parser.add_argument(
        "-l", "--labels", nargs="*", default=None, metavar="LABEL",
        help="Legend labels for each directory (default: derived from directory names).",
    )
    parser.add_argument(
        "-o", "--output-dir", default=None, metavar="OUT",
        help="Directory to save plots (default: <first-dir>/training_plots/).",
    )
    parser.add_argument(
        "--all-versions", action="store_true",
        help="When a parent directory is given, include ALL version_N subdirs "
             "overlaid on the same plots (useful for seed variability studies).",
    )
    parser.add_argument(
        "--cmstext", default="Private Work",
        help="CMS label text shown on every plot (default: 'Private Work').",
    )
    parser.add_argument(
        "--lumitext", default="(13.6 TeV)",
        help="Lumi / energy label shown on every plot (default: '(13.6 TeV)').",
    )
    args = parser.parse_args()

    # ------------------------------------------------------------------
    # Resolve version directories
    # ------------------------------------------------------------------
    version_dirs: List[Path] = []
    for raw in args.dirs:
        expanded = _resolve_dirs(Path(raw), args.all_versions)
        if not expanded:
            print(f"WARNING: no version directories found under {raw}")
        version_dirs.extend(expanded)

    if not version_dirs:
        print("No training directories to process. Exiting.")
        return

    # ------------------------------------------------------------------
    # Build label list
    # ------------------------------------------------------------------
    raw_labels: List[str] = args.labels or []
    labels: List[str] = []
    for i, vd in enumerate(version_dirs):
        if i < len(raw_labels):
            labels.append(raw_labels[i])
        elif re.match(r"version_\d+$", vd.name):
            labels.append(f"{vd.parent.name}/{vd.name}")
        else:
            labels.append(vd.name)

    # ------------------------------------------------------------------
    # Load metrics DataFrames
    # ------------------------------------------------------------------
    dfs: Dict[str, pd.DataFrame] = {}
    for vd, label in zip(version_dirs, labels):
        print(f"Loading  {vd} …")
        df = load_metrics(vd)
        if df is None:
            continue
        # Guarantee unique label keys
        unique = label
        counter = 1
        while unique in dfs:
            unique = f"{label}_{counter}"
            counter += 1
        dfs[unique] = df
        print(f"  → {len(df)} rows, {len([c for c in df.columns if c not in ('epoch','step')])} metrics")

    if not dfs:
        print("No metrics loaded. Exiting.")
        return

    # ------------------------------------------------------------------
    # Output directory
    # ------------------------------------------------------------------
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        first = version_dirs[0]
        output_dir = first / "training_plots"
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\nSaving plots to {output_dir}\n")

    # ------------------------------------------------------------------
    # Generate plots
    # ------------------------------------------------------------------
    plot_all_metrics(dfs, output_dir, cmstext=args.cmstext, lumitext=args.lumitext)

    n_files = sum(1 for f in output_dir.iterdir() if f.is_file())
    print(f"\nDone — {n_files} plot file(s) in {output_dir}")


if __name__ == "__main__":
    main()
