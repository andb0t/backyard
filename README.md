# Backyard


## Todo:
- Deploy on AWS or Heroku
- Migrate to Kubernetes


## Setup
Run the setup scripts, depending on your needs:
```bash
./build_services.sh
./start_services.sh
./stop_services.sh
```

## Execution

Visit http://localhost:8080/ with your browser


## Misc

### NATS

Visit http://localhost:8222/ to monitor the NATS server

### Storage
Peek into the storage volume:
```bash
docker run -it --rm --volumes-from storage_container storage_image ls /data
```

Remove the container with
```bash
docker rm -v storage_container
```


### Scanners
* set up spiderfoot container with
  ```bash
  docker build -t spiderfoot_image scans/spiderfoot/download
  docker run -d -it -p 5001:5001 --rm --name spiderfoot_server spiderfoot_image
  # connect directly via http://localhost:5001/
  ```
  then set up sidecar with
  ```bash
  docker build -t spiderfoot_sidecar_image scans/spiderfoot
  docker run -it --rm --link spiderfoot_server:spiderfoot --name spiderfoot_sidecar spiderfoot_sidecar_image
  ```
* theharvester: See setup scripts



### Frontend
Peek inside
```bash
docker run -it --rm --link master_container:master frontend_image --name frontend_container bash
env  # see available environmental variables, amongst others the master info
ping master  # ping [IP_ADDRESS]
curl --data "url=www.bash.com" 172.17.0.2:5000/request/ # test master
```
Use it on http://localhost:8080/

Check networking on docker with `docker network inspect bridge`


### Clean up
Remove all containers and their associated volumes:
```bash
docker rm -v $(docker ps -qa)
```
