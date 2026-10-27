# Actividad 5 · Control de errores: bits invertidos y retransmisión

## Objetivo

Simular **errores de transmisión reales** (no pérdida: un bit que se invierte en el camino,
como puede pasar por ruido en el medio físico) y ver cómo TCP los detecta y se recupera
retransmitiendo, a costa del ancho de banda efectivo.

## Topología

Dos hosts y un switch, igual que en la Actividad 4. El enlace de `h1` tiene una velocidad fija
(10 Mb/s) y un porcentaje configurable de tramas con **un bit invertido al azar** (parámetro
`--corrupt` de `netem`, distinto de `loss`: la trama llega, pero con el *checksum* inválido).

```
h1 ──── s1 ──── h2
10.0.0.1       10.0.0.2
(enlace de h1 con % de error configurable)
```

## Archivos

- `actividad5_topologia.py`: levanta la red y abre la consola `mininet>`. Acepta
  `--corrupt <porcentaje>` (por defecto 5; 0 = sin errores).
- `actividad5_errores.py`: repite una transferencia TCP de 2 MB con 0%, 5% y 15% de error,
  captura cada una y guarda un resumen con paquetes, retransmisiones y velocidad en
  `actividad5_errores_resultados.txt`.

Antes de empezar, actualizá el repositorio:

```bash
cd ~/itu-transmision-de-datos && git pull
cd actividad5
```

## Parte A · Paso a paso en la consola

```bash
sudo python3 actividad5_topologia.py --corrupt 10
```

1. **Sin mirar nada todavía**, lanzá el servidor y una transferencia:
   ```text
   h2 iperf -s > /dev/null 2>&1 &
   h1 iperf -c 10.0.0.2 -n 2M
   ```
   Anotá la velocidad final (línea `Mbits/sec`).
2. Repetí la topología con `--corrupt 0` (sin errores) y compará la velocidad.
3. **Ahora con captura**, para ver los errores de cerca:
   ```text
   h1 tcpdump -n -i h1-eth0 -w con_error.pcap tcp &
   h1 iperf -c 10.0.0.2 -n 2M
   h1 kill %tcpdump
   ```

Salí con `exit`. Si algo queda trabado: `sudo mn -c`.

## Parte B · Comparación automática

```bash
sudo python3 actividad5_errores.py
cat actividad5_errores_resultados.txt
```

Genera `sin_errores.pcap`, `con_errores_5.pcap` y `con_errores_15.pcap`. Abrilos con Wireshark.
Para encontrar las retransmisiones rápido: **Analyze → Expert Information**, o el filtro
`tcp.analysis.retransmission`.

## Preguntas para responder

1. Completá una tabla con el porcentaje de error, la velocidad medida y la cantidad de
   retransmisiones. ¿Qué relación ves entre las tres columnas?
2. Abrí `con_errores_15.pcap` y buscá una trama marcada como `[TCP Retransmission]`. ¿Qué número
   de secuencia (`seq`) tiene? Buscá la trama anterior con el mismo `seq`: ¿cuánto tiempo pasó
   entre una y otra?
3. **Esto es distinto de la pérdida de la Actividad 2.** Ahí el paquete nunca llegaba; acá
   *netem* lo entrega igual, pero con un bit cambiado. ¿Quién nota el error primero: el enlace,
   la placa de red, o TCP? *(Pista: el checksum de la cabecera TCP se calculó antes de que el
   bit se invirtiera.)*
4. ¿Cómo se entera el emisor de que tiene que retransmitir si el receptor **ni siquiera pudo
   leer** qué segmento era el que llegó mal? *(Pista: pensá en lo que el receptor sí pudo seguir
   mandando: sus ACKs del último dato bueno que tiene.)*
5. En los resultados automáticos, ¿el número de retransmisiones sube siempre con el
   porcentaje de error? Si no, ¿por qué? *(Pista: con mucho error, TCP reduce agresivamente
   la ventana de envío — manda menos datos por vez, así que hay menos para retransmitir
   aunque la proporción de error sea mayor.)*
6. Esta actividad simula errores de bit en el medio de transmisión. ¿Qué parte del programa de
   la materia estudia **por qué** ocurren esos errores (ruido, atenuación, interferencia) antes
   de que lleguen a esta capa?
