#!/usr/bin/env bash

set -xue

autoflake .
isort .
black .
