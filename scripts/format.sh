#!/usr/bin/env bash

set -xue

isort .
autoflake --recursive --remove-all-unused-imports --remove-unused-variables --in-place --exclude venv,migrations .
black .
