# Actividad 1 · Unidad 2: ARP e ICMP en Mininet

## Objetivo

Construir una topología mínima en Mininet, verificar conectividad y analizar en Wireshark el
tráfico ARP e ICMP que genera un `ping`.

```
        c0 (controlador)
         |  OpenFlow
        s1 (Open vSwitch)
       /              \
  h1 10.0.0.1/24    h2 10.0.0.2/24
```

## Archivos

- `hola_mininet.py`: prueba rápida; levanta la red, hace un ping y se apaga.
- `actividad1_topologia.py`: topología interactiva para usar en clase (consola `mininet>`).
- `actividad1_generar_captura.py`: captura en `s1-eth1` y genera un `.pcap` y un resumen en texto.

## 1. Prueba rápida

```bash
cd ~/itu-transmision-de-datos/actividad1
sudo python3 hola_mininet.py
```

## 2. Modo interactivo

```bash
sudo python3 actividad1_topologia.py
```

Dentro de Mininet:

```text
nodes
net
h1 ping -c 2 h2
h1 ip neigh show
h2 ip neigh show
exit
```

## 3. Captura automática

```bash
sudo python3 actividad1_generar_captura.py
```

Genera `actividad1_arp_icmp.pcap` y `actividad1_arp_icmp_resumen.txt`.

## 4. Abrir la captura

Sin interfaz gráfica:

```bash
tshark -r actividad1_arp_icmp.pcap
```

Con Wireshark (requiere conexión con `ssh -X`):

```bash
wireshark actividad1_arp_icmp.pcap &
```

### Desde Windows con PuTTY y Xming

Si `xclock` abre pero `wireshark` falla, el problema es que Xming no soporta las extensiones
gráficas que usa la versión Qt de Wireshark. Alternativas:

```bash
# a) versión GTK (disponible en la VM con Ubuntu 16.04)
wireshark-gtk actividad1_arp_icmp.pcap &

# b) versión Qt sin memoria compartida ni aceleración
export QT_X11_NO_MITSHM=1
export LIBGL_ALWAYS_INDIRECT=1
wireshark actividad1_arp_icmp.pcap &
```

Para abrir un archivo **no hace falta `sudo`**. Si necesitás capturar en vivo como root:
`sudo XAUTHORITY=$HOME/.Xauthority wireshark-gtk &`.

También podés copiar la captura a tu computadora y abrirla con tu Wireshark local:

```bash
scp mininet@<IP_DE_TU_VM>:~/itu-transmision-de-datos/actividad1/actividad1_arp_icmp.pcap .
```

## Qué debería observarse

Con `ping -c 2` la captura tiene **6 paquetes**:

| N° | Protocolo | Info (como la muestra Wireshark) |
| :-: | :-: | :--- |
| 1 | ARP | Who has 10.0.0.2? Tell 10.0.0.1 |
| 2 | ARP | 10.0.0.2 is at *MAC de h2* |
| 3 | ICMP | Echo (ping) request, seq=1 |
| 4 | ICMP | Echo (ping) reply, seq=1 |
| 5 | ICMP | Echo (ping) request, seq=2 |
| 6 | ICMP | Echo (ping) reply, seq=2 |

Campos para revisar en el panel de detalle:

- **Ethernet II:** MAC destino (`ff:ff:ff:ff:ff:ff` en el ARP Request), MAC origen y tipo
  (`0x0806` ARP, `0x0800` IPv4).
- **ARP:** opcode (1 request, 2 reply), MAC e IP del emisor y del destino.
- **IPv4:** direcciones, TTL y protocolo (`1` = ICMP).
- **ICMP:** tipo (8 request, 0 reply), identificador, número de secuencia y tiempo de respuesta.

Si `ping` se repite en modo interactivo, el primer paso ARP desaparece: la MAC de h2 ya está en
la caché de h1 (`h1 ip neigh show`). Para repetir la experiencia: `h1 ip neigh flush all`.
