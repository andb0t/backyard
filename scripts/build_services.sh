#!/bin/bash


echo "Building all docker services ..."

echo "Build the storage ..."
docker build -t storage_image storage
docker create --name storage_container storage_image

echo "Build the scans ..."
docker build -t scan_spiderfoot_server_image scans/spiderfoot/download
docker build -t scan_spiderfoot_sidecar_image scans/spiderfoot
docker build -t scan_theharvester_image scans/theharvester
docker build -t scan_nmap_image scans/nmap
docker build -t scan_cve_image scans/cve
docker build -t scan_wapiti_image scans/wapiti

echo "Build the analyses ..."
docker build -t analysis_data_statistics_image analyses/data_statistics
docker build -t analysis_dummy_image analyses/dummy
docker build -t analysis_counting_image analyses/counting

echo "Build the master ..."
docker build -t master_image master

echo "Build the frontend ..."
docker build -t frontend_image frontend
