# HH4b_SPANet

Repository with [SPANet](https://github.com/matteomalucchi/SPANet) configuration for HH4b analysis. Originally forked from <https://github.com/mmarchegiani/ttHbb_SPANet>.

## Running SPANet within the `cmsml` docker container

In order to use the SPANet package we use the prebuilt **apptainer** image for machine learning applications in CMS, [`cmsml`](https://hub.docker.com/r/cmsml/cmsml).

First we activate the apptainer environment on **lxplus** with the following command (Some of the paths may have to be edited according the the personal setup):

```bash
apptainer shell -B /afs -B /eos/user/${USER:0:1}/${USER} -B /eos/user/m/mmalucch/ -B /eos/user/t/tharte -B /etc/sysconfig/ngbauth-submit -B ${XDG_RUNTIME_DIR} --env KRB5CCNAME="FILE:${XDG_RUNTIME_DIR}/krb5cc" --nv /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmsml/cmsml:latest
```

> [!TIP]
> We advise to create an alias to activate the apptainer in your `.bashrc`, for example:
>
> ```bash
> alias spanet_singularity='apptainer shell -B /afs -B /eos/user/${USER:0:1}/${USER} -B /eos/user/m/mmalucch -B /eos/user/t/tharte -B /etc/sysconfig/ngbauth-submit -B ${XDG_RUNTIME_DIR} --env KRB5CCNAME="FILE:${XDG_RUNTIME_DIR}/krb5cc" --nv /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmsml/cmsml:latest'
> ```
>
> From now on the activation of the apptainer will be indicated with the alias `spanet_singularity`

All the common packages for machine learning applications are now available in a singularity shell.
We can proceed by installing `SPANet` in a virtual environment inside this Docker container:

```bash
# Clone locally the SPANet repository
git clone git@github.com:matteomalucchi/SPANet.git

# Clone locally the HH4b_SPANet repository
git clone git@github.com:matteomalucchi/HH4b_SPANet.git

# Enter the singularity
spanet_singularity

# Create a local virtual environment using the packages defined in the apptainer image
python -m venv --system-site-packages spanet_env

# Activate the environment
source spanet_env/bin/activate

cd HH4b_SPANet
pip install -r requirements.txt

# Install in EDITABLE mode
cd ../SPANet
pip install -e .

# Install the HEPPlotter class
pip install --upgrade  --no-cache-dir git+https://github.com/matteomalucchi/AnalysisConfigs.git
```

The next time the user enters in the apptainer the virtual environment needs to be activated.

```bash
#Enter the singularity
spanet_singularity

# Activate the virtual environment
source spanet_env/bin/activate
```

To check that SPANet is correctly installed in the environment, run the following command:

```bash
python -m spanet.train --help
```

> [!IMPORTANT]
> To Install the `HEPPlotter` class you can use
>
> ```bash
> pip install --upgrade  --no-cache-dir git+https://github.com/matteomalucchi/AnalysisConfigs.git
> ```
>
> This command should be executed every time you want to pull from the AnalysisConfigs repository and update the `HEPPlotter`.
> If it doesn't update, you should first uninstall it with `pip uninstall configs` and then install it again with the command above.

## Dataset creation

To convert the coffea files outputs of [PocketCoffea](https://pocketcoffea.readthedocs.io/en/latest/?badge=latest) (see [HH4b README](https://github.com/matteomalucchi/AnalysisConfigs/blob/main/configs/HH4b_common/README.md) for further information) into h5 files used as input for SPNANet, you can use `utils/dataset/coffea_to_h5_direct.py` script with the following instructions:

```bash
python utils/dataset/coffea_to_h5_direct.py --input <input_coffea_file> --output <output_h5_file>  --regions <list_of_regions_per_class> --class-labels <list_of_classes> --jets <jet_collections_to_convert> --max-jets <max_num_jets_or_pairing> --train-frac <fraction_used_for_training> [--no-shuffle] 

# example for ggf spanet training
python utils/dataset/coffea_to_h5_direct.py --input output_all.coffea --output spanet_training_input.h5  --regions 4b_region --class-labels GluGlu --jets JetTotalSPANetPtFlattenPadded JetTotalSPANetPadded --max-jets 5

# example for vbf ggf spanet training
python utils/dataset/coffea_to_h5_direct.py --input output_all.coffea --output spanet_training_input.h5  --regions 4b_region 4b_region --class-labels GluGlu VBF --jets JetTotalSPANetPtFlattenPadded JetTotalSPANetPadded --max-jets 9

# example for HH4b vs Bkg spanet classification 
python utils/dataset/coffea_to_h5_direct.py --input output_all.coffea --output spanet_training_input.h5  --regions 2b_signal_region_postW 4b_signal_region --class-labels DATA GluGlu --jets JetGoodFromHiggsOrdered --max-jets 5
```

> [!IMPORTANT]
> When creating on a file for training where pT of the jets is flattened, remember to also create the corresponding file where pT is not flattened to later evaluate the model!


> [!NOTE]
>See [utils/dataset/README.md](utils/dataset/README.md) for full instructions, all CLI options, and how to configure jet and global-variable collections.

<details>
<summary> Legacy dataset creation (outdated instructions)  </summary>

### Legacy dataset creation (outdated instructions)

#### Coffea to H5 conversion

In order to create the `.h5` dataset from the `.coffea` output file, one can use the following command:

```bash
cd HH4b_SPANet
python utils/dataset/coffea_to_h5.py -i input.coffea

# e.g.
python3 /work/tharte/HH4b_SPANet/utils/dataset/coffea_to_h5.py -i $1/output_all.coffea -o $TMPDIR/ -r -c 4b_region
```

This code can also be run in a slurm job using a small script. The script has to be adapted a bit and has hardcoded paths. But the idea is, to have such a script in the folder, where you run it and then you can just execute: `sbatch coffea_to_h5.sh`:

```
#!/bin/bash
#
#SBATCH --mem=6000M
#SBATCH --job-name=coffea_to_h5
#SBATCH --account=t3
#SBATCH --time 01:00:00
#SBATCH --cpus-per-task 24
#SBATCH -o %x-%j.out    # replace default slurm-SLURM_JOB_ID.out; %x is a job-name (or script name when there is no job-name)
#SBATCH -e %x-%j.err    # replace default slurm-SLURM_JOB_ID.err

echo HOME: $HOME 
echo USER: $USER 
echo SLURM_JOB_ID: $SLURM_JOB_ID
echo HOSTNAME: $HOSTNAME

# each worker node has local /scratch space to be used during job run
mkdir -p /scratch/$USER/${SLURM_JOB_ID}
export TMPDIR=/scratch/$USER/${SLURM_JOB_ID}

echo InputFileDir: $1/output_all.coffea

python /work/tharte/HH4b_SPANet/utils/dataset/coffea_to_h5.py -i $1/output_all.coffea -o $TMPDIR/ -r -c inclusive_region
cp $TMPDIR/* $1

rm -rf $TMPDIR
```

TODO: This script will be made more agnostic and put into the repo for easier use.

#### Coffea to Parquet conversion

In order to create the `.parquet` dataset from the `.coffea` output file, one can use the following command:

```bash
cd HH4b_SPANet
python utils/dataset/coffea_to_parquet.py -i input.coffea -o output_folder

# Explicit example
python3 /work/tharte/HH4b_SPANet/utils/dataset/coffea_to_parquet.py -i ./output_all.coffea -o . -c 4b_region
```

The script will produce an output file for each sample in the `.parquet` format, saved in the folder `output_folder`.

#### Parquet to H5 conversion

Once the `.parquet` file is saved, the `.h5` file in the SPANet format can be produced using the following command:

```bash
python utils/dataset/parquet_to_h5.py -i input.parquet -o output.h5

# Explicit example (saving to a scratch partition)
python3 /work/tharte/HH4b_SPANet/utils/dataset/parquet_to_h5.py -i ./*.parquet -o /scratch/<user>/166814/ -f 0.8
```

</details>

## Create the SPANet configuration

The SPANet configuration is composed of two files: the `event_file` and the `option_file`. Further information can be found on the SPANet repository at [EventInfo](https://github.com/matteomalucchi/SPANet/blob/master/docs/EventInfo.md) and [Options](https://github.com/matteomalucchi/SPANet/blob/master/docs/Options.md).

> [!TIP]
> When writing the path to the `event_file` in the `option_file`, you should use the absolute path to the `event_file`. In order to make it compatible with also other users, you can use the environment variables defined in [this section](#train-on-htcondor). An example of this can found in [this `option_file`](./options_files/HH4b/vbf_ggf/hh4b_pairing_vbf_ggf_pairing_classification.json), where the key is written like this:
>
> ```json
>"event_info_file": "${SPANET_MAIN_DIR}/HH4b_SPANet/event_files/HH4b/vbf_ggf/hh4b_vbf_ggf_pairing_classification.yaml",
>```

### Configuration examples

In the following you can find some example configurations for the various tasks:

- **Jet pairing**: [`event_file`](./event_files/HH4b/hh4b_5jet_btagWP.yaml), [`option_file`](./options_files/HH4b/1_14_2_h4b_5jets_ptvary_loose_300_btag_wp_newLeptonVeto_3L1Cut_UpdateJetVetoMap.json)
- **Signal-background classification**: [`event_file`](./event_files/HH4b/classification/hh4b_classification_trial.yaml),[`option_file`](./options_files/HH4b/classification/hh4b_classification_trial.json)
- **Jet pairing + Signal-background classification**: [`event_file`](./event_files/HH4b/vbf_ggf/hh4b_vbf_ggf_pairing_classification.yaml),[`option_file`](./options_files/HH4b/vbf_ggf/hh4b_pairing_vbf_ggf_pairing_classification.json)

## Train SPANet model locally

In order to train the SPANet model locally, run the following command inside the apptainer and the virtual environment:

```bash
#Enter the singularity
spanet_singularity

# Activate the virtual environment
source spanet_env/bin/activate

python -m spanet.train -of <options_file> --gpus 1
python -m spanet.train -of options_files/HH4b/vbf_ggf/hh4b_pairing_vbf_ggf_pairing_classification.json --gpus 1
```

## Train on HTCondor

In order to train the SPANet model on HTCondor, one must first define 2 environment variables `SPANET_MAIN_DIR` and `SPANET_ENV_DIR`. It's advisable to do it in the `.bashrc` to having to define them only once. An example of such variables is given below.

```bash
export SPANET_MAIN_DIR="/afs/cern.ch/user/m/mmalucch" # main directory where the SPANet and HH4b_SPANet repositories are saved
export SPANET_ENV_DIR="/afs/cern.ch/user/m/mmalucch/spanet_env" # path to the virtual environment 
```

Subsequently, one can use the following command outside the singularity but inside the venv:

```bash
# Activate the virtual environment
source spanet_env/bin/activate

python3 jobs/submit_jobs_seed.py -o <options_files/option_file.json> -c <jobs/config/config.yaml> -s <start_seed>:<end_seed> -a <"additional arguments to pass to spanet.train"> --suffix <directory_suffix> -out <output_dir>

# e.g.
python3 jobs/submit_jobs_seed.py -o options_files/HH4b/vbf_ggf/hh4b_pairing_vbf_ggf_pairing_classification.json -c jobs/config/training_1gpu_8h.yaml -s 100:100  -out /eos/user/m/mmalucch/spanet_infos/spanet_outputs/
```

### Tune the model on HTCondor

> [!IMPORTANT]
> Work in Progress

To run a hyperparameter scan, one can use the `spanet.tune` script, which can be run on HTCondor using the corresponding configuration. An example of the command is given in shown below. You can chose which hyperparameters and which values to scan in the `SPANet/spanet/tune.py` file.

```bash
# e.g.

python3 jobs/submit_jobs_seed.py -c jobs/config/tune_1gpu_20min.yaml -s 100:100 -o options_files/HH4b/vbf_ggf/hh4b_pairing_vbf_ggf_pairing_classification.json -out /eos/user/m/mmalucch/spanet_infos/spanet_outputs/
```

## Monitor training on TensorBoard

To monitor the training one can use TensorBoard with the following command inside the singularity:

```bash
#Enter the singularity
spanet_singularity

# Activate the virtual environment
source spanet_env/bin/activate

tensorboard --logdir <output_dir/version_[]>

# e.g.
tensorboard --logdir /eos/user/t/tharte/Analysis_data/spanet_output/version_0
```

This will print something like:

```
TensorBoard 2.X.X at http://localhost:6006/
```

### If running locally

If you are running on your local machine, simply open the link in your browser:

```
http://localhost:6006
```

### If running on a remote machine (e.g. lxplus)

Since TensorBoard runs on the remote machine’s `localhost`, you need to create an SSH tunnel to access it from your laptop.

From your **local machine**, run:

```bash
ssh -L 6006:localhost:6006 <user>@lxplus<node>.cern.ch
```

Then open in your local browser:

```
http://localhost:6006
```

This forwards your local port `6006` to the remote machine’s port `6006`, allowing you to access the TensorBoard interface securely.

### Monitoring multiple runs

If you want to compare different runs (e.g. `version_0`, `version_1`, `version_2`), point TensorBoard to the parent directory:

```bash
tensorboard --logdir /eos/user/t/tharte/Analysis_data/spanet_output/
```

TensorBoard will automatically display all available versions for comparison.

---

This allows you to monitor:

- Training and validation loss
- Classification metrics (e.g. accuracy)
- Learning rate schedules
- Other logged quantities

Press `CTRL+C` to stop the TensorBoard server.

## Compute predictions

In order to compute the predictions from a previously trained SPANet model, one has to run the following command in the singularity:

```bash
#Enter the singularity
spanet_singularity

# Activate the virtual environment
source spanet_env/bin/activate

python -m spanet.predict <log_directory> predicitons.h5 -tf input.h5 --gpu
```

where `<log_directory>` is the output folder where the checkpoints of the trained SPANet model are saved, `predicitons.h5` is the customizable name of the output file containing the predictions and `input.h5` is the input `.h5` file in SPANet format. With the `--gpu` flag one can profit from the available GPUs.

> [!IMPORTANT]
> When evaluating a model trained on a file where the jet pT was flattened, remember to evaluate it on a file where the pT is not flattened to get the correct performance!

> [!TIP]
> To use the gpu locally, connect to `ssh <user>@lxplus-gpu.cern.ch`

## Convert to onnx for further use

To use the model afterwards with different frameworks, the easiest way is to have an `onnx` file. This can be exported easily like this from the singularity:

```bash
#Enter the singularity
spanet_singularity

# Activate the virtual environment
source spanet_env/bin/activate

python -m spanet.export <path_to_training>/out_seed_trainings_100/version_0/ <output_file_name>.onnx --gpu
```

## Performance

This repo contains also a script to determine the pairing efficiency and the ROC of the models. It runs on the files gained from `spanet.predict`.

### Run the efficiency script

To add a new model, you just have to add a sub-dictionary to the `spanet_dict` in the configuration for the efficiency script you want to use (e.g. `utils/performance/efficiency_configuration.py`)

```python
# e.g.
spanet_dict = {
    ...
    '5_jets_pt_btag_wp_300e_allklambda':{
        'file': '/eos/user/t/tharte/Analysis_data/predictions/spanet_hh4b_5jets_300_ptreg_loose_s100_btag_wp.h5',
        'true': '5_jets_pt_true_wp_allklambda',
        'label': 'SPANet btag WP',
        'color': 'orange',
    },
    ...
}
```

and then add the corresponding item in the `true_dict` (if not already present)

```python
#e.g.
true_dict = {
    ...
    "5_jets_pt_true_wp_allklambda": {
        "name": "/eos/user/t/tharte/Analysis_data/spanet_samples/loose_MC_postEE_btagWP/output_JetGood_test.h5",
        "klambda": "postEE",
    },
    ...
}
```

> [!IMPORTANT]
> When evaluating the performance of a model trained on a file where the jet pT was flattened, remember to put here the files where the pT is not flattened for both the prediction and true files!

And then in the target folder, you can run this inside the singularity to plot the efficiency for different configurations.

```bash
#Enter the singularity
spanet_singularity

# Activate the virtual environment
source spanet_env/bin/activate

cd HH4b_SPANet

# plot the efficiency as a function of k-lambda and plot the Higgs mass histograms
python utils/performance/efficiency_studies.py -pd <plot_dir> -k [-conf <relative_path_to_conf>] [--histo-mass]

# Alternatively just run on the data samples, to analyse the mass sculpting:
python utils/performance/efficiency_studies.py -pd <plot_dir> -d --histo-mass

# To only on ggF events (if the file has a mixture of ggF and VBF events where the class indicating the VBF is 1):
python3 utils/performance/efficiency_studies.py -pd <plot_dir> -c 0 -k

## VBF configurations ##

# To compute the efficiency also for vbf jets on actual vbf events (if the file has a mixture of ggF and VBF events where the class indicating the VBF is 1):
python utils/performance/efficiency_studies.py -pd <plot_dir> --vbf -c 1 -conf utils/performance/efficiency_configuration_vbf_ggf.py  -k

# compute only vbf pairing (ignore higgs pairing) for vbf events 
python utils/performance/efficiency_studies.py -pd <plot_dir> --vbf -c 1 -ih -conf utils/performance/efficiency_configuration_vbf_ggf.py  -k

# compute only vbf pairing (ignore higgs pairing) for vbf events with the vbf preselection  (mjj>400 and delta eta<3.5)
python utils/performance/efficiency_studies.py -pd <plot_dir> --vbf -c 1 -ih -r vbf_presel  -conf utils/performance/efficiency_configuration_vbf_ggf.py  -k
 
# compute only vbf pairing (ignore higgs pairing) for vbf events with the vbf jets requirement (ask just that there are additional jets but w/o kin cuts)
python utils/performance/efficiency_studies.py -pd <plot_dir> --vbf -c 1 -ih -r vbf_no_kin_cuts  -conf utils/performance/efficiency_configuration_vbf_ggf.py  -k

# run Higgs pairing (without VBF pairing) on ggF events
python utils/performance/efficiency_studies.py -pd <plot_dir>  -c 0 -conf utils/performance/efficiency_configuration_vbf_ggf.py --histo-mass  -k

# run Higgs pairing (without VBF pairing) on VBF events
python utils/performance/efficiency_studies.py -pd <plot_dir>  -c 1 -conf utils/performance/efficiency_configuration_vbf_ggf.py --histo-mass  -k

# run Higgs pairing (without VBF pairing) on ggF+VBF events
python utils/performance/efficiency_studies.py -pd <plot_dir>  -conf utils/performance/efficiency_configuration_vbf_ggf.py --histo-mass  -k

```

> [!TIP]
> To pass the configuration with the input files for the efficiency computation through the argument `-conf`, use the relative path from where you are executing the script.
>
> - ggF analysis: `HH4b_SPANet/utils/performance/efficiency_configuration.py`
> - VBF vs ggF analysis: `HH4b_SPANet/utils/performance/efficiency_configuration_vbf_ggf.py`

### ROC curve

To plot the ROC of a signal/background classifier you can use the following command. The configuration to decide what to plot is the same as for the efficiency scirpts.

```bash
# Activate the virtual environment
source spanet_env/bin/activate

cd HH4b_SPANet

python3 utils/roccurves/ROC_plots.py -pd <plot_dir> -conf  utils/roccurves/roc_configuration_vbfggf.py [--no-weights] [--region <region>]

# e.g. for VBF
python3 utils/roccurves/ROC_plots.py -pd <plot_dir> -conf  utils/roccurves/roc_configuration_vbfggf.py -r vbf_no_kin_cuts
```
