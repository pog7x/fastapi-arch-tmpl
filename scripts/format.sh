#!/usr/bin/env bash

set -xue

autoflake --recursive --remove-all-unused-imports --remove-unused-variables --in-place --exclude venv,migrations .
isort .
black .
