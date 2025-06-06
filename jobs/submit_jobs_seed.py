import os
import subprocess
import argparse


script_dir = os.path.dirname(os.path.realpath(__file__))

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument(
    "-c", "--config", type=str, required=True, help="Path to the config file"
)
arg_parser.add_argument(
    "-o", "--option", type=str, required=True, help="Path to the option file"
)
arg_parser.add_argument(
    "-s", "--seeds", type=str, required=False, default=None, help="start_seed:end_seed, if None use random seed"
)
arg_parser.add_argument(
    "-n", "--num", type=int, required=False, default=0, help="number of trainings with random seeds"
)
arg_parser.add_argument(
    "-a",
    "--add_args",
    type=str,
    required=False,
    default=None,
    help="additional arguments",
)
arg_parser.add_argument(
    "--suffix",
    type=str,
    required=False,
    default="",
    help="directory name",
)
arg_parser.add_argument(
    "-out", "--output_folder", type=str, required=False, default="$EOS_SPANET", help="directory in which out_spanet_outputs is saved"
)
args = arg_parser.parse_args()

if args.seeds:
    seed_start = int(args.seeds.split(":")[0])
    seed_end = int(args.seeds.split(":")[1])

# get the file name without extension and use it as the directory name
dir_name = os.path.splitext(os.path.basename(args.option))[0] + args.suffix
add_args = f'--args "{args.add_args}"' if args.add_args else ""

print(add_args)

if args.seeds:
    for seed in range(seed_start, seed_end + 1):
        cmd = "python3 {}/submit_to_condor.py --cfg {} -of {} -l out_spanet_outputs/out_{}/out_seed_trainings_{} --seed {} --outputdir {} {}".format(
            script_dir, args.config, args.option, dir_name, seed, seed, args.output_folder, add_args
        )
        subprocess.run(cmd, shell=True)
else:
    for i in range(args.num):
        cmd = "python3 {}/submit_to_condor.py --cfg {} -of {} -l out_spanet_outputs/out_{}/out_no_seed_trainings_{} --outputdir {} {}".format(
            script_dir, args.config, args.option, dir_name, i, args.output_folder, add_args
        )
        subprocess.run(cmd, shell=True)
