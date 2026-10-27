import sys
import time
from pathlib import Path

from mininet.log import info, setLogLevel

# Como el script corre con sudo, no queremos dejar un __pycache__ de root en la carpeta.
sys.dont_write_bytecode = True
from actividad5_topologia import LINK_RATE, build_network, set_corrupt

RESULTS_FILE = Path('actividad5_errores_resultados.txt')
TRANSFER = '2M'
lines = []


def report(text=''):
    info(text + '\n')
    lines.append(text)


def run_transfer(net, pcap_file):
    h1, h2 = net.get('h1', 'h2')
    h1.cmd('rm -f', pcap_file)
    h1.cmd('tcpdump -n -i h1-eth0 -w {} tcp 2>/dev/null &'.format(pcap_file))
    time.sleep(1)
    h2.cmd('iperf -s > /dev/null 2>&1 &')
    time.sleep(1)
    out = h1.cmd('iperf -c 10.0.0.2 -n {}'.format(TRANSFER))
    h2.cmd('kill %iperf')
    h1.cmd('kill %tcpdump')
    time.sleep(1)

    total = int(h1.cmd('tcpdump -n -r', pcap_file, '2>/dev/null | wc -l').strip() or 0)
    retrans = h1.cmd(
        'tshark -r {} -Y "tcp.analysis.retransmission" 2>/dev/null | wc -l'.format(pcap_file)
    ).strip()
    speed = None
    for line in out.splitlines():
        if '/sec' in line:
            speed = line.strip().split()[-2] + ' ' + line.strip().split()[-1]
    return total, int(retrans or 0), speed


def main():
    net = build_network()
    net.start()
    h1 = net.get('h1')

    report('Actividad 5 - Control de errores: bits invertidos y retransmision de TCP')
    report('Transferencia TCP de {} entre h1 y h2 (enlace de h1 limitado a {}), midiendo con '
           'tcpdump/tshark en h1.'.format(TRANSFER, LINK_RATE))

    report('')
    report('=== 1. Enlace sin errores (0%) ===')
    set_corrupt(h1, 0)
    total, retrans, speed = run_transfer(net, 'sin_errores.pcap')
    report('Paquetes capturados: {} | Retransmisiones detectadas: {} | Velocidad: {}'.format(
        total, retrans, speed or 'sin dato'))

    report('')
    report('=== 2. Enlace con 5% de paquetes con un bit invertido ===')
    set_corrupt(h1, 5)
    total, retrans, speed = run_transfer(net, 'con_errores_5.pcap')
    report('Paquetes capturados: {} | Retransmisiones detectadas: {} | Velocidad: {}'.format(
        total, retrans, speed or 'sin dato'))

    report('')
    report('=== 3. Enlace con 15% de paquetes con un bit invertido ===')
    set_corrupt(h1, 15)
    total, retrans, speed = run_transfer(net, 'con_errores_15.pcap')
    report('Paquetes capturados: {} | Retransmisiones detectadas: {} | Velocidad: {}'.format(
        total, retrans, speed or 'sin dato'))

    set_corrupt(h1, 0)
    RESULTS_FILE.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    info('\n*** Resultados guardados en {}\n'.format(RESULTS_FILE))
    info('*** Capturas: sin_errores.pcap, con_errores_5.pcap, con_errores_15.pcap (abrilas con Wireshark)\n')
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    main()
