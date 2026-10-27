# Actividad 3 · Tablas MAC: cómo aprende un switch

## Objetivo

Observar cómo un switch Ethernet construye su **tabla de direcciones MAC** (también llamada
tabla CAM o FDB), cuándo **inunda** una trama y cuándo la reenvía por un solo puerto, y qué pasa
cuando las entradas **envejecen**.

## Topología

Dos switches conectados entre sí, cada uno con dos hosts. Los switches funcionan **sin
controlador** (modo *standalone*): se comportan como switches Ethernet clásicos que aprenden
solos.

```
  h1 ──(1)┐                 ┌(1)── h3
          s1 (3)───────(3) s2
  h2 ──(2)┘                 └(2)── h4
```

| Host | IP | MAC | Switch y puerto |
| :-: | :-: | :-: | :-: |
| h1 | 10.0.0.1 | 00:00:00:00:00:01 | s1, puerto 1 |
| h2 | 10.0.0.2 | 00:00:00:00:00:02 | s1, puerto 2 |
| h3 | 10.0.0.3 | 00:00:00:00:00:03 | s2, puerto 1 |
| h4 | 10.0.0.4 | 00:00:00:00:00:04 | s2, puerto 2 |

El puerto 3 de cada switch es el enlace entre s1 y s2.

## Archivos

- `actividad3_topologia.py`: levanta la red y abre la consola `mininet>` para trabajar en clase.
- `actividad3_tablas_mac.py`: recorre todos los pasos de forma automática, muestra las tablas
  y guarda el resultado en `actividad3_tablas_mac_resultados.txt`.

Antes de empezar, actualizá el repositorio:

```bash
cd ~/itu-transmision-de-datos && git pull
cd actividad3
```

## Comandos clave

| Comando (dentro de `mininet>`) | Qué hace |
| :--- | :--- |
| `sh ovs-appctl fdb/show s1` | Muestra la tabla MAC de s1: puerto, VLAN, MAC y antigüedad en segundos |
| `sh ovs-appctl fdb/flush s1` | Vacía la tabla MAC de s1 |
| `sh ovs-vsctl set bridge s1 other_config:mac-aging-time=20` | Cambia el tiempo de envejecimiento (por defecto 300 s) |

Fuera de Mininet, desde otra terminal de la VM, son los mismos comandos con `sudo` y sin `sh`.

## Parte A · Paso a paso en la consola

```bash
sudo python3 actividad3_topologia.py
```

1. **Tablas vacías.** Mirá las tablas de s1 y s2 recién encendidos.
   ```text
   sh ovs-appctl fdb/show s1
   sh ovs-appctl fdb/show s2
   ```
2. **Primer ping.** Ejecutá `h1 ping -c 1 h2` y volvé a mirar **las dos** tablas.
3. **Ping entre switches.** Ejecutá `h1 ping -c 1 h4` y mirá las tablas otra vez.
4. **Todos con todos.** Ejecutá `pingall` y mirá las tablas completas.
5. **Envejecimiento.** Bajá el tiempo de envejecimiento de s1 a 20 segundos, hacé `pingall`,
   esperá unos 40 segundos sin generar tráfico y mirá la tabla de s1.

Salí con `exit`. Si algo queda trabado: `sudo mn -c`.

## Parte B · Experimento automático

```bash
sudo python3 actividad3_tablas_mac.py
```

El script repite los pasos anteriores y agrega un experimento: pone a **h3 a escuchar** mientras
h1 le hace ping a h2, primero con las tablas completas y después con las tablas recién vaciadas.
Tarda menos de un minuto (incluye una espera para ver el envejecimiento).

```bash
cat actividad3_tablas_mac_resultados.txt
```

## Preguntas para responder

1. Después del primer `h1 ping h2`, **s2 ya tiene una entrada** aunque el tráfico era entre dos
   hosts de s1. ¿Qué MAC aprendió, por qué puerto y qué trama la llevó hasta s2?
   *(Pista: ¿cuál es el primer paquete de un ping? Revisá la Actividad 1.)*
2. ¿Por qué s2 **no** aprendió la MAC de h2 en ese mismo paso?
3. Con las tablas completas, ¿por qué en s1 hay **dos MACs en el puerto 3**? ¿Puede un mismo
   puerto tener muchas MACs? ¿Cuándo pasa en una red real?
4. En la Parte B, con las tablas completas h3 no ve nada del tráfico entre h1 y h2, pero con las
   tablas vaciadas recibe **un** Echo Request. ¿Por qué uno solo y no los tres?
5. Si h1 y h2 ya se conocían (su caché ARP estaba completa), ¿por qué el switch igual inundó una
   trama? ¿Qué diferencia hay entre inundar un **broadcast** y una **unicast desconocida**?
6. ¿Para qué sirve que las entradas envejezcan? ¿Qué problema aparecería si h4 se desconecta de
   s2 y se conecta a s1, y la tabla nunca se borrara?
7. Compará con un **hub**: ¿qué habría visto h3 en la Parte B si en lugar de switches hubiera hubs?

## Para profundizar (opcional)

> `dpctl/del-flows` borra el caché de flujos que Open vSwitch mantiene en el kernel. Sin ese
> paso, los primeros paquetes después del `fdb/flush` pueden seguir saliendo por el puerto que
> el switch ya conocía y el resultado cambia de una vez a otra.

- En la consola, dejá a h3 capturando y repetí el experimento a mano:
  ```text
  h3 tcpdump -n -i h3-eth0 icmp &
  sh ovs-appctl fdb/flush s1
  sh ovs-appctl fdb/flush s2
  sh ovs-appctl dpctl/del-flows
  h1 ping -c 3 h2
  ```
- Abrí una captura de h3 en Wireshark y verificá la MAC de destino de la trama que llegó.
