"""Submission of a SPANet training to HTCondor.

The module can be used from the command line (as before) or imported, e.g. by
the law tasks in ``law_tasks``, which need the cluster id of the submitted job
in order to follow it.
"""

import argparse
import configparser
import os

import htcondor

from omegaconf import OmegaConf

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

SINGULARITY_IMAGE = (
    "/cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmsml/cmsml:latest"
)


def law_config(basedir=None):
    """``law.cfg`` of the repository, or ``$LAW_CONFIG_FILE`` when it is set."""
    path = os.environ.get("LAW_CONFIG_FILE") or os.path.join(
        basedir or BASE_DIR, "law.cfg"
    )
    parser = configparser.ConfigParser(
        allow_no_value=True, strict=False, interpolation=None
    )
    try:
        parser.read(path)
    except configparser.Error:
        return configparser.ConfigParser()
    return parser


def config_bindings(basedir=None):
    """The ``extra_binds`` of law.cfg, as a list of paths.

    The shared EOS areas of the group are the same for everybody, so they are
    tracked in the configuration of the repository instead of being exported
    by each of us.
    """
    sources = [
        law_config(basedir).get("hh4b_spanet", "extra_binds", fallback=""),
        os.environ.get("SPANET_APPTAINER_EXTRA_BINDS", ""),
    ]
    return [
        bind.strip()
        for raw in sources
        for bind in raw.replace("\n", ",").split(",")
        if bind.strip()
    ]


def default_bindings(basedir=None):
    """Bind mounts of the job container.

    Generic by default (AFS, the EOS home of ``$USER`` and the credential
    directories), plus the ``extra_binds`` of law.cfg -- the EOS areas holding
    the shared samples.  ``SPANET_APPTAINER_BINDS`` adds more, as a comma
    separated list, without editing anything.
    """
    bindings = ["/afs"]

    user = os.environ.get("USER") or os.environ.get("LOGNAME")
    if user:
        bindings.append("/eos/user/{}/{}".format(user[0], user))

    for path in (os.environ.get("EOS_SPANET"), os.environ.get("SPANET_ENV_DIR")):
        if path:
            bindings.append(path)

    bindings += config_bindings(basedir)

    extra = os.environ.get("SPANET_APPTAINER_BINDS", "")
    bindings += [b.strip() for b in extra.split(",") if b.strip()]

    bindings += ["/etc/sysconfig/ngbauth-submit", "${XDG_RUNTIME_DIR}"]

    # keep the order, drop duplicates
    seen, result = set(), []
    for binding in bindings:
        binding = binding.rstrip("/")
        if binding and binding not in seen:
            seen.add(binding)
            result.append(binding)
    return result


def build_submission(
    cfg,
    options_file,
    log_dir,
    seed=None,
    checkpoint=None,
    ngpu=None,
    ncpu=None,
    good_gpus=False,
    extra_args="",
    output_dir=None,
    interactive=False,
    basedir=None,
):
    """Build the ``htcondor.Submit`` description of one training job."""
    basedir = basedir or BASE_DIR
    homedir = os.environ["HOME"]
    spanet_main_dir = os.environ.get("SPANET_MAIN_DIR", homedir)
    spanet_env_dir = os.environ.get("SPANET_ENV_DIR", homedir)

    cfg = OmegaConf.load(cfg) if isinstance(cfg, str) else cfg
    model = cfg["model"]
    if model not in ("training", "model_tune"):
        raise ValueError("Model {} not implemented".format(model))

    ngpu = cfg["ngpu"] if ngpu is None else ngpu
    ncpu = cfg["ncpu"] if ncpu is None else ncpu
    output_dir = output_dir or basedir

    sub = htcondor.Submit()
    if interactive:
        sub["InteractiveJob"] = True

    sub["Executable"] = "{}/jobs/{}.sh".format(basedir, model)
    sub["arguments"] = (
        "-o {}/{} -n {}/{} -s {} -g {} -m {} -e {} -H {} -- {}".format(
            basedir,
            options_file,
            output_dir,
            log_dir,
            seed,
            ngpu,
            spanet_main_dir,
            spanet_env_dir,
            homedir,
            extra_args,
        )
    )
    # next to the checkpoints and the tensorboard logs of the training, not in
    # the repository: that is where one looks when a job goes wrong
    sub["Output"] = "{}/{}/{}-$(ClusterId).$(ProcId).out".format(
        output_dir, log_dir, model
    )
    sub["Error"] = "{}/{}/{}-$(ClusterId).$(ProcId).err".format(
        output_dir, log_dir, model
    )
    sub["Log"] = "{}/{}/{}-$(ClusterId).log".format(output_dir, log_dir, model)
    sub["MY.SendCredential"] = True
    sub["MY.SingularityImage"] = '"{}"'.format(
        os.environ.get("SPANET_APPTAINER_IMAGE", SINGULARITY_IMAGE)
    )
    sub["+JobFlavour"] = '"{}"'.format(cfg["job_flavour"])
    sub["environment"] = (
        'SINGULARITY_BIND_EXPR="{}", KRB5CCNAME="FILE:${{XDG_RUNTIME_DIR}}/krb5cc"'.format(
            ", ".join(default_bindings(basedir))
        )
    )
    sub["MY.SingularityUseGPU"] = True

    if checkpoint:
        sub["arguments"] += " -cf {}".format(checkpoint)

    sub["request_cpus"] = str(ncpu)
    sub["request_gpus"] = str(ngpu)

    if good_gpus:
        sub["requirements"] = (
            'regexp("A100", TARGET.GPUs_DeviceName) || regexp("V100", TARGET.GPUs_DeviceName)'
        )

    return sub


def create_log_dirs(sub):
    for folder in ["Output", "Error", "Log"]:
        os.makedirs(os.path.dirname(sub[folder]), exist_ok=True)


def submit(sub, dry=False):
    """Submit ``sub`` and return the cluster id (``None`` for a dry run)."""
    create_log_dirs(sub)
    if dry:
        return None

    credd = htcondor.Credd()
    credd.add_user_cred(htcondor.CredTypes.Kerberos, None)

    print("Starting Condor scheduler...")
    schedd = htcondor.Schedd()
    result = schedd.submit(sub, count=1)

    cluster_id = result.cluster()
    print("Submitted {} job(s) to {}".format(result.num_procs(), cluster_id))
    return cluster_id


def submit_training(**kwargs):
    """Build and submit a training job, returning its cluster id."""
    dry = kwargs.pop("dry", False)
    sub = build_submission(**kwargs)
    print("Submission parameters:")
    print(sub, end="\n\n")
    return submit(sub, dry=dry)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cfg", type=str, required=True)
    parser.add_argument(
        "-of",
        "--options_file",
        type=str,
        default=None,
        help="JSON file with option overloads.",
        required=True,
    )
    parser.add_argument(
        "-l",
        "--log_dir",
        type=str,
        default=None,
        help="Output directory for the checkpoints and tensorboard logs. Default to current directory.",
        required=True,
    )
    parser.add_argument(
        "-cf",
        "--checkpoint",
        type=str,
        default=None,
        help="Optional checkpoint to load the training state from. "
        "Fully restores model weights and optimizer state.",
    )
    parser.add_argument("--dry", action="store_true")
    parser.add_argument("--interactive", action="store_true")
    parser.add_argument("--ngpu", type=int, default=None)
    parser.add_argument("--ncpu", type=int, default=None)
    parser.add_argument("--good-gpus", action="store_true")
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    parser.add_argument("--outputdir", type=str, default=None, help="Output directory")
    parser.add_argument("--args", default="", type=str, help="additional args")
    return parser.parse_args()


def main():
    args = parse_args()

    print("basedir {}".format(BASE_DIR))
    print("homedir: ", os.environ["HOME"])
    print("spanet_main_dir: ", os.environ.get("SPANET_MAIN_DIR", os.environ["HOME"]))
    print("spanet_env_dir: ", os.environ.get("SPANET_ENV_DIR", os.environ["HOME"]))
    print("\nargs:", args.args)
    if args.interactive:
        print("interactive mode")

    print("Initializing job submission script...", end="\n\n")
    submit_training(
        cfg=args.cfg,
        options_file=args.options_file,
        log_dir=args.log_dir,
        seed=args.seed,
        checkpoint=args.checkpoint,
        ngpu=args.ngpu,
        ncpu=args.ncpu,
        good_gpus=args.good_gpus,
        extra_args=args.args,
        output_dir=args.outputdir,
        interactive=args.interactive,
        dry=args.dry,
    )


if __name__ == "__main__":
    main()
