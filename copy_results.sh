#!/bin/bash

DOCKER_CONTAINER_ID=`sudo docker ps | grep app: | awk '{print $1}'`

sudo docker cp $DOCKER_CONTAINER_ID:/result.csv .