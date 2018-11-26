# API example using proto files

## Local development setup

### Prerequisites

To run a local, non _kubernetes_ development installation, you need these local accessible components:

- [Docker](https://www.docker.com/get-started)
- [NATS](https://github.com/nats-io/gnatsd/releases)
- [MongoDB](https://www.mongodb.com/download-center/community)

Start _NATS_ via `gnatsd`. Run _MongoDB_ using `mkdir -p /tmp/db && mongodb --dbpath /tmp/db`.

Via Docker:
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
pipenv run python setup.py develop
```

Build example scanner in `templates/scanner/example`:

```
docker build -t backyard/scanner-example:latest .
```

Build example analyzer in `templates/analyzer/example`:

```
docker build -t backyard/analyzer-example:latest .
```

### Running the service

The _supervisor_ contains logic to start scanners and analyzers and sits right on top of
_NATS_ to serve the requests. Start it using:

```
pipenv run backyard-supervisor
```

The _api_ server exposes the swagger defined API to an unencrypted local HTTP service. Make
sure that this is i.e. proxied by an SSL enabled _nginx_ instance if made public.

```
pipenv run backyard-api
```

You can now start the `EXAMPLE` analysis using the API (i.e. via the swagger interface).

## Exploring the API

Default credentials: admin/secret

### Swagger endpoint

URL: http://localhost:8080/v1/ui/

### UI endpoint

URL: http://localhost:8080/v1
