#!/usr/bin/env bash

set -xue

autoflake --check .
black --check --diff .
isort --check-only .