#!/bin/bash

sudo apt-get install -y jq

sudo docker build -f server/Dockerfile -t node_app server/

sudo docker build -f Dockerfile.redis -t wrapped_redis .
sudo docker build -f Dockerfile.benchmark -t wrapped_benchmark .
sudo docker build -f Dockerfile.client -t wrapped_client .

sudo docker run --rm -d -p 8080:8080 node_app

for cpu in $(cat config.json | jq '.cpus' | jq '.[]' -c); do

    sudo docker run --name containernet -d --rm -it --privileged --pid='host' -v /var/run/docker.sock:/var/run/docker.sock containernet/containernet

    CONTAINERNET_CONTAINER_ID=`sudo docker ps | grep containernet | awk '{print $1}'`

    sudo docker cp containernet.py $CONTAINERNET_CONTAINER_ID:/containernet
    sudo docker cp config.json $CONTAINERNET_CONTAINER_ID:/containernet

    sudo docker exec -t $CONTAINERNET_CONTAINER_ID sudo python3 containernet.py $cpu

    sudo docker kill $CONTAINERNET_CONTAINER_ID

    sleep 2

done;

NODE_DOCKER_CONTAINER=`sudo docker ps | grep node_app | awk '{print $1}'`
REDIS_CONTAINER_ID=`sudo docker ps | grep redis-server | awk '{print $1}'`

sudo docker cp $NODE_DOCKER_CONTAINER:/app/result*.csv .

sudo docker kill `sudo docker ps -q`

sudo docker rm $REDIS_CONTAINER_ID