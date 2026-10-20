# Actividad 2 · Enlaces, ancho de banda, latencia y pérdida

## Objetivo

Armar una red más grande, **sin router** todavía (una sola subred), con enlaces de distintas
velocidades, y medir con `iperf` y `ping`:

- el **ancho de banda** que realmente se obtiene en cada enlace;
- la **latencia** (RTT), con la red tranquila y con la red cargada;
- la **pérdida de paquetes** cuando se envía más de lo que el enlace soporta.

## Topología

Un switch central `s0` y cinco segmentos, cada uno con su switch y dos hosts. Todos los enlaces de
un segmento tienen la misma velocidad, incluido el que lo une con `s0`. Todos los hosts están en
`10.0.0.0/24`.

```
                          s0 (central)
        ┌──────────┬──────────┼──────────┬──────────┐
       s1         s2         s3         s4         s5
     1 Mb/s     10 Mb/s   100 Mb/s    1 Gb/s    10 Gb/s
     h11 h12    h21 h22    h31 h32    h41 h42    h51 h52
```

| Segmento | Velocidad | Hosts | IPs |
| :-: | :-: | :-: | :-: |
| 1 | 1 Mb/s | h11, h12 | 10.0.0.11, 10.0.0.12 |
| 2 | 10 Mb/s | h21, h22 | 10.0.0.21, 10.0.0.22 |
| 3 | 100 Mb/s | h31, h32 | 10.0.0.31, 10.0.0.32 |
| 4 | 1 Gb/s | h41, h42 | 10.0.0.41, 10.0.0.42 |
| 5 | 10 Gb/s | h51, h52 | 10.0.0.51, 10.0.0.52 |

Cada enlace tiene además **1 ms de retardo** (se puede cambiar, ver más abajo).

> **Bits y bytes.** Las velocidades de red se expresan en **bits** por segundo:
> 1 Mb/s = 1 megabit por segundo = 125 kilobytes por segundo. Un enlace de 1 Gb/s descarga
> como máximo 125 MB (megabytes) por segundo. `iperf` informa en Mbits/sec.

## Archivos

- `actividad2_topologia.py`: levanta la red y abre la consola `mininet>`.
- `actividad2_mediciones.py`: hace todas las mediciones de forma automática y guarda una tabla en
  `actividad2_mediciones_resultados.txt` (tarda unos 3 minutos).

Ambos aceptan opciones para cambiar el retardo y la pérdida de **todos** los enlaces:

```bash
sudo python3 actividad2_topologia.py                # 1 ms de retardo, sin pérdida
sudo python3 actividad2_topologia.py --delay 20ms   # enlaces "lejanos"
sudo python3 actividad2_topologia.py --loss 2       # 2 % de pérdida en cada enlace
```

Antes de empezar, actualizá el repositorio:

```bash
cd ~/itu-transmision-de-datos && git pull
cd actividad2
```

## Herramientas

| Comando (dentro de `mininet>`) | Qué mide |
| :--- | :--- |
| `h11 ping -c 10 h12` | Latencia (RTT) y pérdida de paquetes ICMP |
| `iperf h31 h32` | Ancho de banda con **TCP**: lo máximo que el enlace deja pasar |
| `iperfudp 150M h31 h32` | Envía **UDP** a una tasa fija (150 Mb/s) y muestra cuánto llegó |
| `h32 iperf -s -u &` y `h31 iperf -c 10.0.0.32 -u -b 150M` | Igual que el anterior, pero muestra **jitter y pérdida** |

TCP se adapta: si el enlace se satura, baja la velocidad y retransmite. UDP no: envía a la tasa
pedida y, si el enlace no da abasto, **los paquetes que sobran se pierden**.

## Parte A · Mediciones en la consola

```bash
sudo python3 actividad2_topologia.py
```

1. **Latencia.** Medí el RTT dentro de un segmento (`h11 ping -c 10 h12`) y entre segmentos
   (`h11 ping -c 10 h52`). ¿Cuántos enlaces atraviesa cada uno?
2. **Ancho de banda TCP.** Medí con `iperf` cada segmento: `iperf h11 h12`, `iperf h21 h22`,
   `iperf h31 h32`, `iperf h41 h42`, `iperf h51 h52`. Anotá los resultados en una tabla.
3. **Cuello de botella.** Medí `iperf h11 h52` e `iperf h31 h41`. ¿Qué enlace manda?
4. **Pérdida con UDP.** En el segmento de 10 Mb/s, enviá UDP por debajo y por encima de su
   capacidad, y mirá la línea *Server Report* (jitter y pérdida):
   ```text
   h22 iperf -s -u &
   h21 iperf -c 10.0.0.22 -u -b 5M
   h21 iperf -c 10.0.0.22 -u -b 15M
   ```
5. **Latencia con carga.** En el segmento de 1 Mb/s, lanzá una transferencia larga y medí el
   ping mientras tanto:
   ```text
   h12 iperf -s &
   h11 iperf -c 10.0.0.12 -t 20 &
   h11 ping -c 10 h12
   ```

Salí con `exit`. Si algo queda trabado: `sudo mn -c`.

## Parte B · Mediciones automáticas

```bash
sudo python3 actividad2_mediciones.py
cat actividad2_mediciones_resultados.txt
```

Después repetilo con pérdida en los enlaces y compará las dos tablas:

```bash
sudo python3 actividad2_mediciones.py --loss 1
```

> Los números exactos dependen de la computadora donde corre la VM, sobre todo en los segmentos
> de 1 y 10 Gb/s: ahí el límite puede ser la CPU y no el enlace.

## Preguntas para responder

**Ancho de banda**

1. Completá una tabla con la velocidad configurada y la medida con TCP en cada segmento. ¿Por qué
   TCP nunca llega exactamente al 100 % de la velocidad del enlace?
2. ¿En el segmento de 10 Gb/s obtuviste 10 Gb/s? Si no, ¿qué lo limitó? *(Pista: emisor,
   receptor y switches corren en la misma VM, que tiene un solo procesador.)*
3. Entre `h11` y `h52`, ¿qué velocidad se obtiene? ¿Qué es un **cuello de botella**?

**Pérdida**

4. Con UDP al 50 % de la capacidad, ¿hubo pérdida? ¿Y al 150 %? Enviando 15 Mb/s por un enlace
   de 10 Mb/s, ¿qué porcentaje esperabas perder? ¿Coincide con lo medido?
5. En la tabla automática, el segmento de 1 Mb/s **no pierde nada** aunque recibe UDP al 150 %
   durante 5 segundos. ¿Dónde quedaron los paquetes que sobraban? Repetí la prueba durante 30
   segundos y mirá el informe del servidor (el cliente no lo recibe: queda atrás de la cola):
   ```text
   h12 iperf -s -u > /tmp/udp.txt &
   h11 iperf -c 10.0.0.12 -u -b 1500K -t 30
   h11 sleep 15
   h12 cat /tmp/udp.txt
   ```
   ¿Qué cambia? ¿Por qué el informe dice que la transferencia duró más de 30 segundos?
6. En los segmentos de 1 y 10 Gb/s, ¿la pérdida de UDP se debe al enlace o a otra cosa? Mirá
   cuánto pudo **enviar** el emisor.

**Latencia**

7. ¿Por qué el RTT dentro de un segmento es de unos 4 ms si cada enlace tiene 1 ms de retardo?
   ¿Cuánto da entre `h11` y `h52` y por qué?
8. En el segmento de 1 Mb/s, ¿cuánto aumentó el RTT durante la descarga? ¿Dónde esperan los
   paquetes del ping? *(Este fenómeno se conoce como* bufferbloat*.)*

**Pérdida en los enlaces**

9. Compará la tabla normal con la de `--loss 1`. ¿En qué segmentos cae más el rendimiento de TCP?
   ¿Por qué una pérdida del 1 % casi no afecta al enlace de 1 Mb/s y hunde al de 1 Gb/s?
10. ¿Por qué esa misma pérdida apenas se nota en un `ping`?
