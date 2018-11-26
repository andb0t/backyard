#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

cd "$DIR" || exit

git submodule update --init

pipenv install --skip-lock
