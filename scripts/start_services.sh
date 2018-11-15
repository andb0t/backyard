#!/bin/bash

echo "Starting all docker services ..."

echo "Start NATS ..."
docker run -d --rm -p 8222:8222 -p 6222:6222 -p 4222:4222 --name nats_container nats

echo "Start the scans ..."
docker run -d -it -p 5001:5001 --rm --name scan_spiderfoot_server_container scan_spiderfoot_server_image
docker run -d -it -p 5005:5005 --rm --volumes-from storage_container --link scan_spiderfoot_server_container:scan_spiderfoot_server --name scan_spiderfoot_sidecar_container scan_spiderfoot_sidecar_image
docker run -d -it -p 5002:5002 --rm --volumes-from storage_container --name scan_theharvester_container scan_theharvester_image
docker run -d -it -p 5006:5006 --rm --volumes-from storage_container --name scan_nmap_container scan_nmap_image
docker run -d -it -p 5007:5007 --rm --volumes-from storage_container --name scan_cve_container scan_cve_image
docker run -d -it -p 5008:5008 --rm --volumes-from storage_container --name scan_wapiti_container scan_wapiti_image

echo "Start the analyses ..."
docker run -d -it -p 5003:5003 --rm --volumes-from storage_container --name analysis_data_statistics_container analysis_data_statistics_image
docker run -d -it -p 5004:5004 --rm --volumes-from storage_container --name analysis_dummy_container analysis_dummy_image
docker run -d -it -p 5009:5009 --rm --volumes-from storage_container --name analysis_counting_container analysis_counting_image
docker run -d -it -p 5010:5010 --rm --volumes-from storage_container --name analysis_spiderfoot_container analysis_spiderfoot_image

echo "Start the master ..."
docker run -d -it -p 5000:5000 --rm --volumes-from storage_container  --link scan_spiderfoot_sidecar_container:scan_spiderfoot  --link scan_wapiti_container:scan_wapiti  --link scan_cve_container:scan_cve  --link scan_nmap_container:scan_nmap  --link scan_theharvester_container:scan_theharvester   --link analysis_spiderfoot_container:analysis_spiderfoot  --link analysis_data_statistics_container:analysis_data_statistics  --link analysis_counting_container:analysis_counting  --link analysis_dummy_container:analysis_dummy --name master_container master_image

echo "Start the frontend ..."
docker run -d -it -p 8080:8080 --rm --link master_container:master --name frontend_container frontend_image

echo "Done!"
docker ps
