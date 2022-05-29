from mininet.net import Containernet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel
import json


SINGLE_INSTANCE = "single_instance"
INSTANCES_KEY = "instances"
BENCHMARK_SCRIPT = "benchmark_script"


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


setLogLevel('info')

net = Containernet(controller=Controller)
info('Adding controller\n')
net.addController('c0')
info('Adding redis\n')

s1 = net.addSwitch('s1')

for idx, host in enumerate(redis_hosts):
    ip = host["host"]
    cpu = int(host["cpu"])
    redis_server = net.addDocker(f'redis{idx}', ip=ip, dimage='wrapped_redis:latest', ports=[6379], dcmd="redis-server", cpu_quota=cpu*1000)
    net.addLink(redis_server, s1)


client = net.addDocker('client', ip="10.0.0.20", dimage='app:latest')

net.addLink(s1, client)

net.start()

info(client.cmd("python3 /app.py"))


CLI(net)
net.stop()