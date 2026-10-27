import sys
import time
from pathlib import Path

from mininet.log import info, setLogLevel

# Como el script corre con sudo, no queremos dejar un __pycache__ de root en la carpeta.
sys.dont_write_bytecode = True
from actividad7_topologia import apply_vlans, build_network, disable_ipv6

RESULTS_FILE = Path('actividad7_vlans_resultados.txt')
TRUNK_PCAP = Path('trunk_vlan10.pcap')
lines = []


def report(text=''):
    info(text + '\n')
    lines.append(text)


def try_ping(h1, h2):
    out = h1.cmd('ping -c 2 -W 1', h2.IP())
    # Ojo: "100% packet loss" tambien contiene "0% packet loss" como
    # substring. Con el espacio antes del "0" no hay ambiguedad.
    ok = ' 0% packet loss' in out
    return ok


def main():
    net = build_network()
    net.start()
    apply_vlans(net)
    disable_ipv6(net)
    h1, h2, h3, h4 = net.get('h1', 'h2', 'h3', 'h4')

    report('Actividad 7 - VLANs: segmentacion de capa 2 sobre el mismo cableado fisico')
    report('h1=10.0.0.1 (VLAN10, s1) | h2=10.0.0.2 (VLAN20, s1) | '
           'h3=10.0.0.3 (VLAN10, s2) | h4=10.0.0.4 (VLAN20, s2)')
    report('Los 4 hosts comparten la red 10.0.0.0/24: si un ping falla, es por la VLAN, '
           'no por falta de ruta.')

    report('')
    report('=== Matriz de conectividad ===')
    pares = [
        (h1, h3, 'VLAN10 <-> VLAN10, cruzando switch (s1-s2)'),
        (h2, h4, 'VLAN20 <-> VLAN20, cruzando switch (s1-s2)'),
        (h1, h2, 'VLAN10 <-> VLAN20, mismo switch (s1)'),
        (h3, h4, 'VLAN10 <-> VLAN20, mismo switch (s2)'),
        (h1, h4, 'VLAN10 <-> VLAN20, cruzando switch'),
    ]
    for origen, destino, descripcion in pares:
        ok = try_ping(origen, destino)
        report('{} -> {} ({}): {}'.format(
            origen.name, destino.name, descripcion, 'OK' if ok else 'SIN RESPUESTA'))

    report('')
    report('=== Captura en el enlace trunk (s1-eth3) durante un ping h1 -> h3 (VLAN10) ===')
    s1 = net.get('s1')
    s1.cmd('rm -f', TRUNK_PCAP)
    s1.cmd('tcpdump -e -n -i s1-eth3 -w {} icmp 2>/dev/null &'.format(TRUNK_PCAP))
    time.sleep(1)
    h1.cmd('ping -c 2 -W 1', h3.IP())
    time.sleep(1)
    s1.cmd('kill %tcpdump')
    time.sleep(1)
    salida = s1.cmd('tcpdump -e -n -r', TRUNK_PCAP, '2>/dev/null').strip()
    for linea in salida.splitlines():
        report('   ' + linea)
    report('')
    report('Fijate el campo "vlan 10" en cada trama: viaja asi SOLO por el enlace trunk. '
           'En el puerto de acceso de h1 o h3 esa etiqueta no existe (el switch la agrega '
           'al entrar al trunk y la quita al salir por el puerto de acceso).')

    RESULTS_FILE.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    info('\n*** Resultados guardados en {}\n'.format(RESULTS_FILE))
    info('*** Captura: {} (abrila con Wireshark para ver la etiqueta 802.1Q en el detalle de '
         'la trama)\n'.format(TRUNK_PCAP))
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    main()
