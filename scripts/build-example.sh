#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

cd "$DIR" || exit

# build containers
docker build -t backyard/scanner-example:latest templates/scanner/example
docker build -t backyard/analyzer-example:latest templates/analyzer/example
docker build -t backyard/api .
