"""Training metric, efficiency and ROC plots of a model."""

import os
import shlex

import law
import luigi

from law_tasks import naming
from law_tasks.base import ModelTask
from law_tasks.tasks.register import RegisterModel
from law_tasks.tasks.training import Training


class TrainingMetrics(ModelTask):
    """Plot losses, accuracies and learning rate of the training."""

    metrics_args = luigi.Parameter(
        default="",
        description="additional arguments forwarded to plot_training_metrics.py",
    )

    def requires(self):
        return self.clone(Training)

    def output(self):
        return self.marker("training_metrics.json")

    def run(self):
        version_dir = self.version_dir()
        plot_dir = os.path.join(version_dir, "training_plots")
        if os.path.isdir(plot_dir) and os.listdir(plot_dir) and not self.force_overwrite:
            raise RuntimeError(
                "{} already exists and is not empty; pass --overwrite-plots "
                "to replace the plots in it".format(plot_dir)
            )

        command = "python3 {script} -d {dir}".format(
            script=self.cfg.training_metrics_script, dir=version_dir
        )
        if self.metrics_args:
            command += " " + self.metrics_args

        self.run_command(command)
        self.write_marker(self.output(), version_dir=version_dir, plot_dir=plot_dir)


class PlotTask(ModelTask):
    """Common behaviour of the efficiency and ROC plot tasks."""

    exclude_index = True

    #: 'efficiency' or 'roc'
    kind = None

    #: whether the plot pairs the jets, and therefore needs the resonances
    needs_resonances = False

    plot_name = luigi.Parameter(
        description="name of the plot configuration, i.e. the subdirectory the "
        "plots are written to (see the [efficiency_plots] and [roc_plots] "
        "sections of law.cfg)",
    )
    plot_dir = luigi.Parameter(
        default="",
        description="parent directory of all plots of this model; default: "
        "derived from the options basename",
    )
    plot_args = luigi.Parameter(
        default="",
        description="additional arguments forwarded to the plotting script",
    )
    region = luigi.Parameter(
        default="",
        description="region the plot is made in, replacing the one of the "
        "configured arguments, e.g. 'vbf_no_kin_cuts', 'vbf_presel', '4b' or "
        "'inclusive' for no selection at all; the plots of a region of their "
        "own are kept apart from the configured ones; default: the region of "
        "the [efficiency_plots] / [roc_plots] entry",
    )

    def requires(self):
        return self.clone(RegisterModel)

    @property
    def plot_definitions(self):
        return (
            self.cfg.efficiency_plots if self.kind == "efficiency" else self.cfg.roc_plots
        )

    @property
    def script(self):
        return (
            self.cfg.efficiency_script if self.kind == "efficiency" else self.cfg.roc_script
        )

    @property
    def plot_base(self):
        return (
            self.cfg.eff_plot_base if self.kind == "efficiency" else self.cfg.roc_plot_base
        )

    @property
    def main_dir(self):
        if self.plot_dir:
            return self.plot_dir
        return naming.derive_plot_dir(self.model_key) + self.eval_suffix

    @property
    def region_suffix(self):
        return "_{}".format(self.region) if self.region else ""

    @property
    def configured_arguments(self):
        """The configured arguments, with ``--region`` replacing the region.

        ``-r`` is what ``efficiency_studies.py`` and ``ROC_plots.py`` call the
        region, and it is part of the arguments of every plot; giving one on
        the command line drops the configured one instead of passing both.
        """
        configured = self.plot_definitions.get(self.plot_name) or ""
        if not self.region:
            return configured

        tokens, keep, skip = shlex.split(configured), [], False
        for token in tokens:
            if skip:
                skip = False
            elif token in ("-r", "--region"):
                skip = True
            else:
                keep.append(token)
        keep += ["-r", self.region]
        return " ".join(shlex.quote(token) for token in keep)

    @property
    def plot_arguments(self):
        """What the plot really runs with: the resonances decide the pairings.

        An efficiency the event file has no resonance for cannot be computed,
        so it is switched off -- ``--ignore-higgs`` is added, ``--vbf``
        dropped -- and the plot is made with the other one.
        """
        arguments = self.configured_arguments
        if not self.needs_resonances:
            return arguments

        adapted, _ = self.event_info.efficiency_arguments(arguments)
        return arguments if adapted is None else adapted

    @property
    def target_dir(self):
        return os.path.join(
            self.plot_base, self.main_dir, self.plot_name + self.region_suffix
        )

    def output(self):
        return self.eval_marker("{}_{}.json".format(self.kind, self.plot_name))

    def unsupported_reason(self):
        """Why the event file of the model leaves no efficiency to compute."""
        if not self.needs_resonances:
            return None
        return self.event_info.unsupported(self.configured_arguments)

    def check_target_dir(self):
        """Refuse to silently write into a directory that already holds plots."""
        if self.force_overwrite or not os.path.isdir(self.target_dir):
            return
        if not os.listdir(self.target_dir):
            return
        if self.marker_is_stale(self.output()):
            # the plots in there are the ones this very task made for an
            # earlier training, and they are what makes it rerun now
            self.publish_message(
                "replacing the plots of an earlier training in {}".format(
                    self.target_dir
                )
            )
            return
        raise RuntimeError(
            "{} already exists and is not empty; pass --overwrite-plots to write "
            "into it anyway, or choose another parent directory with "
            "--plot-dir".format(
                self.target_dir
            )
        )

    def run(self):
        if self.plot_name not in self.plot_definitions:
            raise ValueError(
                "unknown {} plot '{}', known ones: {}".format(
                    self.kind, self.plot_name, ", ".join(sorted(self.plot_definitions))
                )
            )

        reason = self.unsupported_reason()
        if reason:
            raise RuntimeError(
                "the {} plot '{}' cannot be made for this model: {}; it is "
                "left out of hh4b.{}Plots".format(
                    self.kind,
                    self.plot_name,
                    reason,
                    "Efficiency" if self.kind == "efficiency" else "Roc",
                )
            )

        self.check_target_dir()
        os.makedirs(os.path.join(self.plot_base, self.main_dir), exist_ok=True)

        configuration = self.input()[self.kind].path
        arguments = self.plot_arguments
        if arguments != self.configured_arguments:
            self.publish_message(
                "the resonances of {} give: {}".format(
                    os.path.basename(self.event_info.path), arguments
                )
            )
        command = "cd {base} && python3 {script} -pd {pd} -conf {conf} {args}".format(
            base=self.plot_base,
            script=self.script,
            pd=os.path.join(self.main_dir, self.plot_name + self.region_suffix),
            conf=configuration,
            args=arguments,
        )
        if self.plot_args:
            command += " " + self.plot_args

        self.run_command(command)
        self.write_marker(
            self.output(),
            plot_dir=self.target_dir,
            configuration=configuration,
            arguments=arguments,
        )


class EfficiencyPlot(PlotTask):
    """One efficiency configuration, e.g. ``VBFEff_vbf_no_kin_cuts``."""

    kind = "efficiency"
    needs_resonances = True


class RocPlot(PlotTask):
    """One ROC configuration, e.g. ``vbf_no_kin_cuts``."""

    kind = "roc"


class PlotCollection(ModelTask, law.WrapperTask):
    """All plot configurations of one kind."""

    exclude_index = True

    plot_task = None
    plot_dir = luigi.Parameter(
        default="",
        description="parent directory of all plots of this model; default: "
        "derived from the options basename",
    )
    region = luigi.Parameter(
        default="",
        description="region every plot is made in, replacing the configured "
        "ones, e.g. 'inclusive' for no selection at all; default: the region "
        "of each entry",
    )

    @property
    def definitions(self):
        return (
            self.cfg.efficiency_plots
            if self.plot_task is EfficiencyPlot
            else self.cfg.roc_plots
        )

    def skipped(self):
        """``{plot: reason}`` of the plots the event file does not allow."""
        skipped = {}
        for name in sorted(self.definitions):
            reason = self.clone(self.plot_task, plot_name=name).unsupported_reason()
            if reason:
                skipped[name] = reason
        return skipped

    def requires(self):
        skipped = self.skipped()
        return [
            self.clone(self.plot_task, plot_name=name)
            for name in sorted(self.definitions)
            if name not in skipped
        ]


class EfficiencyPlots(PlotCollection):
    """Every efficiency plot defined in the ``[efficiency_plots]`` section."""

    plot_task = EfficiencyPlot


class RocPlots(PlotCollection):
    """Every ROC plot defined in the ``[roc_plots]`` section."""

    plot_task = RocPlot
