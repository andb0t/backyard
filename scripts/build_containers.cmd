@echo off

rem example containers
docker build -t backyard/scanner-example:latest templates/scanner/example
docker build -t backyard/analyzer-example:latest templates/analyzer/example

rem real containers
docker build -t backyard/analyzer-dummy:latest modules/analyzer/dummy
docker build -t backyard/scanner-theharvester:latest modules/scanner/theharvester
docker build -t backyard/analyzer-data_statistics:latest modules/analyzer/data_statistics
docker build -t backyard/analyzer-dummy:latest modules/analyzer/dummy
docker build -t backyard/scanner-arachni:latest modules/scanner/arachni
