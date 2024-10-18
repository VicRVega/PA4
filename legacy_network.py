#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call
import subprocess

# Note: path may be different dependent on where the certificate_generation file is located.
subprocess.run(["sudo", "-E", "python3", "CST311/PA4/certificate_generation.py"])

def myNetwork():

    net = Mininet( topo=None,
                   build=False,
                   ipBase='10.0.0.0/24')

    info( '*** Adding controller\n' )
    c0=net.addController(name='c0',
                      controller=Controller,
                      protocol='tcp',
                      port=6633)

    info( '*** Add switches\n')
    #Add switches before routers
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch)

    info('*** Add routers\n')
    r3 = net.addHost('r3', cls=Node, ip='10.0.1.1/24')
    r3.cmd('sysctl -w net.ipv4.ip_forward=1')

    r4 = net.addHost('r4', cls=Node, ip='192.168.1.2/30')
    r4.cmd('sysctl -w net.ipv4.ip_forward=1')

    r5 = net.addHost('r5', cls=Node, ip='10.0.2.1/24')
    r5.cmd('sysctl -w net.ipv4.ip_forward=1')

    info( '*** Add hosts\n')
    h1 = net.addHost('h1', cls=Host, ip='10.0.1.2/24', defaultRoute='via 10.0.1.1')
    h2 = net.addHost('h2', cls=Host, ip='10.0.1.3/24', defaultRoute='via 10.0.1.1')
    h3 = net.addHost('h3', cls=Host, ip='10.0.2.2/24', defaultRoute='via 10.0.2.1')
    h4 = net.addHost('h4', cls=Host, ip='10.0.2.3/24', defaultRoute='via 10.0.2.1')

    info( '*** Add links\n')
    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(h3, s2)
    net.addLink(h4, s2)

    net.addLink(s2, r5)
    net.addLink(s1, r3)

    #add link parameters
    net.addLink(r3, r4, intfName1='r3-eth1', params1={'ip': '192.168.1.1/30'},
                intfName2='r4-eth0', params2={'ip': '192.168.1.2/30'})

    net.addLink(r4, r5, intfName1='r4-eth1', params1={'ip': '192.168.2.1/30'},
                intfName2='r5-eth1',params2={'ip': '192.168.2.2/30'})

    info( '*** Starting network\n')
    net.build()

    #Add static routes
    r3.cmd('ip route add 10.0.2.0/24 via 192.168.1.2 dev r3-eth1')
    r3.cmd('ip route add 192.168.2.0/30 via 192.168.1.2 dev r3-eth1')

    r4.cmd('ip route add 10.0.1.0/24 via 192.168.1.1 dev r4-eth0')
    r4.cmd('ip route add 10.0.2.0/24 via 192.168.2.2 dev r4-eth1')

    r5.cmd('ip route add 10.0.1.0/24 via 192.168.2.1 dev r5-eth1')
    r5.cmd('ip route add 192.168.1.0/30 via 192.168.2.1 dev r5-eth1')

    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches\n')
    net.get('s2').start([c0])
    net.get('s1').start([c0])

    info( '*** Post configure switches and hosts\n')

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()