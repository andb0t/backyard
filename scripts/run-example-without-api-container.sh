#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

# run docker
docker run -d --name db --publish 27017:27017 mongo
docker run -d --name msg --publish 4222:4222 --publish 6222:6222 --publish 8222:8222 nats

#docker run -d --name api --network proto --publish 8080:8080 --env NATS='msg:4222' backyard/api
"$DIR"/start-api.sh
