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

1. Un ping normal (unicast) funciona sin problema, porque nunca entra en el bucle:
   ```text
   h1 ping -c 2 h2
   ```
2. Mirá el contador de paquetes de un puerto de s1 **antes** de la tormenta:
   ```text
   sh ovs-ofctl dump-ports s1
   ```
3. Mandá **un solo** paquete de difusión (broadcast):
   ```text
   h1 ping -b -c 1 -W 1 10.0.0.255
   ```
4. Esperá 2-3 segundos y volvé a mirar el mismo contador:
   ```text
   sh ovs-ofctl dump-ports s1
   ```
   Deberías ver varios miles de paquetes más, de un solo ping.
5. **Cortá el bucle** para frenar la tormenta antes de seguir:
   ```text
   sh link s1 s2 down
   ```

Salí con `exit`. Si algo queda trabado: `sudo mn -c`.

**Ahora, con STP activado:**

```bash
sudo python3 actividad6_topologia.py --stp
```

6. Esperá **unos 35 segundos** sin hacer nada (STP necesita ese tiempo para converger: pasa por
   los estados *listening*, *learning* y *forwarding* en cada puerto).
7. Mirá el estado de los puertos entre switches:
   ```text
   sh ovs-vsctl get port s1-eth2 status:stp_state
   sh ovs-vsctl get port s2-eth2 status:stp_state
   sh ovs-vsctl get port s3-eth2 status:stp_state
   ```
   Uno de ellos va a estar en `blocking`: ese puerto sigue cableado, pero STP decidió no usarlo
   para que no haya bucle.
8. Repetí el mismo broadcast de antes:
   ```text
   h1 ping -b -c 1 -W 1 10.0.0.255
   sh ovs-ofctl dump-ports s1
   ```
   Esta vez el contador casi no se mueve.

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
3. ¿Por qué un **unicast** entre h1 y h2 (paso 1) no entra en la tormenta, pero un **broadcast**
   sí?
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
