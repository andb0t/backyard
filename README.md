# Backyard


## Todo:
- Deploy on AWS or Heroku
- Migrate to Kubernetes


## Setup
Run the setup scripts:
```bash
./build_services.sh
./start_services.sh
```

### Storage
```bash
# Build image
docker build -t storage_image storage
# Create a container whose sole purpose is to persist data
docker create --name storage_container storage_image
```

Peek into the storage volume:
```bash
docker run -it --rm --volumes-from storage_container storage_image ls /data
```

Remove the container with
```bash
docker rm -v storage_container
```


### Tools
* set up spiderfoot container with
```bash
docker build -t spiderfoot_image tools/spiderfoot/download
docker run -d -it -p 5001:5001 --rm --name spiderfoot_server spiderfoot_image
# connect directly via http://localhost:5001/
```
then set up sidecar with
```bash
docker build -t spiderfoot_sidecar_image tools/spiderfoot
docker run -it --rm --link spiderfoot_server:spiderfoot --name spiderfoot_sidecar spiderfoot_sidecar_image
```
* theharvester
```bash
docker build -t theharvester_image tools/theharvester
docker run -d -it -p 5002:5002 --rm --volumes-from storage_container --name theharvester_container theharvester_image
```


### Analyses
```bash
docker build -t data_statistics_image analyses/data_statistics
docker run -d -it -p 5003:5003 --rm --volumes-from storage_container --name data_statistics_container data_statistics_image
```


### Backend
Build backend image:
```bash
docker build -t backend_image backend
docker run -d -it -p 5000:5000 --rm --volumes-from storage_container --link theharvester_container:theharvester --link data_statistics_container:data_statistics --name backend_container backend_image
```
Check it on http://localhost:5000/


### Frontend
Build frontend:
```bash
docker build -t webapp_image frontend
docker run -d -it -p 8080:8080 --rm --link backend_container:backend --name frontend_container webapp_image
```

Peek inside
```bash
docker run -it --rm --link backend_container:backend webapp_image --name frontend_container bash
env  # see available environmental variables, amongst others the backend info
ping backend  # ping [IP_ADDRESS]
curl --data "url=www.bash.com" 172.17.0.2:5000/request/ # test backend
```
Use it on http://localhost:8080/

Check networking on docker with `docker network inspect bridge`


### Clean up
Remove all containers and their associated volumes:
```bash
docker rm -v $(docker ps -qa)
```


## Execution


### Regular
Visit http://localhost:8080/ with your browser


### Call containers directly via scripts
```bash
python call_backend.py test_client www.hello.com
python call_tools.py test_client www.hello.com
```
