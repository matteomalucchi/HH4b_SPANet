import subprocess
import argparse
import os


parser = argparse.ArgumentParser(
    description="Convert awkward ntuples in coffea files to h5 files."
)
parser.add_argument("-i", "--input", type=str, required=True, help="Input coffea file")
parser.add_argument("-o", "--output", type=str, default="", help="Output directory")
parser.add_argument(
    "-c",
    "--cat",
    type=str,
    default="inclusive",
    help="Event category",
)
parser.add_argument(
    "-f",
    "--frac-train",
    type=float,
    default=0.8,
    help="Fraction of events to use for training",
)
parser.add_argument(
    "--sample",
    type=str,
    default="GluGlutoHHto4B",
    nargs="+",
    help="Sample name",
)
parser.add_argument(
    "-s",
    "--no-shuffle",
    action="store_true",
    default=False,
    help="Do not shuffle the dataset"
)
parser.add_argument(
    "-r",
    "--random_pt",
    action="store_true",
    default=False,
    help="Applying a random weight to pT to reduce mass dependence",
)
parser.add_argument(
    "-p2h",
    "--only-parquet-to-h5",
    action="store_true",
    default=False,
    help="Only run parquet to h5 (used, when parquet files are already available).",
)
args = parser.parse_args()

if args.random_pt:
    random_pt_parameter = "-r"
else:
    random_pt_parameter = ""


out_dir = args.output if args.output else os.path.dirname(args.input)

script_dir = os.path.dirname(os.path.realpath(__file__))

coffea_to_parquet = f"python3 {script_dir}/coffea_to_parquet.py -i {args.input} -o {os.path.dirname(args.input)} -c {args.cat}"
#subprocess.run(coffea_to_parquet, shell=True)

parquet_to_h5 = f"python3 {script_dir}/parquet_to_h5.py -i {os.path.dirname(args.input)}/*.parquet -o {out_dir} -f {args.frac_train} {'--no-shuffle' if args.no_shuffle else ''}"
#subprocess.run(parquet_to_h5, shell=True)

print(coffea_to_parquet)
print(parquet_to_h5)
if not args.only_parquet_to_h5:
    total_command=f"{coffea_to_parquet} && echo 'First part done' && {parquet_to_h5}"
else:
    total_command=f"{parquet_to_h5}"
#total_command=f"{coffea_to_parquet}"
subprocess.run(total_command, shell=True)
