#!/bin/bash

PROD_DEP="requirements.txt"
DEV_DEP="requirements_dev.txt"

echo "Locking production dependencies as $PROD_DEP"

python -m piptools compile \
    -o $PROD_DEP \
    --no-header \
    pyproject.toml
    
if [[ $? != 0 ]]; then
    echo "Failed to lock production dependencies."
    return 1
fi

echo "Locking production dependencies as $DEV_DEP"

python -m piptools compile \
    -o $DEV_DEP \
    --no-header \
    --extra dev \
    --constraint $PROD_DEP \
    pyproject.toml
