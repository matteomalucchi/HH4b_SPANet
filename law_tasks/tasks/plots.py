"""Training metric, efficiency and ROC plots of a model."""

import os

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
        command = "python3 {script} -d {dir}".format(
            script=self.cfg.training_metrics_script, dir=version_dir
        )
        if self.metrics_args:
            command += " " + self.metrics_args

        self.run_command(command)
        self.write_marker(
            self.output(),
            version_dir=version_dir,
            plot_dir=os.path.join(version_dir, "training_plots"),
        )


class PlotTask(ModelTask):
    """Common behaviour of the efficiency and ROC plot tasks."""

    exclude_index = True

    #: 'efficiency' or 'roc'
    kind = None

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
    overwrite = luigi.BoolParameter(
        default=False,
        significant=False,
        description="write into an existing plot directory; default: False",
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
        return self.plot_dir or naming.derive_plot_dir(self.model_key)

    @property
    def target_dir(self):
        return os.path.join(self.plot_base, self.main_dir, self.plot_name)

    def output(self):
        return self.marker("{}_{}.json".format(self.kind, self.plot_name))

    def check_target_dir(self):
        """Refuse to silently write into a directory that already holds plots."""
        if self.overwrite or not os.path.isdir(self.target_dir):
            return
        if not os.listdir(self.target_dir):
            return
        raise RuntimeError(
            "{} already exists and is not empty; pass --overwrite to write into "
            "it anyway, or choose another parent directory with --plot-dir".format(
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

        self.check_target_dir()
        os.makedirs(os.path.join(self.plot_base, self.main_dir), exist_ok=True)

        configuration = self.input()[self.kind].path
        command = "cd {base} && python3 {script} -pd {pd} -conf {conf} {args}".format(
            base=self.plot_base,
            script=self.script,
            pd=os.path.join(self.main_dir, self.plot_name),
            conf=configuration,
            args=self.plot_definitions[self.plot_name],
        )
        if self.plot_args:
            command += " " + self.plot_args

        self.run_command(command)
        self.write_marker(
            self.output(),
            plot_dir=self.target_dir,
            configuration=configuration,
            arguments=self.plot_definitions[self.plot_name],
        )


class EfficiencyPlot(PlotTask):
    """One efficiency configuration, e.g. ``VBFEff_vbf_no_kin_cuts``."""

    kind = "efficiency"


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
    overwrite = luigi.BoolParameter(
        default=False,
        significant=False,
        description="write into existing plot directories; default: False",
    )

    def requires(self):
        definitions = (
            self.cfg.efficiency_plots
            if self.plot_task is EfficiencyPlot
            else self.cfg.roc_plots
        )
        return [
            self.clone(self.plot_task, plot_name=name) for name in sorted(definitions)
        ]


class EfficiencyPlots(PlotCollection):
    """Every efficiency plot defined in the ``[efficiency_plots]`` section."""

    plot_task = EfficiencyPlot


class RocPlots(PlotCollection):
    """Every ROC plot defined in the ``[roc_plots]`` section."""

    plot_task = RocPlot
