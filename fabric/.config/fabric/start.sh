#!/bin/bash

cd "$(dirname "$0")"

if [[ ! -d .venv ]]; then
    uv venv
    uv pip install -r requirements.txt
else
    echo "Virtual environment already exists"
fi

./.venv/bin/python ./main.py
