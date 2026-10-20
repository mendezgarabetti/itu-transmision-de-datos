import subprocess
import time
from pathlib import Path

from mininet.log import info, setLogLevel
from mininet.net import Mininet
from mininet.node import Controller

CAPTURE_FILE = Path('actividad1_arp_icmp.pcap')
SUMMARY_FILE = Path('actividad1_arp_icmp_resumen.txt')


def build_network():
    net = Mininet(controller=Controller)
    net.addController('c0')
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.0.2/24')
    s1 = net.addSwitch('s1')
    net.addLink(h1, s1)
    net.addLink(h2, s1)
    return net, h1, h2


def main():
    net, h1, h2 = build_network()

    if CAPTURE_FILE.exists():
        CAPTURE_FILE.unlink()
    if SUMMARY_FILE.exists():
        SUMMARY_FILE.unlink()

    info('*** Iniciando red\n')
    net.start()

    info('*** Iniciando captura en s1-eth1\n')
    capture = subprocess.Popen(
        [
            'tcpdump', '-i', 's1-eth1', '-n', '-U', '-w', str(CAPTURE_FILE),
            'arp', 'or', 'icmp'
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    time.sleep(2)

    info('*** Limpiando caches ARP\n')
    h1.cmd('ip neigh flush all')
    h2.cmd('ip neigh flush all')

    info('*** Ejecutando ping de h1 a h2\n')
    ping_output = h1.cmd('ping -c 2 10.0.0.2')
    info(ping_output)

    time.sleep(2)

    info('*** Deteniendo captura\n')
    capture.terminate()
    capture.wait(timeout=5)

    info('*** Generando resumen legible\n')
    summary = subprocess.check_output(
        ['tshark', '-r', str(CAPTURE_FILE), '-V'],
        universal_newlines=True,
    )
    SUMMARY_FILE.write_text(summary)

    info('*** Archivos generados: {} y {}\n'.format(CAPTURE_FILE, SUMMARY_FILE))
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    main()
