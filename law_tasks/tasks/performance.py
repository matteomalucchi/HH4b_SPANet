"""Entry point task: everything from the training to the performance plots."""

import json

import luigi

from law_tasks import journal
from law_tasks.base import ModelTask
from law_tasks.tasks.export import ExportModel, ExportParameters, TransferModel
from law_tasks.tasks.plots import EfficiencyPlots, RocPlots, TrainingMetrics
from law_tasks.tasks.register import RegisterModel


class Performance(ExportParameters, ModelTask):
    """Train (or reuse) the model, predict, and produce all performance plots.

    This is the task to run::

        law run hh4b.Performance --options-file options_files/HH4b/vbf_ggf/<model>.json
    """

    plot_dir = luigi.Parameter(
        default="",
        description="parent directory of all plots of this model; default: "
        "derived from the options basename",
    )
    region = luigi.Parameter(
        default="",
        description="region every efficiency and ROC plot is made in, "
        "replacing the configured ones, e.g. 'inclusive' for no selection at "
        "all; default: the region of each entry",
    )
    export = luigi.ChoiceParameter(
        default="auto",
        choices=["auto", "yes", "no"],
        significant=False,
        description="export the trained model to ONNX and copy it to the "
        "machine the analysis runs on; 'auto' exports it and copies it only "
        "when a destination is configured, 'yes' insists on the copy, 'no' "
        "does neither; default: auto",
    )

    @property
    def region_suffix(self):
        return "_{}".format(self.region) if self.region else ""

    def requires(self):
        reqs = {
            "efficiency": self.clone(EfficiencyPlots),
            "roc": self.clone(RocPlots),
            "registration": self.clone(RegisterModel),
        }
        # the training metrics belong to the training, not to the sample it is
        # evaluated on: they are made once, with the model's own test file
        if not self.eval_key:
            reqs["metrics"] = self.clone(TrainingMetrics)

        # the ONNX model belongs to the training as well, and the copy of it
        # only happens when there is somewhere to copy it to
        if self.export != "no" and not self.eval_key:
            _, destination = self.onnx_destination
            reqs["export"] = self.clone(
                TransferModel if destination or self.export == "yes" else ExportModel
            )
        return reqs

    def output(self):
        return self.eval_marker("performance.json")

    def run(self):
        with open(self.input()["registration"]["summary"].path) as fobj:
            registration = json.load(fobj)

        metrics = {}
        if "metrics" in self.input():
            with open(self.input()["metrics"].path) as fobj:
                metrics = json.load(fobj)

        collections = self.requires()
        efficiency = {
            task.plot_name: task.target_dir
            for task in collections["efficiency"].requires()
        }
        roc = {task.plot_name: task.target_dir for task in collections["roc"].requires()}
        skipped = dict(collections["efficiency"].skipped())
        skipped.update(collections["roc"].skipped())

        onnx, onnx_copy = None, None
        if "export" in self.input():
            export = self.input()["export"]
            if isinstance(export, dict):  # hh4b.ExportModel, nowhere to copy to
                onnx = export["onnx"].path
            else:  # hh4b.TransferModel, the marker of the copy
                with open(export.path) as fobj:
                    transfer = json.load(fobj)
                onnx = transfer["onnx_file"]
                onnx_copy = "{}:{}".format(transfer["host"], transfer["remote_file"])

        self.write_marker(
            self.output(),
            model_key=self.model_key,
            eval_tag=self.eval_key,
            seed=self.seed,
            version_dir=self.version_dir(),
            prediction_file=registration["prediction_file"],
            test_file=registration["test_file"],
            label=registration["label"],
            color=registration["color"],
            training_plots=metrics.get("plot_dir"),
            onnx_file=onnx,
            onnx_copy=onnx_copy,
            efficiency_plots=efficiency,
            roc_plots=roc,
            skipped_plots=skipped,
            region=self.region or None,
            event_file=self.event_info_path,
            journal=journal.journal_path(self.journal_base),
        )

        self.publish_message("")
        self.publish_message("model:            {}".format(self.model_key))
        if self.eval_key:
            self.publish_message("evaluation:       {}".format(self.eval_key))
            self.publish_message("test file:        {}".format(registration["test_file"]))
        self.publish_message("training:         {}".format(self.version_dir()))
        self.publish_message("prediction:       {}".format(registration["prediction_file"]))
        if metrics:
            self.publish_message("training plots:   {}".format(metrics["plot_dir"]))
        if onnx:
            self.publish_message("onnx model:       {}".format(onnx))
        if onnx_copy:
            self.publish_message("copied to:        {}".format(onnx_copy))
        for name, path in sorted(efficiency.items()):
            self.publish_message("efficiency plots: {}".format(path))
        for name, path in sorted(roc.items()):
            self.publish_message("ROC plots:        {}".format(path))
        for name in sorted(skipped):
            self.publish_message(
                "not made:         {} ({})".format(name, skipped[name])
            )
        self.publish_message("summary:          {}".format(self.output().path))
        self.publish_message(
            "journal:          {}".format(journal.journal_path(self.journal_base))
        )
        self.publish_message(
            "log:              {}".format(journal.transcript_path(self.journal_base))
        )
