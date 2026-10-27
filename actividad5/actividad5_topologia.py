import argparse

from mininet.cli import CLI
from mininet.log import info, setLogLevel
from mininet.net import Mininet
from mininet.node import Controller


def build_network():
    net = Mininet(controller=Controller)

    info('*** Agregando controlador\n')
    net.addController('c0')

    info('*** Agregando hosts\n')
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.0.2/24')

    info('*** Agregando switch\n')
    s1 = net.addSwitch('s1')

    info('*** Creando enlaces\n')
    net.addLink(h1, s1)
    net.addLink(h2, s1)

    return net


LINK_RATE = '10mbit'


def set_corrupt(host, pct):
    # Un solo bit al azar se invierte en una fraccion de los paquetes que salen
    # por esta interfaz. El checksum calculado antes queda invalido: es un
    # error de transmision simulado, no una perdida. La tasa se limita a
    # LINK_RATE en el mismo qdisc para que las capturas no crezcan sin limite.
    host.cmd('tc qdisc del dev {}-eth0 root 2>/dev/null'.format(host.name))
    corrupt = ' corrupt {}%'.format(pct) if pct else ''
    host.cmd('tc qdisc add dev {}-eth0 root netem rate {}{}'.format(
        host.name, LINK_RATE, corrupt))


def parse_args():
    parser = argparse.ArgumentParser(description='Enlace con errores de transmision simulados (netem corrupt)')
    parser.add_argument('--corrupt', type=float, default=5,
                        help='porcentaje de paquetes de h1 con un bit invertido (por defecto 5; 0 = sin errores)')
    return parser.parse_args()


def main():
    args = parse_args()
    net = build_network()
    net.start()
    h1 = net.get('h1')
    set_corrupt(h1, args.corrupt)

    info('\n*** Topologia lista: h1 (10.0.0.1) y h2 (10.0.0.2), enlace de h1 a {} con {}% de errores\n'.format(
        LINK_RATE, args.corrupt))
    info('*** Comandos sugeridos para la actividad:\n')
    info('h2 iperf -s > /dev/null 2>&1 &\n')
    info('h1 tcpdump -n -i h1-eth0 -w captura.pcap tcp &\n')
    info('h1 iperf -c 10.0.0.2 -n 2M\n')
    info('h1 kill %tcpdump\n')
    info('exit\n\n')

    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    main()
