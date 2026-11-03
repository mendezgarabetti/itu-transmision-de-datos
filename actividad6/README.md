# Actividad 6 · Bucles de capa 2: tormenta de difusión y STP

## Objetivo

Ver qué pasa cuando hay **más de un camino** entre dos switches (un bucle), por qué eso es un
problema grave en capa 2 (a diferencia de capa 3, donde el ruteo sabe evitar bucles), y cómo
el **Spanning Tree Protocol (STP)** lo resuelve bloqueando puertos de forma lógica sin tocar el
cableado físico.

## Topología

Tres switches conectados en **triángulo** (cada uno con los otros dos), cada uno con un host.
El enlace entre switches está limitado a 1 Mb/s a propósito: si se forma una tormenta sin
control, el límite evita que sature la VM, pero la diferencia sigue siendo enorme y se mide
igual.

```
      h1
       │
       s1
      /  \
   (1Mb)  (1Mb)
    /        \
  s2 ──(1Mb)── s3
  │             │
  h2            h3
```

## Archivos

- `actividad6_topologia.py`: levanta la red y abre la consola `mininet>`. Sin argumentos, STP
  está **desactivado** (el bucle queda sin control). Con `--stp`, lo activa.
- `actividad6_storm.py`: repite el experimento de forma automática (con y sin STP) y guarda un
  resumen en `actividad6_storm_resultados.txt`.

Antes de empezar, actualizá el repositorio:

```bash
cd ~/itu-transmision-de-datos && git pull
cd actividad6
```

## Parte A · Paso a paso en la consola

**Primero, sin STP** (el caso peligroso):

```bash
sudo python3 actividad6_topologia.py
```

1. Mirá los contadores de paquetes de los puertos de s1 **antes** de la tormenta (`rx pkts`
   tiene que estar en 0 o muy cerca):
   ```text
   sh ovs-ofctl dump-ports s1
   ```
2. Mandá **un solo** paquete de difusión (broadcast):
   ```text
   h1 ping -b -c 1 -W 1 10.0.0.255
   ```
3. Esperá 2-3 segundos y volvé a mirar los mismos contadores:
   ```text
   sh ovs-ofctl dump-ports s1
   ```
   Deberías ver varios miles de paquetes más, de un solo ping.
4. **Cortá el bucle** para frenar la tormenta y salí:
   ```text
   sh link s1 s2 down
   exit
   ```
5. **Un ping común tampoco se salva.** Volvé a levantar la topología sin STP y probá un ping
   normal entre h1 y h2, mirando los contadores antes y después:
   ```bash
   sudo mn -c
   sudo python3 actividad6_topologia.py
   ```
   ```text
   sh ovs-ofctl dump-ports s1
   h1 ping -c 2 h2
   sh ovs-ofctl dump-ports s1
   sh link s1 s2 down
   exit
   ```
   ¿Respondió h2? ¿Qué pasó con los contadores?

Si algo queda trabado: `sudo mn -c`.

**Ahora, con STP activado:**

```bash
sudo python3 actividad6_topologia.py --stp
```

6. Esperá **unos 35 segundos** sin hacer nada (STP necesita ese tiempo para converger: pasa por
   los estados *listening*, *learning* y *forwarding* en cada puerto).
7. Mirá el estado de los seis puertos entre switches (`-eth2` y `-eth3` de cada switch; el
   `-eth1` es el del host):
   ```text
   sh for p in s1-eth2 s1-eth3 s2-eth2 s2-eth3 s3-eth2 s3-eth3; do echo $p $(ovs-vsctl get port $p status:stp_state); done
   ```
   Uno de los seis va a estar en `blocking`: ese puerto sigue cableado, pero STP decidió no
   usarlo para que no haya bucle. Cuál de los seis queda bloqueado puede cambiar cada vez que
   levantás la red: depende de qué switch STP elija como raíz.
8. Repetí el mismo broadcast de antes y el ping común del paso 5:
   ```text
   h1 ping -b -c 1 -W 1 10.0.0.255
   sh ovs-ofctl dump-ports s1
   h1 ping -c 2 h2
   ```
   Esta vez el contador casi no se mueve y h2 responde.

Salí con `exit`. Si algo queda trabado: `sudo mn -c`.

## Parte B · Comparación automática

```bash
sudo python3 actividad6_storm.py
cat actividad6_storm_resultados.txt
```

Tarda alrededor de un minuto (incluye la espera de convergencia de STP). Repite el mismo
experimento —un solo broadcast, medir paquetes durante 3 segundos— primero sin STP y después
con STP, y guarda la comparación.

## Preguntas para responder

1. En tus resultados, ¿cuántos paquetes circularon en 3 segundos **sin** STP? ¿Y **con** STP?
   ¿Qué tan grande es la diferencia?
2. Un solo paquete de difusión generó miles de copias. ¿Por qué un switch nunca se da cuenta de
   que está reenviando una copia de algo que él mismo ya mandó? *(Pista: pensá en qué
   información lleva una trama Ethernet y qué le falta comparado con un paquete IP.)*
3. En el paso 5, un ping común entre h1 y h2 no tuvo respuesta y disparó la tormenta, aunque el
   ping viaja en tramas unicast. ¿Qué trama manda h1 **antes** del primer Echo Request, y por qué
   esa sí entra en el bucle? *(Pista: revisá la Actividad 1.)*
4. En el paso 7, un puerto queda en `blocking`. ¿Ese puerto deja de recibir tramas por completo,
   o solo deja de *reenviarlas* para evitar el bucle? *(Pista: STP necesita seguir escuchando
   ese puerto para darse cuenta si el enlace que está usando se corta.)*
5. Si el enlace que **sí** está en uso (uno de los que quedó en `forwarding`) se corta, ¿qué
   tendría que hacer STP? ¿Por qué eso tarda unos segundos en lugar de ser instantáneo?
6. Esta actividad usa un triángulo de **switches**. ¿Por qué un bucle entre **routers** (capa 3)
   no causa el mismo problema? *(Pista: pensá en el campo TTL de la cabecera IP, visto en la
   Actividad 1, y en si Ethernet tiene algo parecido.)*
7. En una red real, ¿por qué alguien cablearía intencionalmente un enlace redundante entre dos
   switches si STP lo va a dejar bloqueado la mayor parte del tiempo?

## Para profundizar (opcional)

- Con la topología sin STP todavía corriendo, probá cortar el bucle a mano en lugar de activar
  STP: `sh link s1 s2 down`. Repetí el broadcast: ¿la tormenta vuelve a aparecer? ¿Qué perdiste
  al cortar ese enlace a mano, comparado con dejar que STP lo bloquee solo?
- Investigá qué es **RSTP** (*Rapid* STP) y por qué existe: ¿qué problema de STP clásico
  resuelve?
