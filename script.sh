#!/bin/bash

sudo docker pull containernet/containernet

sudo docker build -f Dockerfile.redis -t wrapped_redis .
sudo docker build -f Dockerfile.app -t app .

DOCKER_CONTAINER_ID=`sudo docker ps | grep containernet | awk '{print $1}'`

sudo docker cp example.py $DOCKER_CONTAINER_ID:/containernet
sudo docker cp main.py $DOCKER_CONTAINER_ID:/containernet

sudo docker exec -it $DOCKER_CONTAINER_ID /bin/sh
