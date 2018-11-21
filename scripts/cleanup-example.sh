#!/usr/bin/env bash

docker kill api msg db
docker rm api msg db
docker network rm proto