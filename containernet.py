from mininet.net import Containernet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel
import json
import sys
import time
import os


setLogLevel('info')

SINGLE_INSTANCE = "single_instance"
INSTANCES_KEY = "instances"
BENCHMARK = "benchmark"
THREADS = "threads"
REQUESTS = "requests"
RATIO = "ratio"
CPUS = "cpus"
KEY_PATTERN="key-pattern"

net = Containernet(controller=Controller)
info('Adding controller\n')
net.addController(f'c0')

def get_benchmark_values(config):
    benchmark_values = config.get(BENCHMARK, None)
    if benchmark_values is None:
        return 4, 10000
    
    threads = benchmark_values.get(THREADS, 4)
    requests = benchmark_values.get(REQUESTS, 10000)
    return threads, requests
    

def read_config():
    with open("config.json", "r") as f:
        return json.load(f)


def get_redis_hosts(config):
    redis_hosts = config.get(INSTANCES_KEY, None)
    if redis_hosts is None or len(redis_hosts) == 0:
        raise ValueError('You didn\'t provide instance array in config or instance array length is 0.')
    
    return redis_hosts

config = read_config()
redis_hosts = get_redis_hosts(config)


def prepare_cluster():
    for idx, host in enumerate(redis_hosts):
        os.makedirs(str(7000+idx), mode=0o755, exist_ok=True)

        with open('redis.conf', "w+") as f:
            f.write(f"port {7000+idx} cluster-enabled yes cluster-config-file nodes.conf cluster-node-timeout 5000 append-only yes bind {host}")


def make_one_cpu(cpu, mode, config):
    client, redis_client, redis_server = None, None, None

    info('Adding redis\n')

    s1 = net.addSwitch(f's1')

    if config.get["type"] == "single_instance":
        redis_server = net.addDocker(f'redis', ip=redis_hosts[0], dimage='wrapped_redis:latest', ports=[6379], dcmd="redis-server", cpu_quota=cpu*1000)
        net.addLink(redis_server, s1)
    elif config.get["type"] == "cluster":
        prepare_cluster()
        for idx, host in enumerate(redis_hosts):
            redis_server = net.addDocker(f'redis{idx}', ip=host, dimage='wrapped_redis:latest', ports=[7000+idx], dcmd="redis-server /usr/local/etc/redis/redis.conf", volumes=[f"{os.getcwd()}/{7000+idx}/redis.conf:/usr/local/etc/redis/redis.conf"], cpu_quota=cpu*1000, network_mode="host")
            net.addLink(redis_server, s1)


    if mode == 1:
        info("Adding client\n")
        client = net.addDocker(f'client{cpu}', ip="10.0.0.50", dimage='wrapped_benchmark:latest', network_mode="host")

        info("Adding link \n")
        net.addLink(s1, client)

    threads, requests = get_benchmark_values(config)


    if mode == 2:
        redis_client = net.addDocker(f'mark{cpu}', ip="10.0.0.60", dimage='wrapped_client:latest', network_mode="host")
        net.addLink(s1, redis_client)

    net.start()

    if config.get["type"] == "cluster":
        cluster_string = ""
        for idx, host in enumerate(redis_hosts):
            cluster_string += f"{host}:{7000+idx} "
        redis_server.cmd(f"redis-cli --cluster create {cluster_string} --cluster-replicas 1")

    if mode == 1:
        info(client.cmd(f"memtier_benchmark -s {redis_hosts[0]} -c 1 -t {threads} -n {requests} --ratio=1:0 --key-pattern=S:S --hide-histogram --json-out-file=result{cpu}.json"))
        client.cmd(f'cat result{cpu}.json | curl -H "Content-Type: application/json" -X POST -d "$(</dev/stdin)" http://localhost:8080/{cpu}/Sets')

        info(client.cmd(f"memtier_benchmark -s {redis_hosts[0]} -c 1 -t {threads} -n {requests} --ratio=0:1 --key-pattern=S:S --hide-histogram --json-out-file=result{cpu}.json"))
        client.cmd(f'cat result{cpu}.json | curl -H "Content-Type: application/json" -X POST -d "$(</dev/stdin)" http://localhost:8080/{cpu}/Gets')

    if mode == 2:
        info(redis_client.cmd(f"""echo "operation,ops" > my.csv && redis-benchmark -h {redis_hosts[0]} -q --csv >> my.csv && cat my.csv | python3 -c 'import csv, json, sys; print(json.dumps([dict(r) for r in csv.DictReader(sys.stdin)]))' > result{cpu}.json"""))
        redis_client.cmd(f'cat result{cpu}.json | curl -H "Content-Type: application/json" -X POST -d "$(</dev/stdin)" http://localhost:8080/redis-benchmark/{cpu}')

    net.stop()

cpus = config.get(CPUS, [10, 50, 100])


make_one_cpu(int(sys.argv[1]), int(sys.argv[2]), config)