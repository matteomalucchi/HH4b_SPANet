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
converter, e.g. the weight normalization, see below), `collections` (which jet
collection groups to transfer, default: all) and `remote_dir`.

Every one of them is also a command line option, so a dataset that is not in
the file needs no edit:

```bash
law run hh4b.Dataset --dataset my_study \
    --coffea-dir VBF/out_my_study --output-prefix My_Study_ \
    --regions "my_region my_region" --remote-dir vbf/out_my_study
```

### Weights, and any other converter flag

`coffea_to_h5_direct.py` writes the coffea `weight` column into
`WEIGHTS/weight` **as it is**: it normalizes only when asked, so without a
flag the h5 carries whatever the coffea production put there, which can be
many orders of magnitude away from one.  The two flags that change this are

| flag | what it does |
|---|---|
| `-n` / `--norm-weights` | divides by `sum_genweights` of the dataset |
| `-bw class` / `-bw sample` | rescales so each class (or each sample) sums to 1 |

They are mutually exclusive.  Everything the converter accepts and the tasks
do not model themselves goes through `convert_args`, in the dataset entry:

```yaml
  vbf_ggf_all_klambda_dnnvars_nokincut_higgsglobal:
    ...
    convert_args: "-n"        # or: "-bw class", "-n -rw", ...
```

or on the command line, where the value **has to be attached with `=`** (or
start with a space), otherwise `-n` is read as a law option and not as its
value:

```bash
law run hh4b.Dataset --dataset <name> --convert-args="-n"
law run hh4b.Dataset --dataset <name> --convert-args="-n -m 5 5"   # several of them
```

Changing the flags does not change the file names, so the h5 files of an
earlier conversion are in the way: add `--overwrite` to replace them, on
`hh4b.Dataset` to redo the conversion *and* the copy to EOS, or on
`hh4b.ConvertDataset` to redo the conversion alone.

```bash
law run hh4b.Dataset --dataset <name> --convert-args="-n" --overwrite
```

Check what came out with

```python
import h5py, numpy as np
with h5py.File("<prefix><collection>_train.h5") as h:
    w = h["WEIGHTS/weight"][:]
    print(w.mean(), w.sum(), np.abs(w).max())
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
it), `--workers 4`, `--log-level DEBUG` (luigi's verbose output).

The tasks run without a central scheduler: `law.cfg` sets
`[luigi_core] local_scheduler: True`, so nothing has to be started before
`law run`.  Without it luigi tries to reach `luigid` on `localhost:8082` and
waits in `Failed connecting to remote scheduler ... Retrying attempt 2 of 3`.
To use a central scheduler instead, set that option to `False` and start
`luigid`.

Single steps can be run on their own, e.g. only the plots of a model that is
already predicted:

```bash
law run hh4b.EfficiencyPlots --options-file <options> --seed 100
law run hh4b.RocPlot --options-file <options> --plot-name vbf_presel
```

## Evaluate an existing model on another test file

Nothing has to be trained again: `hh4b.Training` adopts the trained
`version_N` that is already there, so the same command evaluates a model on a
different sample by pointing it at that sample.

```bash
law run hh4b.Performance \
    --options-file options_files/HH4b/vbf_ggf/<model>.json --seed 100 \
    --test-file /eos/user/x/xyz/spanet_infos/spanet_inputs/vbf/<dir>/<other>_test.h5
```

It predicts on that file, registers the model against it and produces every
efficiency and ROC plot, as for the model's own test file.

The evaluation gets a name, printed as `evaluation:` in the summary and
derived from the tokens that the two file names do not share (e.g.
`vbfPresel...` for a model whose own test file is the `vbfNoKinCut` one), or
from the directory when the two names are equal. It keeps the evaluations
apart, so a model evaluated on several samples does not overwrite itself:

| | own test file | another test file |
|---|---|---|
| prediction | `predict_<test>.h5` | `predict_<evaluation>_<test>.h5` |
| configurations | `<work_dir>/configs/<model>/` | `<work_dir>/configs/<model>_<evaluation>/` |
| plots | `plots_<model>/` | `plots_<model>_<evaluation>/` |
| summary | `law/performance.json` | `law/performance_<evaluation>.json` |
| legend | the usual label | the label plus ` - <evaluation>` |

The evaluation is part of the prediction name as well, so two samples whose
files share a basename but sit in different directories cannot produce the
same prediction.  The training metric plots are *not* redone: they describe
the training, not the sample, so they are made once, with the model's own test
file.

`--eval-tag <name>` replaces the derived name when it is too long or not
telling enough, and `--plot-dir` still overrides the plot directory outright.
A model trained by somebody else is evaluated by adding `--output-base
<their out_spanet_outputs parent>`; `--model-version N` pins a version other
than the latest.

Single steps work the same way, e.g. only the predictions:

```bash
law run hh4b.Predict --options-file <options> --test-file <other test file>
```

## What is overwritten, and when

law runs a step only when one of its outputs is missing.  Everything follows
from that:

* repeating a command that already went through does nothing at all;
* a command that stopped halfway carries on where it stopped;
* a result that is finished is never replaced -- unless you ask for it.

Asking for it is `--overwrite`, or `--overwrite-plots` when the data is to be
kept: "redo this step" and "replace what this step wrote" are the same thing,
so the question is always *which steps are redone*.

### What each step writes

| step | what it (re)writes when it runs |
|---|---|
| `hh4b.ConvertDataset` | `<prefix><collection>_{train,test}.h5` next to the coffea file |
| `hh4b.TransferDataset` | the same h5 files in the destination directory on the training machine |
| `hh4b.Training` | a new `version_N/` -- **only** with `--overwrite`, otherwise it adopts the one that is there |
| `hh4b.Predict` | `version_N/predict_<test file>.h5` |
| `hh4b.RegisterModel` | `<work_dir>/configs/<model>/{efficiency,roc}_configuration_<model>.py` and `registration.json` |
| `hh4b.TrainingMetrics` | `version_N/training_plots/` |
| `hh4b.EfficiencyPlot`, `hh4b.RocPlot` | everything the plotting script writes into `<plot base>/<plot dir>/<plot name>/` |
| `hh4b.Performance`, `hh4b.Dataset` | only their summary |

Every step also writes a small marker under `<run dir>/law/` (a dataset step:
under `<coffea dir>/law/`).  That is the bookkeeping law reads to know what is
done; it is rewritten whenever the step runs.

### Which steps a flag redoes

Two flags, and both reach every step below the one they are given to:

| flag | steps redone |
|---|---|
| *(none)* | the ones whose outputs are missing |
| `--overwrite-plots` | the step it is given to and every step below it, **except** the conversion, the transfer, the training and the prediction |
| `--overwrite` | the step it is given to and every step below it, whatever it is |

`--overwrite` redoes the data as well: it trains the model again, predicts
again, and on the analysis machine converts the coffea file again.  On
`hh4b.Performance` it is therefore the full chain, condor job included, which
takes as long as the first time.

`--overwrite-plots` is the one for everything that is drawn from a prediction
that is fine: it never costs a GPU or a conversion.

The training is the one step that is not replaced but *added to*: a new
`version_N` appears next to the one that is there, and everything below is
made from it.  The previous training, its checkpoints and its prediction stay
on disk.  `--model-version N` therefore still reaches them, and asking for
both at once (`--overwrite --model-version N`) is refused rather than guessed.

### Spelled out

With a model that is trained and predicted,

```bash
law run hh4b.Performance --options-file <options> --overwrite-plots
```

replaces exactly these:

```
<work_dir>/configs/<model>/efficiency_configuration_<model>.py
<work_dir>/configs/<model>/roc_configuration_<model>.py
<work_dir>/configs/<model>/registration.json
<eff plot base>/<plot dir>/<every efficiency plot>/*
<roc plot base>/<plot dir>/<every ROC plot>/*
<run dir>/version_N/training_plots/*
<run dir>/law/*.json                     (the markers of the steps above)
```

and leaves these untouched:

```
<run dir>/version_N/checkpoints/*        the training
<run dir>/version_N/predict_*.h5         the prediction
the h5 input files
utils/performance/..., utils/roccurves/...   the configurations tracked in git
everything that belongs to another --test-file / --eval-tag evaluation
```

The same command with `--overwrite` trains again.  It creates

```
<run dir>/version_N+1/checkpoints/*       the new training
<run dir>/version_N+1/predict_*.h5        its prediction
<run dir>/version_N+1/training_plots/*    its metric plots
```

replaces the same configurations, plots and markers as above -- they are named
after the model, so they now describe `version_N+1` -- and still leaves
`version_N` exactly as it was.

On the analysis machine, `--overwrite` is what makes a conversion run again
with different flags, replacing the h5 next to the coffea file and the copies
of them on the training machine:

```bash
law run hh4b.Dataset --dataset <name> --convert-args="-n" --overwrite
```

### When law redoes something you did not ask for

Only one case: a step whose outputs were made for a **training that has since
been replaced** counts as unfinished, and is redone without `--overwrite`.
See the next section.

### When law refuses instead

A step that would write into a directory holding files law did not put there
stops and names them:

| step | what it refuses to touch |
|---|---|
| `hh4b.TransferDataset` | files already in the destination directory on the training machine (checked over ssh) |
| `hh4b.TrainingMetrics`, `hh4b.EfficiencyPlot`, `hh4b.RocPlot` | a plot directory that exists and is not empty |

Typically these are plots made by hand, before the pipeline existed.  Either
`--overwrite-plots` to replace them, or `--plot-dir <other name>` to leave them
alone and send the new plots elsewhere.

What a step declares as its *own* output is not protected against that step:
law only runs it when one of those outputs is missing, so whatever is still
there is the leftover of an attempt that did not finish -- refusing it would
leave the step unable to ever complete.  A half written registration, for
instance, is simply rewritten:

```
<work_dir>/configs/<model>/registration.json     # there
<work_dir>/configs/<model>/*_configuration_*.py  # gone
```

## A new training replaces what was derived from the old one

Only the prediction file carries the `version_N` directory in its name; the
generated configurations, the plots and the markers are named after the model.
Every result therefore records the training it belongs to, and law redoes it
when that training is no longer the current one:

```bash
law run hh4b.Performance --options-file <options> --overwrite   # version_1
```

That is one command: it trains into `version_1`, predicts there, rewrites the
configurations against the new prediction and redraws the plots.  The same
happens when the training is made separately, or by somebody else -- a
`version_N` that appears is enough:

```bash
law run hh4b.Training --options-file <options> --overwrite   # version_1
law run hh4b.Performance --options-file <options>            # no flag needed
```

The second command finds the configurations and the plots of `version_0` and
redoes them, without `--overwrite`: the plots that are in the way are the ones
law itself made for `version_0`.  Plots that law did not make are still
protected.

Without this, the second command would have reported the whole chain complete
and the efficiency and ROC plots would have kept showing `version_0`.

`--model-version N` follows that version instead of the latest one.  The plot
directory is shared by every version of a model, so going back to an earlier
one redraws it; `--plot-dir` keeps the two apart.

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

Each of them can be overridden: `--test-file`, `--eval-tag`, `--label`,
`--color`, `--true-key`, `--plot-dir`, and `--extra-spanet-keys` /
`--extra-true-keys` (JSON dicts) for entries such as `{"jet_coll": "JetVBF"}`.

## The jets and the resonances, from the event file

The efficiency and the ROC scripts need to know which collection holds which
jets; the entries carry it, and the event file of the model already says it.
`hh4b.RegisterModel` reads `event_info_file` from the options file and fills
the keys in:

| key | where it comes from | in |
|---|---|---|
| `jet_coll_higgs` | the sequential input the Higgs daughters are taken from, or the one that carries the targets when there is no Higgs resonance | both entries |
| `jet_coll_vbf` | the sequential input of the VBF daughters, when it is not the same one | both entries |
| `n_higgs_jets` | `0` when the VBF jets have a collection of their own, otherwise the four leading jets of the single collection (the default of the script) | both entries |
| `offset_jet_idx_higgs`, `offset_jet_idx_vbf` | minus the slots of the collections *before* the one of that resonance: SPANet numbers the jets over its sequential inputs concatenated, the file stores them per collection | the model entry |
| `resonances` | the `RESONANCES_DICT` entry whose daughters are the ones of the event file: `h1: b1 b2`, `h2: b3 b4` is `OLD_RESONANCES`, `h2: b1 b2` is `DEFAULT_RESONANCES` | the model entry |

The number of slots of a collection is read from the file the model is
evaluated on (`INPUTS/<collection>/MASK`), so two collections of four and five
jets give what the configurations of this repository say by hand:

```python
"jet_coll_higgs": "JetHiggs",       # INPUTS: SEQUENTIAL: JetHiggs, JetVBF
"jet_coll_vbf": "JetVBF",           # EVENT:  h1/h2 on JetHiggs, vbf on JetVBF
"n_higgs_jets": 0,
"offset_jet_idx_higgs": 0,          # JetHiggs is the first collection
"offset_jet_idx_vbf": -4,           # JetHiggs has four slots
"resonances": "DEFAULT_RESONANCES",
```

A collection whose name contains `VBF` is taken to hold the VBF jets alone,
which is what makes `n_higgs_jets` zero; `--extra-true-keys` overrides it, and
overrides every other key, for a sample that does not follow the convention.

### Plots that cannot be made are not made

`efficiency_studies.py` pairs the Higgs jets unless it is given
`--ignore-higgs`, and the VBF jets when it is given `--vbf`.  A resonance that
the event file does not define is not in the prediction either, and the script
fails looking for it, so `hh4b.EfficiencyPlots` leaves those plots out:

```
not made:         HiggsEff (hh4b_..._JetVBF_DNNVars_JetHiggsGlobal.yaml defines no Higgs resonance)
```

They are listed like that at the end of `hh4b.Performance` and kept in its
summary under `skipped_plots`.  Asking for one by name stops with the same
explanation instead of running into the failure.

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

## What ran: the journal

Every `law run` writes what it did under `<work_dir>/journal`, one directory
per invocation, with `latest` pointing at the most recent one:

```
<work_dir>/journal/20260917_101530_31415/run.jsonl        the steps, in order
<work_dir>/journal/20260917_101530_31415/001_Training.log the output of a command
<work_dir>/journal/20260917_101530_31415/002_Predict.log
<work_dir>/journal/latest
```

`run.jsonl` holds one JSON line per event: a step that started, finished or
failed, and every bash command with the directory it ran in, its exit code,
how long it took and the file its output went to.  The output is shown while
it runs, exactly as before, *and* kept in that file.

```bash
cd <work_dir>/journal/latest

# what the run did, in order
python3 -c 'import json
for line in open("run.jsonl"):
    e = json.loads(line)
    print(e["time"], e["task"], e.get("state") or e["command"])'

# the commands alone, ready to be pasted into a shell
python3 -c 'import json
for line in open("run.jsonl"):
    e = json.loads(line)
    if e["event"] == "command":
        print(e["command"])'
```

The marker of every step keeps its own commands as well, so
`<run dir>/law/<step>.json` answers "what exactly was executed to produce
this" without looking for the run it belonged to, and `hh4b.Performance`
prints the path of the journal when it is done.

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

* An existing trained `version_N` is reused.  `--overwrite` starts a new
  training anyway, in a new `version_N`; `--model-version N` pins a specific
  version.
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
