import re
import sys
import time
from pathlib import Path

from mininet.log import info, setLogLevel

# Como el script corre con sudo, no queremos dejar un __pycache__ de root en la carpeta.
sys.dont_write_bytecode = True
from actividad2_topologia import SEGMENTS, build_network, label, parse_args

RESULTS_FILE = Path('actividad2_mediciones_resultados.txt')
SECONDS = 5
lines = []


def report(text=''):
    info(text + '\n')
    lines.append(text)


def ping(src, dst, count=10):
    out = src.cmd('ping -c {} -i 0.2 {}'.format(count, dst.IP()))
    rtt = re.search(r'= [\d.]+/([\d.]+)/', out)
    loss = re.search(r'([\d.]+)% packet loss', out)
    return (float(rtt.group(1)) if rtt else None,
            float(loss.group(1)) if loss else None)


def csv_rows(output, min_fields):
    # iperf -y C imprime una línea CSV por reporte.
    return [line.split(',') for line in output.splitlines()
            if line.count(',') >= min_fields - 1]


def server_rows(host, path, min_fields, timeout=40):
    # El servidor informa recién cuando le llegó todo, incluido lo que quedó en
    # la cola del enlace; en los enlaces lentos eso puede tardar varios segundos.
    deadline = time.time() + timeout
    while time.time() < deadline:
        rows = csv_rows(host.cmd('cat', path), min_fields)
        if rows:
            return rows
        time.sleep(1)
    return []


def iperf_tcp(src, dst, seconds=SECONDS):
    # Se mide en el receptor: cuenta lo que llegó, no lo que se escribió en la cola.
    path = '/tmp/iperf_tcp_{}.csv'.format(dst.name)
    dst.cmd('rm -f', path)
    dst.cmd('iperf -s -y C > {} 2>/dev/null &'.format(path))
    time.sleep(1)
    src.cmd('iperf -c {} -t {} > /dev/null 2>&1'.format(dst.IP(), seconds))
    rows = server_rows(dst, path, 9)
    dst.cmd('kill %iperf')
    return int(rows[-1][8]) / 1e6 if rows else None


def iperf_udp(src, dst, mbps, seconds=SECONDS):
    # El reporte del servidor (14 campos) trae lo recibido y la pérdida medida en el destino.
    path = '/tmp/iperf_udp_{}.csv'.format(dst.name)
    dst.cmd('rm -f', path)
    dst.cmd('iperf -s -u -y C > {} 2>/dev/null &'.format(path))
    time.sleep(1)
    src.cmd('iperf -c {} -u -b {}K -t {} > /dev/null 2>&1'.format(
        dst.IP(), int(mbps * 1000), seconds))
    rows = server_rows(dst, path, 14)
    dst.cmd('kill %iperf')
    if not rows:
        return None, None
    return int(rows[-1][8]) / 1e6, float(rows[-1][12])


def fmt(value, pattern):
    return pattern.format(value) if value is not None else 'sin dato'


def main():
    args = parse_args()
    net = build_network(delay=args.delay, loss=args.loss)
    net.start()
    report('Actividad 2 - Enlaces, ancho de banda, latencia y perdida')
    report('Retardo por enlace: {} | Perdida por enlace: {}% | Cada prueba dura {} s'.format(
        args.delay or '0', args.loss, SECONDS))

    report('')
    report('=== 1. Dentro de cada segmento (hN1 -> hN2) ===')
    report('{:<10} {:>9} {:>11} {:>14} {:>16} {:>16}'.format(
        'Enlace', 'RTT (ms)', 'TCP (Mb/s)', 'UDP 50%: perd', 'UDP 150%: llega', 'UDP 150%: perd'))
    for n, mbps in enumerate(SEGMENTS, start=1):
        a, b = net.get('h{}1'.format(n), 'h{}2'.format(n))
        rtt, _ = ping(a, b)
        tcp = iperf_tcp(a, b)
        _, loss_half = iperf_udp(a, b, mbps * 0.5)
        got_over, loss_over = iperf_udp(a, b, mbps * 1.5)
        report('{:<10} {:>9} {:>11} {:>14} {:>16} {:>16}'.format(
            label(mbps), fmt(rtt, '{:.2f}'), fmt(tcp, '{:.2f}'), fmt(loss_half, '{:.1f}%'),
            fmt(got_over, '{:.2f} Mb/s'), fmt(loss_over, '{:.1f}%')))

    report('')
    report('=== 2. Entre segmentos: manda el enlace mas lento del camino ===')
    for src, dst in (('h11', 'h52'), ('h31', 'h41'), ('h41', 'h52')):
        a, b = net.get(src, dst)
        rtt, _ = ping(a, b)
        tcp = iperf_tcp(a, b)
        report('{} -> {}: TCP {} Mb/s | RTT {} ms'.format(
            src, dst, fmt(tcp, '{:.2f}'), fmt(rtt, '{:.2f}')))

    report('')
    report('=== 3. Latencia con el enlace cargado (segmento de 1 Mb/s) ===')
    a, b = net.get('h11', 'h12')
    idle, _ = ping(a, b)
    b.cmd('iperf -s > /dev/null 2>&1 &')
    time.sleep(1)
    a.cmd('iperf -c {} -t 8 > /dev/null 2>&1 &'.format(b.IP()))
    time.sleep(3)
    loaded, _ = ping(a, b, count=20)
    a.cmd('wait')
    b.cmd('kill %iperf')
    report('RTT sin carga: {} ms | RTT durante una descarga TCP: {} ms'.format(
        fmt(idle, '{:.2f}'), fmt(loaded, '{:.2f}')))

    RESULTS_FILE.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    info('\n*** Resultados guardados en {}\n'.format(RESULTS_FILE))
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    main()
