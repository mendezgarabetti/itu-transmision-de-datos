import argparse

from mininet.cli import CLI
from mininet.link import TCIntf, TCLink
from mininet.log import info, setLogLevel
from mininet.net import Mininet
from mininet.node import OVSSwitch

# Mininet acepta como máximo 1000 Mb/s en "bw"; lo ampliamos para el segmento de 10 Gb/s.
TCIntf.bwParamMax = 10000

# Velocidad de cada segmento, en megabits por segundo.
SEGMENTS = [1, 10, 100, 1000, 10000]


def label(mbps):
    return '{} Gb/s'.format(mbps // 1000) if mbps >= 1000 else '{} Mb/s'.format(mbps)


def build_network(delay='1ms', loss=0):
    # Una sola red 10.0.0.0/24, sin router: un switch central (s0) y un switch por
    # segmento (s1 a s5). Dentro de cada segmento, todos los enlaces tienen la misma
    # velocidad, incluido el que lo une con s0.
    net = Mininet(controller=None, link=TCLink, autoSetMacs=True, listenPort=6654)
    core = net.addSwitch('s0', cls=OVSSwitch, failMode='standalone', dpid='100')

    for n, mbps in enumerate(SEGMENTS, start=1):
        options = {'bw': mbps}
        if delay:
            options['delay'] = delay
        if loss:
            options['loss'] = loss

        switch = net.addSwitch('s{}'.format(n), cls=OVSSwitch, failMode='standalone')
        net.addLink(switch, core, **options)
        for k in (1, 2):
            host = net.addHost('h{}{}'.format(n, k), ip='10.0.0.{}{}/24'.format(n, k))
            net.addLink(host, switch, **options)

    return net


def parse_args():
    parser = argparse.ArgumentParser(description='Red con enlaces de 1 Mb/s a 10 Gb/s')
    parser.add_argument('--delay', default='1ms',
                        help='retardo de cada enlace, por ejemplo 5ms (por defecto 1ms; 0 = sin retardo)')
    parser.add_argument('--loss', type=float, default=0,
                        help='porcentaje de perdida de cada enlace, por ejemplo 1 (por defecto 0)')
    args = parser.parse_args()
    if args.delay in ('0', '0ms'):
        args.delay = None
    return args


def main():
    args = parse_args()
    net = build_network(delay=args.delay, loss=args.loss)
    net.start()

    info('\n*** Red lista (retardo por enlace: {}, perdida por enlace: {}%)\n'.format(
        args.delay or '0', args.loss))
    for n, mbps in enumerate(SEGMENTS, start=1):
        info('    Segmento {}: s{} a {:>8}  ->  h{}1 (10.0.0.{}1) y h{}2 (10.0.0.{}2)\n'.format(
            n, n, label(mbps), n, n, n, n))
    info('*** Comandos sugeridos:\n')
    info('h11 ping -c 5 h12\n')
    info('iperf h31 h32\n')
    info('iperfudp 150M h31 h32\n')
    info('iperf h11 h52\n')
    info('exit\n\n')

    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    main()
