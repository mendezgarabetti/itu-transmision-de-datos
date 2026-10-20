from mininet.cli import CLI
from mininet.log import info, setLogLevel
from mininet.net import Mininet
from mininet.node import OVSSwitch


def build_network():
    # Sin controlador: cada switch trabaja en modo "standalone", como un
    # switch Ethernet clásico que aprende las direcciones MAC por su cuenta.
    # autoSetMacs asigna MACs fáciles de leer: h1 = 00:00:00:00:00:01, etc.
    net = Mininet(controller=None, autoSetMacs=True, listenPort=6654)

    info('*** Agregando hosts\n')
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.0.2/24')
    h3 = net.addHost('h3', ip='10.0.0.3/24')
    h4 = net.addHost('h4', ip='10.0.0.4/24')

    info('*** Agregando switches\n')
    s1 = net.addSwitch('s1', cls=OVSSwitch, failMode='standalone')
    s2 = net.addSwitch('s2', cls=OVSSwitch, failMode='standalone')

    info('*** Creando enlaces\n')
    net.addLink(h1, s1)  # s1 puerto 1
    net.addLink(h2, s1)  # s1 puerto 2
    net.addLink(h3, s2)  # s2 puerto 1
    net.addLink(h4, s2)  # s2 puerto 2
    net.addLink(s1, s2)  # s1 puerto 3 <-> s2 puerto 3

    return net


def disable_ipv6(net):
    # Con IPv6 activo, hosts y switches emiten tráfico propio (descubrimiento
    # de vecinos) que ensucia las tablas. Sin él, las tablas empiezan vacías
    # y solo aprenden de nuestros pings.
    for host in net.hosts:
        host.cmd('sysctl -qw net.ipv6.conf.all.disable_ipv6=1')
        host.cmd('sysctl -qw net.ipv6.conf.default.disable_ipv6=1')
    for switch in net.switches:
        for name in [switch.name] + [intf.name for intf in switch.intfList()]:
            switch.cmd('sysctl -qw net.ipv6.conf.{}.disable_ipv6=1 2>/dev/null'.format(name))
    for switch in net.switches:
        switch.cmd('ovs-appctl fdb/flush', switch)


def main():
    net = build_network()
    net.start()
    disable_ipv6(net)

    info('\n*** Topologia lista: h1 y h2 en s1, h3 y h4 en s2\n')
    info('*** Comandos sugeridos para la actividad:\n')
    info('sh ovs-appctl fdb/show s1\n')
    info('h1 ping -c 1 h2\n')
    info('sh ovs-appctl fdb/show s1\n')
    info('sh ovs-appctl fdb/show s2\n')
    info('pingall\n')
    info('sh ovs-appctl fdb/flush s1\n')
    info('exit\n\n')

    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    main()
