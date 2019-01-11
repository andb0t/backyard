# API example using proto files


## Local development setup

### Prerequisites

This does not run on windows shells, yet!

To run a local, non *kubernetes* development installation, you need these local accessible components:

 * [Docker](https://www.docker.com/get-started)
 * [NATS](https://github.com/nats-io/gnatsd/releases)
 * [MongoDB](https://www.mongodb.com/download-center/community)

Start *NATS* via `gnatsd`. Run *MongoDB* using `mkdir -p /tmp/db && mongodb --dbpath /tmp/db`.

or via Docker:
`docker run -d --name db --publish 27017:27017 mongo`
and
`docker run -d --name msg --publish 4222:4222 --publish 6222:6222 --publish 8222:8222 nats`

### Initialize submodules
```
git submodule update --init
```

### Build components

Build main processes (API server and Supervisor):

```
pipenv install --skip-lock
pipenv shell
./setup.py develop
```

Build scanners and analyzers with:

```
./scripts/build_containers.sh
```

### Running the service

The *supervisor* contains logic to start scanners and analyzers and sits right on top of
*NATS* to serve the requests. Start it using:

```
backyard-supervisor
```

The *api* server exposes the swagger defined API to an unencrypted local HTTP service. Make
sure that this is i.e. proxied by an SSL enabled *nginx* instance if made public.

```
backyard-api
```

You can now start the `EXAMPLE` analysis using the API (i.e. via the swagger interface).


## Adding scanners
```
./scripts/create_new_module.sh [analyzer, scanner] YOUR_MODULE_NAME
```

## Exploring the API
Default credentials: admin/secret

### Swagger endpoint
URL: http://localhost:8080/v1/ui/

### UI endpoint
URL: http://localhost:8080/v1
