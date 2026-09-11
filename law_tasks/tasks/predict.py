"""Evaluation of a trained model on the corresponding test file."""

import json
import os

import law
import luigi

from law_tasks.base import ModelTask
from law_tasks.tasks.training import Training


class Predict(ModelTask):
    """Run ``spanet.predict`` on the test file belonging to the training file."""

    gpu = luigi.BoolParameter(
        default=True,
        significant=False,
        description="evaluate the network on the GPU; default: True",
    )
    predict_args = luigi.Parameter(
        default="",
        description="additional arguments forwarded to spanet.predict; default: empty",
    )
    prediction_checkpoint = luigi.Parameter(
        default="",
        description="checkpoint inside the version directory to evaluate; "
        "default: the one chosen by spanet.predict",
    )

    def requires(self):
        return self.clone(Training)

    def output(self):
        version = self.resolve_version()
        if version is None:
            # the training has not run yet, the path is only known afterwards
            return self.marker("prediction_pending.json")
        return law.LocalFileTarget(self.prediction_path(version))

    def run(self):
        with open(self.input().path) as fobj:
            version = json.load(fobj)["version"]

        version_dir = self.version_dir(version)
        evaluation_file = self.evaluation_file
        if not os.path.exists(evaluation_file):
            raise RuntimeError(
                "test file '{}' does not exist; pass an explicit --test-file".format(
                    evaluation_file
                )
            )

        command = "cd {dir} && python -m spanet.predict ./ {name} -tf {test}".format(
            dir=version_dir, name=self.prediction_name, test=evaluation_file
        )
        if self.prediction_checkpoint:
            command += " -ckpt {}".format(self.prediction_checkpoint)
        if self.gpu:
            command += " --gpu"
        if self.predict_args:
            command += " " + self.predict_args

        self.run_command(command, gpu=self.gpu)

        prediction = self.prediction_path(version)
        if not os.path.exists(prediction):
            raise RuntimeError(
                "spanet.predict did not create {}".format(prediction)
            )
        self.publish_message("wrote {}".format(prediction))
