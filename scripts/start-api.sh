#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

sleep 5s

curl localhost:4222

nohup pipenv run python "$DIR"/../src/backyard/api &
