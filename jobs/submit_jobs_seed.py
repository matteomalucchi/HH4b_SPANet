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
    "-s",
    "--seeds",
    type=str,
    required=False,
    default=None,
    help="start_seed:end_seed, if None use random seed",
)
arg_parser.add_argument(
    "-n",
    "--num",
    type=int,
    required=False,
    default=0,
    help="number of trainings with random seeds",
)
arg_parser.add_argument(
    "-cf",
    "--checkpoint",
    type=str,
    default=None,
    help="Optional checkpoint to load the training state from. "
    "Fully restores model weights and optimizer state.",
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
    "-out",
    "--output_folder",
    type=str,
    required=False,
    default="$SPANET_OUT_DIR",
    help="directory in which out_spanet_outputs is saved",
)
arg_parser.add_argument("--interactive", action="store_true")
args = arg_parser.parse_args()

if args.seeds:
    seed_start = int(args.seeds.split(":")[0])
    seed_end = int(args.seeds.split(":")[1])

# get the file name without extension and use it as the directory name
dir_name = os.path.splitext(os.path.basename(args.option))[0] + args.suffix
add_args = f'--args "{args.add_args}"' if args.add_args else ""
interactive_str = "--interactive" if args.interactive else ""
checkpoint_str = f"--checkpoint {args.checkpoint}" if args.checkpoint else ""

print(add_args)

if args.seeds:
    for seed in range(seed_start, seed_end + 1):
        cmd = "python3 {}/submit_to_condor.py --cfg {} -of {} -l out_spanet_outputs/out_{}/out_seed_trainings_{} --seed {} {} --outputdir {} {} {}".format(
            script_dir,
            args.config,
            args.option,
            dir_name,
            seed,
            seed,
            checkpoint_str,
            args.output_folder,
            interactive_str,
            add_args,
        )
        print(cmd)
        subprocess.run(cmd, shell=True)
else:
    for i in range(args.num):
        cmd = "python3 {}/submit_to_condor.py --cfg {} -of {} -l out_spanet_outputs/out_{}/out_no_seed_trainings_{} {} --outputdir {} {} {}".format(
            script_dir,
            args.config,
            args.option,
            dir_name,
            i,
            checkpoint_str,
            args.output_folder,
            interactive_str,
            add_args,
        )
        print(cmd)
        subprocess.run(cmd, shell=True)
