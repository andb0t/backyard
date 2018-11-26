# API example using proto files


## Local development setup

### Prerequisites

To run a local, non *kubernetes* development installation, you need these local accessible components:

 * [Docker](https://www.docker.com/get-started)
 * [NATS](https://github.com/nats-io/gnatsd/releases)
 * [MongoDB](https://www.mongodb.com/download-center/community)

Start *NATS* via `gnatsd`. Run *MongoDB* using `mkdir -p /tmp/db && mongodb --dbpath /tmp/db`.

### Initialize submodules
```
git submodule init --update
```

### Build components

Build main processes (API server and Supervisor):

```
pipenv install --skip-lock
pipenv shell
./setup.py develop
```

Build example scanner:

```
docker build -t backyard/scanner-example:latest templates/scanner/example
```

Build example analyzer:

```
docker build -t backyard/analyzer-example:latest templates/analyzer/example
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

## Exploring the API
Default credentials: admin/secret

### Swagger endpoint
URL: http://localhost:8080/v1/ui/

### UI endpoint
URL: http://localhost:8080/v1
