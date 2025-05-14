#!/bin/bash

MODE=$1

if [[ "$MODE" != "init" && "$MODE" != "check" ]]; then
  echo "Usage : ./launch.sh [init|check]"
  exit 1
fi

source venv/bin/activate
python main.py "$MODE"
