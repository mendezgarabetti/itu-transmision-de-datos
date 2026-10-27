import time
from pathlib import Path

from mininet.log import info, setLogLevel

from actividad3_topologia import build_network, disable_ipv6

RESULTS_FILE = Path('actividad3_tablas_mac_resultados.txt')
AGING_TIME = 10
lines = []


def report(text=''):
    info(text + '\n')
    lines.append(text)


def mac_names(net):
    return {host.MAC(): host.name for host in net.hosts}


def show_tables(net, title):
    names = mac_names(net)
    report('')
    report('=== {} ==='.format(title))
    for switch in net.switches:
        output = switch.cmd('ovs-appctl fdb/show', switch).strip().splitlines()
        entries = output[1:]
        report('Tabla MAC de {}: {} entradas'.format(switch.name, len(entries)))
        report('   puerto  MAC                 host  edad (s)')
        for entry in entries:
            port, _vlan, mac, age = entry.split()
            report('   {:<7} {:<19} {:<5} {}'.format(port, mac, names.get(mac, '?'), age))


def count_icmp_seen_by(host, action):
    # Captura en la interfaz del host solo los ICMP que NO son para él.
    capture = '/tmp/{}_icmp.pcap'.format(host.name)
    host.cmd('rm -f', capture)
    host.cmd('tcpdump -i {}-eth0 -n -U -w {} "icmp and not host {}" &'.format(
        host.name, capture, host.IP()))
    time.sleep(2)
    action()
    time.sleep(1)
    host.cmd('kill %tcpdump')
    time.sleep(1)
    output = host.cmd('tcpdump -n -r', capture, '2>/dev/null')
    return [line for line in output.splitlines() if 'ICMP' in line]


def main():
    net = build_network()
    net.start()
    disable_ipv6(net)
    h1, h2, h3, h4 = net.get('h1', 'h2', 'h3', 'h4')

    report('Actividad 3 - Tablas MAC en switches Ethernet')
    report('MACs: ' + ', '.join('{} = {}'.format(h.name, h.MAC()) for h in net.hosts))
    report('Puertos: s1-eth1 = h1, s1-eth2 = h2, s2-eth1 = h3, s2-eth2 = h4, '
           's1-eth3 <-> s2-eth3 (enlace entre switches)')

    show_tables(net, 'Paso 0: recien encendidos')

    h1.cmd('ping -c 1 10.0.0.2')
    show_tables(net, 'Paso 1: h1 ping h2')

    h1.cmd('ping -c 1 10.0.0.4')
    show_tables(net, 'Paso 2: h1 ping h4')

    net.pingAll()
    show_tables(net, 'Paso 3: pingall')

    report('')
    report('=== Paso 4: h3 ve el trafico entre h1 y h2? ===')
    seen = count_icmp_seen_by(h3, lambda: h1.cmd('ping -c 3 10.0.0.2'))
    report('Con las tablas completas, h3 recibio {} paquetes ICMP ajenos.'.format(len(seen)))
    for switch in net.switches:
        switch.cmd('ovs-appctl fdb/flush', switch)
    seen = count_icmp_seen_by(h3, lambda: h1.cmd('ping -c 3 10.0.0.2'))
    report('Con las tablas vaciadas, h3 recibio {} paquetes ICMP ajenos:'.format(len(seen)))
    for line in seen:
        report('   ' + line)

    report('')
    report('=== Paso 5: envejecimiento (aging time = {} s) ==='.format(AGING_TIME))
    for switch in net.switches:
        switch.cmd('ovs-vsctl set bridge', switch,
                   'other_config:mac-aging-time={}'.format(AGING_TIME))
    net.pingAll()
    show_tables(net, 'Paso 5a: despues de pingall')
    report('Esperando {} segundos sin trafico...'.format(AGING_TIME * 2 + 5))
    time.sleep(AGING_TIME * 2 + 5)
    show_tables(net, 'Paso 5b: tras {} s sin trafico'.format(AGING_TIME * 2 + 5))

    RESULTS_FILE.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    info('\n*** Resultados guardados en {}\n'.format(RESULTS_FILE))
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    main()
