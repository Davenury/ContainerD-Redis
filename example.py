from mininet.net import Containernet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel
import redis

setLogLevel('info')

net = Containernet(controller=Controller)
info('Adding controller\n')
net.addController('c0')
info('Adding redis\n')

redis_server = net.addDocker('redis', ip="10.0.0.10", dimage='wrapped_redis:latest', ports=[6379], dcmd="redis-server")
client = net.addDocker('client', ip="10.0.0.20", dimage='app:latest')

s1 = net.addSwitch('s1')

net.addLink(redis_server, s1)
net.addLink(s1, client)

net.start()

net.ping([redis_server, client])
print("here")

info(client.cmd("ls /"))
info(client.cmd("python3 /app.py"))


CLI(net)
net.stop()