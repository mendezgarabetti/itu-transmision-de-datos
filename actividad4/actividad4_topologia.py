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


def main():
    net = build_network()
    net.start()

    info('\n*** Topologia lista: h1 (cliente) y h2 (servidor) en el mismo switch\n')
    info('*** Comandos sugeridos para la actividad:\n')
    info('h2 python3 tcp_echo_server.py 5000 &\n')
    info('h1 tcpdump -n -i h1-eth0 -w captura.pcap tcp port 5000 &\n')
    info('h1 python3 tcp_client.py 10.0.0.2 5000 hola\n')
    info('h1 kill %tcpdump\n')
    info('h1 tcpdump -n -r captura.pcap\n')
    info('exit\n\n')

    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    main()
