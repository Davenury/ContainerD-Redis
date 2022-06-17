from mininet.net import Containernet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel
import json
import sys
import time


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

def make_one_cpu(cpu, config):

    info('Adding redis\n')

    s1 = net.addSwitch(f's1')

    for idx, host in enumerate(redis_hosts):
        redis_server = net.addDocker(f'redis{idx}', ip=host, dimage='wrapped_redis:latest', ports=[6379], dcmd="redis-server", cpu_quota=cpu*1000)
        net.addLink(redis_server, s1)


    info("Adding client\n")
    client = net.addDocker(f'client{cpu}', ip="10.0.0.50", dimage='wrapped_benchmark:latest', network_mode="host")

    threads, requests = get_benchmark_values(config)

    info("Adding link \n")
    net.addLink(s1, client)

    redis_client = net.addDocker(f'mark{cpu}', ip="10.0.0.60", dimage='wrapped_client:latest', network_mode="host")
    net.addLink(s1, redis_client)

    net.start()

    net.ping([redis_server, client])
    net.ping([redis_client, redis_server])

    info(client.cmd(f"memtier_benchmark -s {redis_hosts[0]} -c 1 -t {threads} -n {requests} --ratio=1:0 --key-pattern=S:S --hide-histogram --json-out-file=result{cpu}.json"))
    client.cmd(f'cat result{cpu}.json | curl -H "Content-Type: application/json" -X POST -d "$(</dev/stdin)" http://localhost:8080/{cpu}/Sets')

    info(client.cmd(f"memtier_benchmark -s {redis_hosts[0]} -c 1 -t {threads} -n {requests} --ratio=0:1 --key-pattern=S:S --hide-histogram --json-out-file=result{cpu}.json"))
    client.cmd(f'cat result{cpu}.json | curl -H "Content-Type: application/json" -X POST -d "$(</dev/stdin)" http://localhost:8080/{cpu}/Gets')

    info(redis_client.cmd(f"""echo "operation,ops" > my.csv && redis-benchmark -h {redis_hosts[0]} -q --csv >> my.csv && cat my.csv | python3 -c 'import csv, json, sys; print(json.dumps([dict(r) for r in csv.DictReader(sys.stdin)]))' > result{cpu}.json"""))
    redis_client.cmd(f'cat result{cpu}.json | curl -H "Content-Type: application/json" -X POST -d "$(</dev/stdin)" http://localhost:8080/redis-benchmark/{cpu}')

    net.stop()

cpus = config.get(CPUS, [10, 50, 100])


make_one_cpu(int(sys.argv[1]), config)