#!/usr/bin/env bash

set -xue

autoflake --check --recursive --exclude venv,migrations --quiet .
black --check --diff .
isort --check-only .