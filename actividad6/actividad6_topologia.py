from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel
from mininet.net import Mininet
from mininet.node import OVSSwitch

# Los enlaces ENTRE switches van limitados a 1 Mb/s a proposito: si se forma
# una tormenta de difusion (broadcast storm) sin control, el limite evita que
# sature la CPU de la VM (1 nucleo, 1 GB de RAM). Asi la tormenta se ve
# clarísimo en los contadores de paquetes, pero no puede colgar la maquina.
INTERSWITCH_BW = 1


def build_network(stp=False):
    # Tres switches en triangulo: s1-s2, s2-s3 y s3-s1. Sin ese tercer enlace
    # no habria bucle. Con el, una trama de difusion (broadcast) que entra
    # por un switch puede volver a el por el otro lado y circular sin fin,
    # salvo que algo lo evite (por eso existe STP).
    net = Mininet(controller=None, autoSetMacs=True, listenPort=6655)

    info('*** Agregando hosts\n')
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.0.2/24')
    h3 = net.addHost('h3', ip='10.0.0.3/24')

    info('*** Agregando switches\n')
    stp_cfg = {'stp': True} if stp else {}
    s1 = net.addSwitch('s1', cls=OVSSwitch, failMode='standalone', **stp_cfg)
    s2 = net.addSwitch('s2', cls=OVSSwitch, failMode='standalone', **stp_cfg)
    s3 = net.addSwitch('s3', cls=OVSSwitch, failMode='standalone', **stp_cfg)

    info('*** Creando enlaces (triangulo entre switches: hay un bucle)\n')
    net.addLink(h1, s1)
    net.addLink(h2, s2)
    net.addLink(h3, s3)
    net.addLink(s1, s2, cls=TCLink, bw=INTERSWITCH_BW)
    net.addLink(s2, s3, cls=TCLink, bw=INTERSWITCH_BW)
    net.addLink(s3, s1, cls=TCLink, bw=INTERSWITCH_BW)

    return net


def disable_ipv6(net):
    for host in net.hosts:
        host.cmd('sysctl -qw net.ipv6.conf.all.disable_ipv6=1')
        host.cmd('sysctl -qw net.ipv6.conf.default.disable_ipv6=1')
    for switch in net.switches:
        switch.cmd('ovs-appctl fdb/flush', switch)


def main():
    import sys
    stp = '--stp' in sys.argv
    net = build_network(stp=stp)
    net.start()
    disable_ipv6(net)

    info('\n*** Topologia lista: h1-s1, h2-s2, h3-s3, triangulo s1-s2-s3 (enlaces entre '
         'switches a {} Mb/s)\n'.format(INTERSWITCH_BW))
    info('*** STP {}\n'.format('activado' if stp else 'DESACTIVADO (hay un bucle sin control)'))
    info('*** Comandos sugeridos:\n')
    if not stp:
        info('h1 ping -c 1 h2   # unicast: no entra en bucle, funciona normal\n')
        info('sh ovs-ofctl dump-ports s1   # contador de paquetes por puerto, antes de la tormenta\n')
        info('h1 ping -b -c 1 -W 1 10.0.0.255   # UN broadcast: dispara la tormenta\n')
        info('sh ovs-ofctl dump-ports s1   # mismo contador, segundos despues: deberia haber explotado\n')
        info('sh link s1 s2 down   # cortar el bucle para frenar la tormenta\n')
    else:
        info('sh ovs-vsctl get port s1-eth2 status:stp_state   # esperar ~35s desde el arranque\n')
        info('sh ovs-vsctl get port s2-eth2 status:stp_state\n')
        info('sh ovs-vsctl get port s3-eth2 status:stp_state\n')
        info('h1 ping -b -c 1 -W 1 10.0.0.255   # mismo broadcast: ahora no deberia haber tormenta\n')
    info('exit\n\n')

    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    main()
