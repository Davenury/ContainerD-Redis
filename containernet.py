from mininet.net import Containernet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel
import json


setLogLevel('info')


SINGLE_INSTANCE = "single_instance"
INSTANCES_KEY = "instances"
BENCHMARK = "benchmark"
CLIENTS = "clients"
THREADS = "threads"
REQUESTS = "requests"
RATIO = "ratio"
CPUS = "cpus"

def get_benchmark_values(config):
    benchmark_values = config.get(BENCHMARK, None)
    if benchmark_values is None:
        return 5, 4, 10000, "1:10"
    
    clients = config.get(CLIENTS, 5)
    threads = config.get(THREADS, 4)
    requests = config.get(REQUESTS, 10000)
    ratio = config.get(RATIO, "1:10")
    return clients, threads, requests, ratio
    

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
    net = Containernet(controller=Controller)
    info('Adding controller\n')
    net.addController('c0')
    info('Adding redis\n')

    s1 = net.addSwitch('s1')

    for idx, host in enumerate(redis_hosts):
        redis_server = net.addDocker(f'redis{idx}', ip=host, dimage='wrapped_redis:latest', ports=[6379], dcmd="redis-server", cpu_quota=cpu*1000)
        net.addLink(redis_server, s1)


    client = net.addDocker('client', ip="10.0.0.50", dimage='wrapped_benchmark:latest', network_mode="host")

    clients, threads, requests, ratio = get_benchmark_values(config)

    net.addLink(s1, client)

    net.start()

    info(client.cmd(f"memtier_benchmark -s {redis_hosts[0]} -c {clients} -t {threads} -n {requests} --ratio {ratio} --hide-histogram --json-out-file=result{cpu}.json"))
    client.cmd(f'cat result{cpu}.json | curl -H "Content-Type: application/json" -X POST -d "$(</dev/stdin)" http://localhost:8080/{cpu}')

    net.stop()

cpus = config.get(CPUS, [10, 50, 100])

for cpu in cpus:
    info(f"Iterating for {cpu}% cpu")
    make_one_cpu(cpu, config)