"""Registration of the model in the efficiency and ROC configurations."""

import json
import os

import law
import luigi

from law_tasks import naming, registry
from law_tasks.base import ModelTask
from law_tasks.tasks.predict import Predict


class RegisterModel(ModelTask):
    """Write the efficiency/ROC configurations used to plot this model.

    Two small modules are generated: they import the tracked base
    configuration -- so every model that is active there is drawn as well --
    and add the entries of this model.  With ``--update-base-config`` the
    entries are in addition appended to the tracked configuration itself.
    """

    label = luigi.Parameter(
        default="",
        description="legend label; default: derived from the options basename",
    )
    color = luigi.Parameter(
        default="",
        description="plot color; default: the first unused color of the palette",
    )
    true_key = luigi.Parameter(
        default="",
        description="key of the truth entry; default: the existing entry pointing "
        "at the test file, else derived from the options basename",
    )
    vbf = luigi.BoolParameter(
        default=True,
        description="mark the entry as a VBF model; default: True",
    )
    baseline_models = luigi.Parameter(
        default="all",
        description="models of the base configuration to keep for comparison: "
        "'all', 'none' or a comma separated list of keys; default: all",
    )
    extra_spanet_keys = luigi.Parameter(
        default="",
        description="JSON dict of additional keys for the spanet_dict entry",
    )
    extra_true_keys = luigi.Parameter(
        default="",
        description="JSON dict of additional keys for the true_dict entry",
    )
    update_base_config = luigi.BoolParameter(
        default=False,
        significant=False,
        description="also append the entries to the tracked configurations; "
        "default: False",
    )

    def requires(self):
        return self.clone(Predict)

    @property
    def config_dir(self):
        return os.path.join(self.cfg.work_dir, "configs", self.model_key)

    def config_path(self, kind):
        return os.path.join(
            self.config_dir, "{}_configuration_{}.py".format(kind, self.model_key)
        )

    def output(self):
        return {
            "efficiency": law.LocalFileTarget(self.config_path("efficiency")),
            "roc": law.LocalFileTarget(self.config_path("roc")),
            "summary": law.LocalFileTarget(
                os.path.join(self.config_dir, "registration.json")
            ),
        }

    def _pick_color(self, modules):
        if self.color:
            return self.color

        # keep the color of the model if it is already known to a configuration
        for module in modules:
            entry = getattr(module, "spanet_dict", {}).get(self.model_key)
            if entry and entry.get("color"):
                return entry["color"]

        return naming.pick_color(registry.used_colors(modules))

    def run(self):
        prediction = self.input().path
        evaluation_file = self.evaluation_file

        base_configs = {
            "efficiency": self.cfg.eff_base_config,
            "roc": self.cfg.roc_base_config,
        }
        modules = [registry.load_config_module(path) for path in base_configs.values()]

        if self.true_key:
            true_key, reused = self.true_key, False
        else:
            true_key, reused = registry.resolve_true_key(
                modules, evaluation_file, naming.derive_true_key(self.model_key)
            )
        self.publish_message(
            "truth entry: {}{}".format(true_key, " (existing)" if reused else "")
        )
        color = self._pick_color(modules)

        spanet_entry, true_entry = registry.build_entries(
            self.model_key,
            prediction_file=prediction,
            test_file=evaluation_file,
            color=color,
            label=self.label or None,
            true_key=true_key,
            vbf=self.vbf,
            extra_spanet=json.loads(self.extra_spanet_keys or "{}"),
            extra_true=json.loads(self.extra_true_keys or "{}"),
        )

        for kind, base_config in base_configs.items():
            source = registry.render_module(
                self.model_key,
                base_config,
                spanet_entry,
                true_key,
                true_entry,
                baseline_models=self.baseline_models,
            )
            path = registry.write_module(self.config_path(kind), source)
            self.publish_message("wrote {}".format(path))

            if self.update_base_config:
                modified = registry.update_base_config(
                    base_config, self.model_key, spanet_entry, true_key, true_entry
                )
                self.publish_message(
                    "updated {} in {}".format(modified or "nothing", base_config)
                )

        self.write_marker(
            self.output()["summary"],
            model_key=self.model_key,
            label=spanet_entry["label"],
            color=color,
            true_key=true_key,
            prediction_file=prediction,
            test_file=evaluation_file,
        )
