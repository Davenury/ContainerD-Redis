from mininet.net import Containernet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel
setLogLevel('info')

net = Containernet(controller=Controller)
info('Adding controller\n')
net.addController('c0')
info('Adding redis\n')
redis = net.addDocker('redis', ip='10.0.0.251', dimage='redis', ports=[6379], port_bindings={6379:6379})
