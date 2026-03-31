#!/bin/bash

# Run bot in LIVE mode
source venv/bin/activate

export DRY_RUN=false
export VERBOSE=true

python -m src.bot