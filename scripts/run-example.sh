#!/usr/bin/env bash

cd ..

# run docker
docker network create --driver bridge proto
docker run -d --name db --network proto --publish 27017:27017 mongo
docker run -d --name msg --network proto --publish 4222:4222 --publish 6222:6222 --publish 8222:8222 nats
sleep 5s
docker run -d --name api --network proto --publish 8080:8080 --env NATS='msg:4222' backyard/api