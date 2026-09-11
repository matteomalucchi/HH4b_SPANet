"""Entry point task: everything from the training to the performance plots."""

import json

import luigi

from law_tasks.base import ModelTask
from law_tasks.tasks.plots import EfficiencyPlots, RocPlots, TrainingMetrics
from law_tasks.tasks.register import RegisterModel


class Performance(ModelTask):
    """Train (or reuse) the model, predict, and produce all performance plots.

    This is the task to run::

        law run hh4b.Performance --options-file options_files/HH4b/vbf_ggf/<model>.json
    """

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
        return {
            "metrics": self.clone(TrainingMetrics),
            "efficiency": self.clone(EfficiencyPlots),
            "roc": self.clone(RocPlots),
            "registration": self.clone(RegisterModel),
        }

    def output(self):
        return self.marker("performance.json")

    def run(self):
        with open(self.input()["registration"]["summary"].path) as fobj:
            registration = json.load(fobj)

        with open(self.input()["metrics"].path) as fobj:
            metrics = json.load(fobj)

        efficiency = {
            task.plot_name: task.target_dir for task in self.requires()["efficiency"].requires()
        }
        roc = {
            task.plot_name: task.target_dir for task in self.requires()["roc"].requires()
        }

        self.write_marker(
            self.output(),
            model_key=self.model_key,
            seed=self.seed,
            version_dir=self.version_dir(),
            prediction_file=registration["prediction_file"],
            test_file=registration["test_file"],
            label=registration["label"],
            color=registration["color"],
            training_plots=metrics["plot_dir"],
            efficiency_plots=efficiency,
            roc_plots=roc,
        )

        self.publish_message("")
        self.publish_message("model:            {}".format(self.model_key))
        self.publish_message("training:         {}".format(self.version_dir()))
        self.publish_message("prediction:       {}".format(registration["prediction_file"]))
        self.publish_message("training plots:   {}".format(metrics["plot_dir"]))
        for name, path in sorted(efficiency.items()):
            self.publish_message("efficiency plots: {}".format(path))
        for name, path in sorted(roc.items()):
            self.publish_message("ROC plots:        {}".format(path))
        self.publish_message("summary:          {}".format(self.output().path))
