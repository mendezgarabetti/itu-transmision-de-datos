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


def server_report(host, path, timeout=60):
    # iperf -y C: el servidor escribe una linea CSV recien cuando recibio todo.
    deadline = time.time() + timeout
    while time.time() < deadline:
        for line in host.cmd('cat', path).splitlines():
            if line.count(',') >= 8:
                return line.split(',')
        time.sleep(1)
    return None


def run_transfer(net, pcap_file):
    h1, h2 = net.get('h1', 'h2')
    report_file = '/tmp/iperf_servidor.csv'
    h1.cmd('rm -f', pcap_file)
    h2.cmd('rm -f', report_file)
    # --immediate-mode: sin el, tcpdump recibe los paquetes del kernel en bloques
    # y, si se lo corta enseguida, la captura queda incompleta.
    h1.cmd('tcpdump -n --immediate-mode -i h1-eth0 -w {} tcp 2>/dev/null &'.format(pcap_file))
    time.sleep(1)
    h2.cmd('iperf -s -y C > {} 2>/dev/null &'.format(report_file))
    time.sleep(1)
    h1.cmd('iperf -c 10.0.0.2 -n {} > /dev/null 2>&1'.format(TRANSFER))
    # El cliente termina cuando sus datos entraron en la cola de salida, no cuando
    # llegaron. La velocidad se toma del servidor, que informa al recibir todo.
    row = server_report(h2, report_file)
    time.sleep(1)
    h2.cmd('kill %iperf')
    h1.cmd('kill %tcpdump')
    time.sleep(1)

    total = int(h1.cmd('tcpdump -n -r', pcap_file, '2>/dev/null | wc -l').strip() or 0)
    retrans = h1.cmd(
        'tshark -r {} -Y "tcp.analysis.retransmission" 2>/dev/null | wc -l'.format(pcap_file)
    ).strip()
    speed = '{:.2f} Mbits/sec'.format(int(row[8]) / 1e6) if row else None
    return total, int(retrans or 0), speed


def main():
    net = build_network()
    net.start()
    h1 = net.get('h1')

    report('Actividad 5 - Control de errores: bits invertidos y retransmision de TCP')
    report('Transferencia TCP de {} entre h1 y h2 (enlace de h1 limitado a {}), midiendo con '
           'tcpdump/tshark en h1. La velocidad es la que midio el servidor (h2).'.format(TRANSFER, LINK_RATE))

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
