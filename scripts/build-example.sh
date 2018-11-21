#!/usr/bin/env bash

cd ..

# build containers
docker build -t backyard/scanner-example:latest templates/scanner/example
docker build -t backyard/analyzer-example:latest templates/analyzer/example
docker build -t backyard/api .