import re
import sys
import time
from pathlib import Path

from mininet.log import info, setLogLevel

# Como el script corre con sudo, no queremos dejar un __pycache__ de root en la carpeta.
sys.dont_write_bytecode = True
from actividad6_topologia import build_network, disable_ipv6

RESULTS_FILE = Path('actividad6_storm_resultados.txt')
STORM_SECONDS = 3
STP_WAIT_SECONDS = 35  # STP tarda en converger: listening -> learning -> forwarding
PKT_RE = re.compile(r'pkts=(\d+)')
lines = []


def report(text=''):
    info(text + '\n')
    lines.append(text)


def total_packets(switch):
    out = switch.cmd('ovs-ofctl dump-ports', switch, '2>/dev/null')
    return sum(int(n) for n in PKT_RE.findall(out))


def run_case(net, titulo):
    h1 = net.get('h1')
    before = {s.name: total_packets(s) for s in net.switches}
    h1.cmd('ping -b -c 1 -W 1 10.0.0.255 > /dev/null 2>&1 &')
    time.sleep(STORM_SECONDS)
    after = {s.name: total_packets(s) for s in net.switches}

    report('')
    report('=== {} ==='.format(titulo))
    for switch in net.switches:
        delta = after[switch.name] - before[switch.name]
        report('{}: {} paquetes en {} s (antes {}, despues {})'.format(
            switch.name, delta, STORM_SECONDS, before[switch.name], after[switch.name]))


def main():
    report('Actividad 6 - Tormenta de difusion (broadcast storm) y STP')
    report('Se manda UN solo paquete broadcast desde h1 y se mide cuantos paquetes circularon '
           'por cada switch en los {} segundos siguientes. Los enlaces entre switches estan '
           'limitados a 1 Mb/s a proposito, para que una tormenta sin control no pueda saturar '
           'la VM.'.format(STORM_SECONDS))

    report('')
    report('########## CASO 1: sin STP (bucle fisico sin control) ##########')
    net = build_network(stp=False)
    net.start()
    disable_ipv6(net)
    run_case(net, 'Sin STP')
    info('*** Cortando el bucle antes de apagar, por las dudas\n')
    net.configLinkStatus('s1', 's2', 'down')
    time.sleep(1)
    net.stop()

    report('')
    report('########## CASO 2: con STP (mismo bucle fisico, bloqueado logicamente) ##########')
    net = build_network(stp=True)
    net.start()
    disable_ipv6(net)
    info('*** Esperando {} s a que STP converja...\n'.format(STP_WAIT_SECONDS))
    time.sleep(STP_WAIT_SECONDS)
    run_case(net, 'Con STP')
    net.stop()

    RESULTS_FILE.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    info('\n*** Resultados guardados en {}\n'.format(RESULTS_FILE))


if __name__ == '__main__':
    setLogLevel('info')
    main()
