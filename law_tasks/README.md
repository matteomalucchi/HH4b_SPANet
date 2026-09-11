# law pipeline: from the coffea files to the performance plots

[law](https://github.com/riga/law) tasks that chain the whole workflow of a
SPANet model: **convert** the coffea outputs into h5 inputs and **transfer**
them to the training machine, submit (or reuse) the **training**, compute the
**predictions**, plot the **training metrics**, register the model in the
performance configurations and produce the **efficiency** and **ROC** plots.

The chain spans two machines, as it does by hand: the conversion runs where
the coffea files are, everything else runs on lxplus.

```
analysis machine                     lxplus
----------------                     ------
hh4b.Dataset  --- rsync to EOS --->  hh4b.Performance
```

Every task knows its outputs, so nothing is computed twice: rerunning the
pipeline after a crash, or for a model that is already trained, only executes
what is missing.

## Setup

On **lxplus**, all commands run inside the SPANet virtual environment (e.g.
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

On the **analysis machine** (the one with the coffea files) only the dataset
tasks run, in the environment that reads coffea. `SPANET_ENV_DIR` is not
needed there; `law` has to be installed in that environment:

```bash
export SPANET_COFFEA_BASE="/work/${USER}/out_hh4b"          # where the coffea outputs live
export SPANET_REMOTE_HOST="<cern user>@lxplus.cern.ch"      # default: $USER@lxplus.cern.ch
export SPANET_REMOTE_INPUT_DIR="/eos/user/x/xyz/spanet_infos/spanet_inputs"

cd HH4b_SPANet
source setup_law.sh
```

## Step 0: the inputs (on the analysis machine)

```bash
law run hh4b.Dataset --dataset vbf_ggf_all_klambda_dnnvars_nokincut_higgsglobal
```

replaces the manual

```bash
cd <coffea dir>
python utils/dataset/coffea_to_h5_direct.py --input output_all.coffea --output <prefix> \
    --regions <region> <region> --class-labels GluGlu VBF -j <jets> -jg <jet-like globals>
rsync <prefix>*<collection>_*.h5 <user>@lxplus.cern.ch:<eos input dir>/
```

| task | what it does |
|---|---|
| `hh4b.ConvertDataset` | runs `coffea_to_h5_direct.py`; its outputs are the h5 files, so a dataset that is already converted is not converted again |
| `hh4b.TransferDataset` | creates the destination directory and `rsync`s the h5 files to the training machine |
| `hh4b.Dataset` | wrapper, writes a summary with the `training_file` path to put into the options file |

The datasets live in `law_tasks/datasets.yaml` (`dataset_config` in `law.cfg`):

```yaml
defaults:                       # applied to every dataset
  coffea_file: output_all.coffea
  class_labels: [GluGlu, VBF]
  jets: JET_COLLECTIONS_VBF_PAIRING_AFTER_HIGGS_PAIRING_TOTAL
  jet_like_global_vars: JET_LIKE_GLOBAL_HIGGS_ORDERED

datasets:
  vbf_ggf_all_klambda_dnnvars_nokincut_higgsglobal:
    coffea_dir: VBF/out_ggf_vbf_spanet_input_..._vbfregions   # relative to coffea_base
    output_prefix: FixMASK_AllKlambda_..._JetGoodProvHiggsPaddedGlobal_
    regions: [hh4b_vbf_..._nokincut_region, hh4b_vbf_..._nokincut_region]
    collections: [JetGoodVBFMergedProvVBFPadded_JetGoodProvHiggsPadded]
    remote_dir: vbf/out_ggf_vbf_spanet_input_..._vbfregions   # relative to remote_input_base
```

Fields: `coffea_dir`, `coffea_file`, `output_dir` (default: the coffea
directory), `output_prefix`, `regions`, `class_labels`, `jets`, `global_vars`,
`jet_like_global_vars`, `max_jets`, `convert_args` (anything else for the
converter), `collections` (which jet collection groups to transfer, default:
all) and `remote_dir`.

Every one of them is also a command line option, so a dataset that is not in
the file needs no edit:

```bash
law run hh4b.Dataset --dataset my_study \
    --coffea-dir VBF/out_my_study --output-prefix My_Study_ \
    --regions "my_region my_region" --remote-dir vbf/out_my_study
```

### Which files are produced

`coffea_to_h5_direct.py` writes one `<prefix><jet collection group>_train.h5`
and `_test.h5` pair per jet collection group, and a named group such as
`JET_COLLECTIONS_VBF_PAIRING_AFTER_HIGGS_PAIRING_TOTAL` expands to several
groups. The tasks expand the group the same way, which is how they know their
outputs up front. `collections` selects the groups that are worth copying.

Once the transfer is done, the summary prints the `training_file` to put into
the options file, e.g.

```
training_file entries for the options file:
  "JetGoodVBFMergedProvVBFPadded_JetGoodProvHiggsPadded": "/eos/user/x/xyz/spanet_infos/spanet_inputs/vbf/out_..._vbfregions/FixMASK_..._train.h5"
```

From there on, everything runs on lxplus.

## The one command (on lxplus)

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
| coffea outputs | `coffea_base` | `$SPANET_COFFEA_BASE` | the current directory |
| dataset list | `dataset_config` | `$SPANET_DATASET_CONFIG` | `law_tasks/datasets.yaml` |
| conversion env | `conversion_env` | `$SPANET_CONVERSION_ENV` | the environment law runs in |
| transfer target | `remote_host`, `remote_input_base` | `$SPANET_REMOTE_HOST`, `$SPANET_REMOTE_INPUT_DIR` | `$USER@lxplus.cern.ch`, the remote user's `spanet_infos/spanet_inputs` |
| h5 inputs (lxplus) | `input_base` | `$SPANET_INPUT_DIR` | `<eos_base>/spanet_inputs` |
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

The dataset tasks are the exception: they run on the analysis machine in its
own environment, so they never enter the container unless `--apptainer yes` is
given, and they only activate `conversion_env` if it is configured.

Flags that are on by default are switched off by passing the value explicitly,
e.g. `--gpu False` to predict on the CPU or `--vbf False` for a model that is
not a VBF one.
