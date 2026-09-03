# law pipeline: from the training to the performance plots

[law](https://github.com/riga/law) tasks that chain the whole workflow of a
SPANet model: submit (or reuse) the **training**, compute the **predictions**,
plot the **training metrics**, register the model in the performance
configurations and produce the **efficiency** and **ROC** plots.

Every task knows its outputs, so nothing is computed twice: rerunning the
pipeline after a crash, or for a model that is already trained, only executes
what is missing.

## Setup

All commands run inside the SPANet virtual environment (e.g.
`spanet_env_test_eos`), *outside* the apptainer container: the tasks enter the
container themselves whenever a payload needs it.

```bash
# once, e.g. in the .bashrc
export SPANET_MAIN_DIR="/afs/cern.ch/user/${USER:0:1}/${USER}"                       # SPANet + HH4b_SPANet checkouts
export SPANET_ENV_DIR="/eos/user/${USER:0:1}/${USER}/spanet_infos/spanet_env_test_eos"  # virtual environment
export EOS_SPANET="/eos/user/${USER:0:1}/${USER}/spanet_infos/spanet_outputs"        # where out_spanet_outputs lives

# in every session, from the repository root
cd $SPANET_MAIN_DIR/HH4b_SPANet
source setup_law.sh
```

`setup_law.sh` activates the environment, exports `LAW_CONFIG_FILE`, makes the
`law_tasks` package importable and builds the task index (needed for the shell
auto-completion).  `law` itself is part of `requirements.txt`; install it with
`pip install law` if the environment predates it.

## The one command

```bash
law run hh4b.Performance \
    --options-file options_files/HH4b/vbf_ggf/hh4b_pairing_vbf_ggf_all_Klambda_VBFPairing_JetHiggsGlobal_DNNVars_VBFNoKinCut_ClassLoss7.json \
    --seed 100
```

This is the equivalent of the manual chain

```bash
python3 jobs/submit_jobs_seed.py -c jobs/config/training_1gpu_1d.yaml -s 100:100 -o <options> -out $EOS_SPANET
# ... wait for the job, then, inside the container:
python -m spanet.predict ./ predict_<test>.h5 -tf <test file> --gpu
python scripts/plot_training_metrics.py -d <version dir>
# ... edit the two performance configurations by hand, then:
python3 utils/performance/efficiency_studies.py ...   # three times
python3 utils/roccurves/ROC_plots.py ...              # twice
```

and does, in order:

| task | what it does |
|---|---|
| `hh4b.Training` | submits the training to HTCondor and waits for it, **or** adopts an already trained `version_N` |
| `hh4b.Predict` | `spanet.predict` on the test file derived from the training file |
| `hh4b.TrainingMetrics` | `scripts/plot_training_metrics.py` on the version directory |
| `hh4b.RegisterModel` | writes the efficiency/ROC configurations containing this model |
| `hh4b.EfficiencyPlots` | one `efficiency_studies.py` run per entry of `[efficiency_plots]` |
| `hh4b.RocPlots` | one `ROC_plots.py` run per entry of `[roc_plots]` |
| `hh4b.Performance` | wrapper, writes a summary with every produced path |

Useful law flags: `--print-status -1` (what is done and what is missing),
`--print-deps -1`, `--remove-output 0` (drop the outputs of a task and rerun
it), `--workers 4`, `--local-scheduler` (default when no central scheduler is
configured).

Single steps can be run on their own, e.g. only the plots of a model that is
already predicted:

```bash
law run hh4b.EfficiencyPlots --options-file <options> --seed 100
law run hh4b.RocPlot --options-file <options> --plot-name vbf_presel
```

## Derived names

Everything follows from the options file, exactly like in the manual
procedure:

| value | rule | example |
|---|---|---|
| test file | `training_file` with `_train.h5` -> `_test.h5` and every `PtFlatten` removed | `..._vbfNoKinCut..._test.h5` |
| prediction | `predict_<test basename>` in the version directory | `predict_FixMASK_..._test.h5` |
| `true_dict` key | the existing entry pointing at the test file, else the options basename with `hh4b_pairing_vbf_ggf_all_Klambda_` -> `9jets_all_Klambda_` and the training-only tokens (`ClassLoss7`, `300e`, `PtFlatten`) dropped | `9jets_all_Klambda_VBFPairing_JetTotal_DNNVars_VBFNoKinCut` |
| label | tokens of the options basename joined with ` - `, `DNNVars` -> `DNN Vars`, ` Train` after `VBFNoKinCut` | `VBF pair+clas - JetTotal - DNN Vars - VBFNoKinCut Train - ClassLoss7` |
| color | the color the model already has in a configuration, else the first unused one of the palette (identical in both configurations) | `teal` |
| plot directory | `plots_` + options basename without the `hh4b_pairing_vbf_ggf_all_Klambda_` prefix | `plots_VBFPairing_JetTotal_DNNVars_VBFNoKinCut_ClassLoss7` |

Each of them can be overridden: `--test-file`, `--label`, `--color`,
`--true-key`, `--plot-dir`, and `--extra-spanet-keys` / `--extra-true-keys`
(JSON dicts) for entries such as `{"jet_coll": "JetVBF"}`.

## The generated configurations

`hh4b.RegisterModel` does **not** edit the configurations tracked in git.  It
writes

```
<work_dir>/configs/<model>/efficiency_configuration_<model>.py
<work_dir>/configs/<model>/roc_configuration_<model>.py
```

which import `utils/performance/efficiency_configuration_vbf_ggf.py` and
`utils/roccurves/roc_configuration_vbf_ggf.py` and add the entries of the new
model.  All models that are active in those base configurations are therefore
still drawn next to the new one; `--baseline-models none` (or a comma
separated list of keys) restricts the comparison.

To keep the new model permanently in the tracked configuration as well, add
`--update-base-config`: the entries are appended to the base files if they are
not there yet.

## Configuration

`law.cfg` in the repository root documents every option; nothing has to be set
because each one falls back to an environment variable and then to a default
derived from `$USER`:

| what | law.cfg (`[hh4b_spanet]`) | environment | default |
|---|---|---|---|
| checkouts | `spanet_main_dir` | `$SPANET_MAIN_DIR` | parent of this repository |
| virtual env | `spanet_env_dir` | `$SPANET_ENV_DIR` | `$VIRTUAL_ENV` |
| output base | `eos_base` | `$SPANET_EOS_BASE` | `/eos/user/${USER:0:1}/$USER/spanet_infos` |
| trainings | `output_base` | `$EOS_SPANET` | `<eos_base>/spanet_outputs` |
| efficiency plots | `eff_plot_base` | `$SPANET_EFF_PLOT_DIR` | `<eos_base>/spanet_eff_plots/vbf` |
| ROC plots | `roc_plot_base` | `$SPANET_ROC_PLOT_DIR` | `<eos_base>/spanet_roc_curves` |
| generated configs | `work_dir` | `$SPANET_LAW_WORK_DIR` | `<eos_base>/law_work` |
| container | `apptainer_image`, `apptainer_binds` | `$SPANET_APPTAINER_IMAGE`, `$SPANET_APPTAINER_BINDS` | cmsml image; `/afs`, `/cvmfs`, the EOS home of `$USER` and all directories above |

The `[efficiency_plots]` and `[roc_plots]` sections define which plots are
produced: the key is the subdirectory, the value the arguments handed to the
plotting script.  Add a line there to add a plot to the pipeline.

To read samples from somebody else's EOS area, add it to the binds:

```bash
export SPANET_APPTAINER_BINDS="/eos/user/m/mmalucch,/eos/user/t/tharte"
```

The same variable is used by `jobs/submit_to_condor.py` for the training jobs.

## Trainings

* An existing trained `version_N` is reused.  `--force-training` starts a new
  training anyway, `--model-version N` pins a specific version.
* A job of this training that is still in the queue is picked up instead of
  submitting a second one.
* `--job-config jobs/config/training_1gpu_3d.yaml` selects the condor
  configuration, `--train-args "..."` forwards arguments to `spanet.train` and
  `--checkpoint <file>` resumes from a checkpoint.
* The task polls the queue every `--poll-interval` seconds (5 min) and gives up
  after `--max-wait-hours` (72).  Because a training takes hours, run law
  inside `tmux`/`screen`, or submit with `--no-wait` and rerun the pipeline
  once the job is done (the resubmission is skipped, the queued job is picked
  up again).
* `--local-training` runs `jobs/training.sh` in the current session instead
  (use `lxplus-gpu`).

## Containers

Payloads that need the CMS ML image (prediction, plots) are wrapped in
`apptainer exec ... bash -c "source <env>/bin/activate && ..."` automatically.
`--apptainer no` skips the container (when law is already started inside one),
`--apptainer yes` forces it; the default `auto` detects it.

Flags that are on by default are switched off by passing the value explicitly,
e.g. `--gpu False` to predict on the CPU or `--vbf False` for a model that is
not a VBF one.
