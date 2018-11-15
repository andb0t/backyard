#!/bin/bash

echo "Stopping all docker services ..."

docker stop \
scan_spiderfoot_server_container \
scan_spiderfoot_sidecar_container \
scan_theharvester_container \
scan_nmap_container \
scan_cve_container \
scan_wapiti_container \
analysis_data_statistics_container \
analysis_dummy_container \
analysis_counting_container \
analysis_spiderfoot_container \
master_container \
frontend_container \
nats_container

echo "Done!"
docker ps
