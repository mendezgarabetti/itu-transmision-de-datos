import sys
import time
from pathlib import Path

from mininet.log import info, setLogLevel

# Como el script corre con sudo, no queremos dejar un __pycache__ de root en la carpeta.
sys.dont_write_bytecode = True
from actividad4_topologia import build_network

RESULTS_FILE = Path('actividad4_handshake_resultados.txt')
PORT = 5000
lines = []


def report(text=''):
    info(text + '\n')
    lines.append(text)


def capture(host, pcap_file, bpf_filter, action, settle=1):
    host.cmd('rm -f', pcap_file)
    host.cmd('tcpdump -n -i {}-eth0 -w {} {} 2>/dev/null &'.format(host.name, pcap_file, bpf_filter))
    time.sleep(1)
    action()
    time.sleep(settle)
    host.cmd('kill %tcpdump')
    time.sleep(1)
    return host.cmd('tcpdump -n -r', pcap_file, '2>/dev/null').strip()


def main():
    net = build_network()
    net.start()
    h1, h2 = net.get('h1', 'h2')

    report('Actividad 4 - Establecimiento y liberacion de una conexion TCP')
    report('h1 = cliente (10.0.0.1), h2 = servidor (10.0.0.2), puerto {}'.format(PORT))

    h2.cmd('python3 tcp_echo_server.py {} > /tmp/servidor.log 2>&1 &'.format(PORT))
    time.sleep(1)

    report('')
    report('=== 1. Conexion TCP normal: handshake + datos + cierre con FIN ===')
    dump = capture(h1, 'tcp_normal.pcap', 'tcp port {}'.format(PORT),
                   lambda: h1.cmd('python3 tcp_client.py 10.0.0.2 {} hola'.format(PORT)))
    report(dump)

    report('')
    report('=== 2. Conexion TCP con cierre abrupto (RST en vez de FIN) ===')
    dump = capture(h1, 'tcp_rst.pcap', 'tcp port {}'.format(PORT),
                   lambda: h1.cmd('python3 tcp_client.py 10.0.0.2 {} hola --rst'.format(PORT)))
    report(dump)

    report('')
    report('=== 3. Un datagrama UDP, sin conexion previa (para comparar) ===')
    dump = capture(h1, 'udp_demo.pcap', 'udp port {}'.format(PORT),
                   lambda: h1.cmd('python3 udp_send.py 10.0.0.2 {} hola'.format(PORT)), settle=1)
    report(dump)

    h2.cmd('kill %python3')

    RESULTS_FILE.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    info('\n*** Resultados guardados en {}\n'.format(RESULTS_FILE))
    info('*** Capturas: tcp_normal.pcap, tcp_rst.pcap, udp_demo.pcap (abrilas con Wireshark)\n')
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    main()
