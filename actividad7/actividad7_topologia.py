from mininet.cli import CLI
from mininet.log import info, setLogLevel
from mininet.net import Mininet
from mininet.node import OVSSwitch

# Puerto de acceso (access) -> VLAN de cada host. El enlace entre switches
# (s1-eth3 <-> s2-eth3) no se toca: queda como puerto "trunk", que en Open
# vSwitch es el comportamiento por defecto de un puerto sin "tag" (deja
# pasar tramas etiquetadas de cualquier VLAN).
ACCESS_VLAN = {
    's1-eth1': 10,  # h1
    's1-eth2': 20,  # h2
    's2-eth1': 10,  # h3
    's2-eth2': 20,  # h4
}


def build_network():
    net = Mininet(controller=None, autoSetMacs=True, listenPort=6656)

    info('*** Agregando hosts\n')
    # Los 4 hosts quedan en la MISMA subred a proposito: si dos hosts no se
    # pueden pingear, tiene que ser porque la VLAN los separa a nivel de
    # trama, no porque falte una ruta IP (eso seria otro motivo de fallo y
    # no demostraria nada de capa 2).
    h1 = net.addHost('h1', ip='10.0.0.1/24')  # VLAN 10
    h2 = net.addHost('h2', ip='10.0.0.2/24')  # VLAN 20
    h3 = net.addHost('h3', ip='10.0.0.3/24')  # VLAN 10
    h4 = net.addHost('h4', ip='10.0.0.4/24')  # VLAN 20

    info('*** Agregando switches\n')
    s1 = net.addSwitch('s1', cls=OVSSwitch, failMode='standalone')
    s2 = net.addSwitch('s2', cls=OVSSwitch, failMode='standalone')

    info('*** Creando enlaces\n')
    net.addLink(h1, s1)  # s1-eth1
    net.addLink(h2, s1)  # s1-eth2
    net.addLink(h3, s2)  # s2-eth1
    net.addLink(h4, s2)  # s2-eth2
    net.addLink(s1, s2)  # s1-eth3 <-> s2-eth3 (trunk)

    return net


def apply_vlans(net):
    for switch in net.switches:
        for intf_name, vlan in ACCESS_VLAN.items():
            if intf_name.startswith(switch.name + '-'):
                switch.cmd('ovs-vsctl set port', intf_name, 'tag={}'.format(vlan))


def disable_ipv6(net):
    for host in net.hosts:
        host.cmd('sysctl -qw net.ipv6.conf.all.disable_ipv6=1')
        host.cmd('sysctl -qw net.ipv6.conf.default.disable_ipv6=1')
    for switch in net.switches:
        switch.cmd('ovs-appctl fdb/flush', switch)


def main():
    net = build_network()
    net.start()
    apply_vlans(net)
    disable_ipv6(net)

    info('\n*** Topologia lista (los 4 hosts comparten la red 10.0.0.0/24):\n')
    info('***   VLAN 10: h1 (10.0.0.1, en s1) <-> h3 (10.0.0.3, en s2)\n')
    info('***   VLAN 20: h2 (10.0.0.2, en s1) <-> h4 (10.0.0.4, en s2)\n')
    info('***   s1-eth3 <-> s2-eth3 es el enlace "trunk" que lleva ambas VLANs etiquetadas\n')
    info('*** Comandos sugeridos:\n')
    info('h1 ping -c 2 10.0.0.3   # misma VLAN, distinto switch: deberia funcionar\n')
    info('h1 ping -c 2 10.0.0.2   # distinta VLAN, mismo switch: NO deberia funcionar\n')
    info('sh ovs-vsctl list port s1-eth1 | grep tag\n')
    info('exit\n\n')

    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    main()
