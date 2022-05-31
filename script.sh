#!/bin/bash

sudo docker run --name containernet -d --rm -it --privileged --pid='host' -v /var/run/docker.sock:/var/run/docker.sock containernet/containernet

sudo docker build -f server/Dockerfile -t node_app server/

sudo docker build -f Dockerfile.redis -t wrapped_redis .
sudo docker build -f Dockerfile.benchmark -t wrapped_benchmark .

DOCKER_CONTAINER_ID=`sudo docker ps | grep containernet | awk '{print $1}'`

sudo docker run -d -p 8080:8080 node_app

sudo docker cp containernet.py $DOCKER_CONTAINER_ID:/containernet
sudo docker cp config.json $DOCKER_CONTAINER_ID:/containernet

sudo docker exec -it $DOCKER_CONTAINER_ID sudo python3 containernet.py

#sudo docker cp node_app:/app/result.csv .