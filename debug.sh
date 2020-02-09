#!/bin/bash

export LC_ALL=en_US.utf-8
export LANG=en_US.utf-8
.venv/bin/uvicorn api:app --port $1 --reload
