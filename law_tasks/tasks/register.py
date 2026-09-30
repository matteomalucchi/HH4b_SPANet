"""Registration of the model in the efficiency and ROC configurations."""

import json
import os

import law
import luigi

from law_tasks import eventinfo, naming, registry
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
    higgs = luigi.ChoiceParameter(
        default="auto",
        choices=["auto", "yes", "no"],
        description="whether the prediction holds the Higgs pairing, i.e. the "
        "'higgs' key of the entry; 'auto' takes it from the resonances of the "
        "event file; default: auto",
    )
    vbf = luigi.ChoiceParameter(
        default="auto",
        choices=["auto", "yes", "no"],
        description="whether the prediction holds the VBF pairing, i.e. the "
        "'vbf' key of the entry; 'auto' takes it from the resonances of the "
        "event file; default: auto",
    )
    resonances = luigi.Parameter(
        default="",
        description="set of resonances the efficiency script pairs with, i.e. "
        "a key of RESONANCES_DICT in utils/performance/efficiency_functions.py "
        "('DEFAULT_RESONANCES', 'OLD_RESONANCES'); default: the one matching "
        "the EVENT section of the event file",
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

    @staticmethod
    def _flag(choice, derived):
        """``auto`` keeps what the event file says, ``yes``/``no`` force it."""
        return derived if choice == "auto" else choice == "yes"

    def derived_keys(self):
        """The jet and resonance keys of the entries, from the event file.

        ``jet_coll_higgs``, ``jet_coll_vbf`` and ``n_higgs_jets`` describe the
        file and belong to both entries; the index offsets and the resonance
        set describe the prediction and belong to the model entry alone.  Both
        are overridden by --extra-spanet-keys / --extra-true-keys.
        """
        info = self.event_info
        slots = eventinfo.input_slots(self.evaluation_file, info.needs_slots())

        model_keys = info.model_keys(slots)
        true_keys = info.collection_keys()
        if self.resonances:
            model_keys["resonances"] = self.resonances

        model_keys["higgs"] = self._flag(self.higgs, info.has_higgs)
        model_keys["vbf"] = self._flag(self.vbf, info.has_vbf)
        self.publish_message(
            "event file: {}".format(os.path.basename(info.path))
        )
        self.publish_message(
            "jets and resonances: {}".format(
                ", ".join("{}={}".format(k, v) for k, v in sorted(model_keys.items()))
            )
        )
        return model_keys, true_keys

    def run(self):
        self.check_no_overwrite(
            [target.path for target in self.output().values()], what="configuration"
        )

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

        label = self.label
        if not label and self.eval_key:
            # keep the legend unambiguous when a model is evaluated on
            # several samples
            label = "{} - {}".format(naming.derive_label(self.model_key), self.eval_key)

        model_keys, true_keys = self.derived_keys()
        model_keys.update(json.loads(self.extra_spanet_keys or "{}"))
        true_keys.update(json.loads(self.extra_true_keys or "{}"))

        spanet_entry, true_entry = registry.build_entries(
            self.model_key,
            prediction_file=prediction,
            test_file=evaluation_file,
            color=color,
            label=label or None,
            true_key=true_key,
            higgs=model_keys.pop("higgs"),
            vbf=model_keys.pop("vbf"),
            extra_spanet=model_keys,
            extra_true=true_keys,
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
            event_file=self.event_info_path,
            spanet_entry=spanet_entry,
            true_entry=true_entry,
        )
