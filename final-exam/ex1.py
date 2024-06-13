#!/usr/bin/python

"""
This script creates the network environment for Lab5:
- Starts all routers, switches and hosts
- You need to choose either Topo1 or Topo2
- XTerm window launched for all devices.
"""
# Needed to check for display status 
import inspect
import os

# Needed to patch Mininet's isShellBuiltin module
import sys

# Run commands when you exit the python script
import atexit

# patch isShellBuiltin (suggested by MiniNExT's authors)
import mininet.util

sys.modules['mininet.util'] = mininet.util

# Loads the default controller for the switches

from mininet.node import Controller

# Needed to set logging level and show useful information during script execution.
from mininet.log import setLogLevel, info

# To launch xterm for each node
from mininet.term import cleanUpScreens, makeTerms # for supporting copy/paste

# Provides the mininet> prompt
from mininet.cli import CLI

# Primary constructor for the virtual environment.
from mininet.net import Mininet

# We import the TC-enabled link
from mininet.link import Intf, TCIntf, TCLink


# Variable initialization
net = None
hosts = None


def run():
    " Creates the virtual environment, by starting the network and configuring debug information "
    info('** Creating an instance of the network topology\n')
    global net
    global hosts
   
    net = Mininet(intf=TCIntf)
    
    info('\n** Adding Controller\n')
    net.addController( 'c0' )
    
    info('\n** Adding Hosts\n')
    r1 = net.addHost('r1', ip='24.30.65.5/24', hostname='r1',  privateLogDir=True, privateRunDir=True, inMountNamespace=True, inPIDNamespace=True, inUTSNamespace=True)
    h1 = net.addHost('h1', ip='24.30.65.1/24', hostname='h1',  privateLogDir=True, privateRunDir=True, inMountNamespace=True, inPIDNamespace=True, inUTSNamespace=True)
    h2 = net.addHost('h2', ip='24.30.65.2/24', hostname='h2',  privateLogDir=True, privateRunDir=True, inMountNamespace=True, inPIDNamespace=True, inUTSNamespace=True)
    h3 = net.addHost('h3', ip='24.30.90.3/24', hostname='h3',  privateLogDir=True, privateRunDir=True, inMountNamespace=True, inPIDNamespace=True, inUTSNamespace=True)
    h4 = net.addHost('h4', ip='24.30.90.4/24', hostname='h4',  privateLogDir=True, privateRunDir=True, inMountNamespace=True, inPIDNamespace=True, inUTSNamespace=True)

 
    info('\n** Adding Switches\n')
    # Adding switches to the network
    sw1 = net.addSwitch('sw1')
    sw2 = net.addSwitch('sw2')
    
    info('\n** Creating Links \n')
    link_h1sw1 = net.addLink( h1, sw1)
    link_h2sw1 = net.addLink( h2, sw1)
    link_h3sw2 = net.addLink( h3, sw2)
    link_h4sw2 = net.addLink( h4, sw2)
    link_r1sw1 = net.addLink( r1, sw1, intfName1='r1-eth0')
    link_r1sw2 = net.addLink( r1, sw2, intfName1='r1-eth1')

    
    info('\n** Modifying Link Parameters \n')
    """
        Default parameters for links:
        bw = None,
 		delay = None,
 		jitter = None,
 		loss = None,
 		disable_gro = True,
 		speedup = 0,
 		use_hfsc = False,
 		use_tbf = False,
 		latency_ms = None,
 		enable_ecn = False,
 		enable_red = False,
 		max_queue_size = None 
    """
    
    net.start()

    info( '*** Configuring hosts\n' )
    info('** Executing custom commands\n')
    output = net.nameToNode.keys
    r1.cmd('ifconfig r1-eth1 24.30.90.5 netmask 255.255.255.0')
    r1.cmd('echo 1 > /proc/sys/net/ipv4/ip_forward')

    h1.cmd('ip route add default via 24.30.65.5')
    h2.cmd('ip route add default via 24.30.65.5')
    h3.cmd('ip route add default via 24.30.90.5')
    h4.cmd('ip route add default via 24.30.90.5')

    r1.cmd('iptables -t nat -A PREROUTING -p ICMP -s 24.30.65.1 -d 24.30.90.3 -j DNAT --to 24.30.65.5')
    r1.cmd('iptables -t nat -A POSTROUTING -p ICMP -s 24.30.90.3 -d 24.30.65.1 -j SNAT --to 24.30.90.5')
 
     
    
	#Enable Xterm window for every host
    info('** Enabling xterm for hosts only\n')
    # We check if the display is available
    hosts = [ r1, h1, h2, h3, h4 ]
    if 'DISPLAY' not in os.environ:
        error( "Error starting terms: Cannot connect to display\n" )
        return
    # Remove previous (and possible non-used) socat X11 tunnels
    cleanUpScreens()
    # Mininet's function to create Xterms in hosts
    makeTerms( hosts, 'host' )

	# Enable the mininet> prompt 
    info('** Running CLI\n')
    CLI(net)

    info( '*** Closing the terminals on the hosts\n' )
    r1.cmd("killall xterm")
    h1.cmd("killall xterm")
    h2.cmd("killall xterm")
    h3.cmd("killall xterm")
    h4.cmd("killall xterm")
    

    # This command stops the simulation
    net.stop()
    cleanUpScreens()

if __name__ == '__main__':
    # Set the log level on terminal
    setLogLevel('info')
    
    # Execute the script
    run()