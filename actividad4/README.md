# Actividad 4 · Establecimiento y liberación de una conexión TCP

## Objetivo

Ver en Wireshark el **saludo de tres vías** (*three-way handshake*) con el que arranca toda
conexión TCP, dos formas distintas de terminarla (prolija con `FIN` y abrupta con `RST`), y
contrastarlo con un datagrama UDP, que no negocia nada antes de mandar datos.

## Topología

Dos hosts y un switch, como en la Actividad 1.

```
h1 ──── s1 ──── h2
(cliente)      (servidor)
10.0.0.1       10.0.0.2
```

## Archivos

- `actividad4_topologia.py`: levanta la red y abre la consola `mininet>`.
- `tcp_echo_server.py`: servidor TCP simple — acepta una conexión, devuelve lo que recibe y
  cierra. Se usa como `python3 tcp_echo_server.py <puerto>`.
- `tcp_client.py`: cliente TCP — conecta, manda un mensaje, espera la respuesta y cierra.
  Con `--rst` cierra de forma abrupta (manda `RST` en vez de `FIN`) y no espera respuesta.
  Uso: `python3 tcp_client.py <ip> <puerto> [mensaje] [--rst]`.
- `udp_send.py`: manda **un** datagrama UDP y listo, sin esperar nada.
  Uso: `python3 udp_send.py <ip> <puerto> [mensaje]`.
- `actividad4_handshake.py`: arma las tres capturas automáticamente y guarda un resumen en
  `actividad4_handshake_resultados.txt`.

Antes de empezar, actualizá el repositorio:

```bash
cd ~/itu-transmision-de-datos && git pull
cd actividad4
```

## Parte A · Paso a paso en la consola

```bash
sudo python3 actividad4_topologia.py
```

1. **Servidor arriba.**
   ```text
   h2 python3 tcp_echo_server.py 5000 &
   ```
2. **Capturá en el cliente** (antes de conectar, para no perderte el handshake):
   ```text
   h1 tcpdump -n -i h1-eth0 -w normal.pcap tcp port 5000 &
   ```
3. **Conectá y cerrá prolijo:**
   ```text
   h1 python3 tcp_client.py 10.0.0.2 5000 hola
   h1 kill %tcpdump
   h1 tcpdump -n -r normal.pcap
   ```
4. **Repetí con cierre abrupto**, en una captura nueva:
   ```text
   h1 tcpdump -n -i h1-eth0 -w rst.pcap tcp port 5000 &
   h1 python3 tcp_client.py 10.0.0.2 5000 hola --rst
   h1 kill %tcpdump
   h1 tcpdump -n -r rst.pcap
   ```
5. **Un datagrama UDP, para comparar:**
   ```text
   h1 tcpdump -n -i h1-eth0 -w udp.pcap udp port 5000 &
   h1 python3 udp_send.py 10.0.0.2 5000 hola
   h1 kill %tcpdump
   h1 tcpdump -n -r udp.pcap
   ```

Salí con `exit`. Si algo queda trabado: `sudo mn -c`.

## Parte B · Capturas automáticas

```bash
sudo python3 actividad4_handshake.py
cat actividad4_handshake_resultados.txt
```

Genera `tcp_normal.pcap`, `tcp_rst.pcap` y `udp_demo.pcap`. Abrilos con Wireshark (`wireshark-gtk
tcp_normal.pcap`, ver troubleshooting en el README de la Actividad 1 si hace falta) para ver los
**flags** de cada trama (columna *Flags* o filtro `tcp.flags`).

## Preguntas para responder

**Conexión normal (`tcp_normal.pcap`)**

1. Identificá las tres tramas del *three-way handshake*: ¿qué flags tiene cada una (`SYN`,
   `SYN, ACK`, `ACK`)? ¿Quién las manda?
2. ¿En qué trama va el mensaje `hola`? ¿Y la respuesta del servidor?
3. El cierre normal necesita **cuatro** tramas (`FIN`+`ACK` de cada lado). Identificalas: ¿quién
   cierra primero, el cliente o el servidor? *(Pista: mirá quién llama a `close()` primero en el
   código.)*

**Cierre abrupto (`tcp_rst.pcap`)**

4. Comparado con el normal, ¿qué cambia al final de la conexión? ¿Cuántas tramas tiene el cierre
   acá?
5. ¿Qué diferencia práctica hay entre terminar una conexión con `FIN` y con `RST`? ¿Cuándo
   aparece un `RST` en una red real (más allá de este ejemplo a propósito)?

**UDP (`udp_demo.pcap`)**

6. ¿Cuántas tramas hay en esta captura? ¿Hubo algún intercambio antes de mandar los datos?
7. Si ese datagrama se hubiera perdido en el camino, ¿quién se entera? Compará con qué pasaría
   si se perdiera la trama 1 (`SYN`) de la conexión TCP.

**En general**

8. ¿Por qué un protocolo necesita "saludar" antes de mandar datos? ¿Qué información se
   intercambian las partes en el `SYN`/`SYN, ACK` que no está en un simple datagrama UDP?
   *(Pista: mirá los números de secuencia (`seq`) de cada trama.)*
