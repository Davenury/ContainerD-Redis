#!/bin/bash
DOCKER_CONTAINER_ID=`sudo docker ps | grep containernet | awk '{print $1}'`

sudo docker cp example.py $DOCKER_CONTAINER_ID:/containernet
sudo docker cp ./ContainerD-Redis/main.py $DOCKER_CONTAINER_ID:/containernet
sudo docker cp containernet_script.sh $DOCKER_CONTAINER_ID:/containernet

sudo docker exec $DOCKER_CONTAINER_ID /bin/sh "chmod +x containernet_script.sh;"
sudo docker exec -it $DOCKER_CONTAINER_ID /bin/sh
