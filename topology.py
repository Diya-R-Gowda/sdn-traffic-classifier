from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel

def create_topology():
    net = Mininet(controller=RemoteController, switch=OVSSwitch)

    print("[*] Adding controller...")
    c0 = net.addController('c0', controller=RemoteController,
                            ip='127.0.0.1', port=6633)

    print("[*] Adding switch...")
    s1 = net.addSwitch('s1')

    print("[*] Adding hosts...")
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.0.2/24')
    h3 = net.addHost('h3', ip='10.0.0.3/24')

    print("[*] Adding links...")
    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(h3, s1)

    net.start()
    print("[*] Network started. Type 'exit' to stop.\n")
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    create_topology()
