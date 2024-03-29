#!/bin/bash

PROJECT="slack-status-cli"

python -m pip install --upgrade setuptools
python -m pip install pip~=23.0 pip-tools~=7.3 --no-cache

if [ ! -d "./$PROJECT.venv" ]; then
    python -m venv ./$PROJECT.venv
fi

source ./$PROJECT.venv/bin/activate

pip-sync ./requirements.txt ./requirements_dev.txt
