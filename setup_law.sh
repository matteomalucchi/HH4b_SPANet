#!/usr/bin/env bash
# Environment for the law pipeline of this repository.
#
#   source setup_law.sh
#
# It activates the SPANet virtual environment (if not active yet), points law
# at law.cfg, makes the law_tasks package importable and builds the task index.
# All paths are derived from $USER / the location of this file, so the script
# works for every user; export SPANET_ENV_DIR (and optionally SPANET_MAIN_DIR,
# EOS_SPANET) in your .bashrc to pin your own setup.
#
# On the machine that only converts the coffea files, SPANET_ENV_DIR does not
# have to be set: the current environment is kept, and the dataset tasks
# (hh4b.Dataset) run in it.

_law_setup() {
    local this_file="${BASH_SOURCE[0]:-${(%):-%x}}"
    local repo_dir
    repo_dir="$( cd "$( dirname "${this_file}" )" && pwd )"

    # the directory holding the SPANet and HH4b_SPANet checkouts
    export SPANET_MAIN_DIR="${SPANET_MAIN_DIR:-$( dirname "${repo_dir}" )}"

    # the virtual environment holding spanet, law and the plotting packages
    if [ -z "${SPANET_ENV_DIR}" ] && [ -n "${VIRTUAL_ENV}" ]; then
        export SPANET_ENV_DIR="${VIRTUAL_ENV}"
    fi
    if [ -z "${SPANET_ENV_DIR}" ]; then
        echo "setup_law.sh: SPANET_ENV_DIR is not set, keeping the current environment."
        echo "  Only the dataset tasks work without it; for the training set e.g."
        echo "  export SPANET_ENV_DIR=/eos/user/\${USER:0:1}/\${USER}/spanet_infos/spanet_env_test_eos"
    elif [ "${VIRTUAL_ENV}" != "${SPANET_ENV_DIR}" ]; then
        # shellcheck disable=SC1091
        source "${SPANET_ENV_DIR}/bin/activate" || return 1
    fi

    export LAW_HOME="${LAW_HOME:-${repo_dir}/.law}"
    export LAW_CONFIG_FILE="${LAW_CONFIG_FILE:-${repo_dir}/law.cfg}"
    export PYTHONPATH="${repo_dir}:${PYTHONPATH}"

    if ! command -v law >/dev/null 2>&1; then
        echo "setup_law.sh: law is not installed in ${SPANET_ENV_DIR:-${VIRTUAL_ENV:-the current environment}}" >&2
        echo "  pip install law" >&2
        return 1
    fi

    source "$( law completion )" "" 2>/dev/null

    law index --quiet || return 1

    echo "law is set up:"
    echo "  repository:  ${repo_dir}"
    echo "  environment: ${SPANET_ENV_DIR:-${VIRTUAL_ENV:-system python}}"
    echo "  config:      ${LAW_CONFIG_FILE}"
    echo "  law home:    ${LAW_HOME}"
}

_law_setup "$@"
