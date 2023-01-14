#!/usr/bin/env bash

set -xue

COMPOSE_FILE="docker-compose.test.yml"
CMD="docker-compose -f ${COMPOSE_FILE}"

function docker_compose_down() {
    if [[ $? -ne 0 ]]; then
      ${CMD} logs --tail="all" app
    fi
    ${CMD} down --remove-orphans
    ${CMD} rm -f
}

docker_compose_down

function clear_pytest() {
    ${CMD} exec -T app rm -rf .pytest_cache/
    ${CMD} exec -T app find . -type d -name "pycache" -exec rm -rf {} +
}

trap docker_compose_down EXIT

${CMD} up -d --build

clear_pytest

${CMD} exec -T app pytest -vvs && clear_pytest
