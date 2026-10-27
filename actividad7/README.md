# Actividad 7 · VLANs: segmentar una red sin tocar el cableado

## Objetivo

Ver cómo una **VLAN (802.1Q)** separa una red en capa 2 sin importar qué switch físico use cada
host, y cómo esa separación se transporta entre switches por un único enlace **trunk**, usando
una etiqueta que viaja dentro de la propia trama Ethernet.

## Topología

Dos switches, dos hosts en cada uno, pero repartidos en dos VLANs distintas. Los 4 hosts
comparten la misma red IP (10.0.0.0/24) a propósito: si un ping falla, tiene que ser por la
VLAN, no porque falte una ruta.

```
   VLAN 10        VLAN 20              VLAN 10        VLAN 20
      h1             h2                   h3             h4
10.0.0.1(tag10) 10.0.0.2(tag20)     10.0.0.3(tag10) 10.0.0.4(tag20)
       \            /                      \            /
        \          /                        \          /
            s1 ──────────── trunk ──────────── s2
```

| Host | IP | VLAN | Switch |
| :-: | :-: | :-: | :-: |
| h1 | 10.0.0.1 | 10 | s1 |
| h2 | 10.0.0.2 | 20 | s1 |
| h3 | 10.0.0.3 | 10 | s2 |
| h4 | 10.0.0.4 | 20 | s2 |

El enlace `s1-eth3 <-> s2-eth3` es el único cable entre switches: es un puerto **trunk**, lleva
tramas de ambas VLANs al mismo tiempo, cada una con su etiqueta 802.1Q.

## Archivos

- `actividad7_topologia.py`: levanta la red, aplica las VLANs a los puertos de acceso y abre la
  consola `mininet>`.
- `actividad7_vlans.py`: prueba la matriz de conectividad completa y captura una trama en el
  trunk para mostrar la etiqueta de VLAN. Guarda todo en `actividad7_vlans_resultados.txt`.

Antes de empezar, actualizá el repositorio:

```bash
cd ~/itu-transmision-de-datos && git pull
cd actividad7
```

## Parte A · Paso a paso en la consola

```bash
sudo python3 actividad7_topologia.py
```

1. **Misma VLAN, distinto switch** (tiene que funcionar):
   ```text
   h1 ping -c 2 10.0.0.3
   ```
2. **Distinta VLAN, mismo switch** (NO tiene que funcionar, aunque estén en el mismo cable):
   ```text
   h1 ping -c 2 10.0.0.2
   ```
3. Mirá la configuración de un puerto de acceso y la del trunk:
   ```text
   sh ovs-vsctl list port s1-eth1 | grep tag
   sh ovs-vsctl list port s1-eth3 | grep tag
   ```
   El puerto de acceso tiene un `tag` puesto; el del trunk lo tiene vacío (`[]`): por eso deja
   pasar las dos VLANs.
4. **Capturá en el trunk** mientras hacés un ping entre VLANs iguales de distinto switch:
   ```text
   s1 tcpdump -e -n -i s1-eth3 icmp &
   h1 ping -c 2 10.0.0.3
   s1 kill %tcpdump
   ```
   Buscá la palabra `vlan` en la salida.

Salí con `exit`. Si algo queda trabado: `sudo mn -c`.

## Parte B · Comparación automática

```bash
sudo python3 actividad7_vlans.py
cat actividad7_vlans_resultados.txt
```

Prueba los 5 pares de hosts posibles (misma VLAN/distinta VLAN, mismo switch/distinto switch) y
guarda una captura del trunk (`trunk_vlan10.pcap`) para abrir en Wireshark.

## Preguntas para responder

1. Completá la matriz: ¿qué combinaciones de host funcionan y cuáles no? ¿Alcanza con mirar el
   switch de cada host para predecirlo, o hace falta mirar la VLAN?
2. h1 y h2 están conectados al **mismo switch físico**, con un cable cada uno. Aun así no se
   pueden pingear. ¿Qué parte del switch es la que decide que esas dos tramas no se mezclen?
3. En la captura del trunk, ¿qué campo de la trama Ethernet lleva el número de VLAN? ¿En qué
   posición va respecto de las direcciones MAC origen/destino? *(Repasá la estructura de la
   trama Ethernet de la Actividad 1 y compará.)*
4. Si capturás en el puerto de acceso de h1 (`h1-eth0`) en lugar del trunk, ¿vas a ver la
   etiqueta de VLAN? ¿Por qué el switch se la saca antes de entregarle la trama al host?
5. h1 manda un ping a 10.0.0.2 (h2) y no hay respuesta. Para h1, eso se ve exactamente igual
   que si h2 estuviera apagado. ¿Qué mensaje de error da el comando `ping`, y qué tiene que ver
   con el protocolo ARP que vimos antes? *(Pista: pensá qué pasa primero, ARP o ICMP.)*
6. ¿Qué pasaría si alguien, por error, configura el puerto `s1-eth3` (el trunk) con
   `tag=10`? ¿Qué tráfico dejaría de llegar a dónde?
7. En una red real, ¿qué ventaja práctica tiene separar por VLANs en vez de usar switches
   físicos distintos para cada grupo de hosts?

## Para profundizar (opcional)

- Agregá una quinta VLAN con un host nuevo en s1, sin agregar ningún host en s2: ¿hace falta
  tocar el puerto trunk para que funcione un ping entre dos hosts de esa VLAN que estén en el
  mismo switch?
- Investigá qué es la **VLAN nativa** de un trunk y qué pasa con una trama que llega sin
  etiqueta a un puerto trunk.
