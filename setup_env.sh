#!/bin/bash
# This script sets up the PYTHONPATH to include the project's 'py' directory.
#
# USAGE:
# From your project's root directory, run the following command:
# source setup_env.sh

echo "Setting up PYTHONPATH for the project..."

# Get the absolute path of the directory where this script is located.
# This makes the script runnable from any location.
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Construct the full path to the 'py' directory.
PY_MODULE_PATH="${SCRIPT_DIR}/py"

# Prepend the module path to PYTHONPATH to ensure it's checked first.
# This also handles the case where PYTHONPATH is not yet set and avoids duplicates.
if [[ -z "$PYTHONPATH" ]]; then
  export PYTHONPATH="${PY_MODULE_PATH}"
elif [[ ":$PYTHONPATH:" != *":${PY_MODULE_PATH}:"* ]]; then
  export PYTHONPATH="${PY_MODULE_PATH}:${PYTHONPATH}"
fi

echo "PYTHONPATH has been updated for this terminal session."
echo "Current PYTHONPATH: ${PYTHONPATH}"