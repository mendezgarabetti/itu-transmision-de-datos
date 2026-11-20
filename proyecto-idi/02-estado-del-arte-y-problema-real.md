# 1. Estado del Arte y Problema Real

Cuando se retoma un proyecto previo para mejorarlo, el error más común es pensar que "mejorar" equivale a **agregar cosas**: sumar tres sensores más a la misma placa, poner una pantalla más grande o cambiar de librería sin cambiar qué problema se resuelve.

En **Transmisión de Datos**, la evolución del proyecto debe nacer de una pregunta de ingeniería:

> **¿En qué problema concreto del mundo real este prototipo —tal como estaba— fallaría o se quedaría corto, qué existe hoy en el mercado y en la literatura para resolverlo, y cómo nuestra arquitectura de comunicación de datos aporta una mejora real?**

---

## Complejidad Artificial vs. Mejora con Impacto Real

| Eje | ❌ Complejidad artificial (Lo que NO buscamos) | ✅ Mejora orientada a un problema real (Lo que SÍ buscamos) |
|---|---|---|
| **Hardware y Nodos** | "Le agregamos 4 sensores más (luz, sonido, humedad y ultrasonido) al mismo ESP8266 para que el proyecto parezca más complejo." | "Mantenemos la variable crítica (ej. temperatura/humedad en cultivo o cámara frigorífica), pero distribuimos 2 o más nodos en puntos distintos porque un único punto de medición no representa lo que ocurre en un recinto o terreno real." |
| **Transmisión de Datos** | "Cambiamos de HTTP a MQTT sólo para usar otra librería, pero todo sigue ocurriendo en la misma mesa sin restricciones reales." | "En una finca o galpón no hay Wi-Fi en todos lados o el consumo agota la batería en horas. Por eso los nodos de campo transmiten tramas compactas por **ESP-NOW** hacia un nodo concentrador (**Gateway**), que recién ahí publica por **MQTT** y gestiona *timeouts* si se cae el enlace." |
| **Aporte / Innovación** | "Le pusimos un buzzer y más gráficos en pantalla." | "Las soluciones comerciales relevadas cuestan más de USD 500 y dependen de nubes cerradas pagas. Nuestra propuesta logra telemetría distribuida de bajo costo (< USD 25) con tecnologías abiertas y detección activa de caída de nodos." |

---

## ¿Qué es el "Estado del Arte" y por qué investigamos antes de programar?

En ingeniería e I+D+i, investigar el **Estado del Arte (o Estado de la Técnica)** significa responder con rigor: 
* *«¿Qué hicieron ya los mejores del mercado o de la comunidad técnica para resolver este mismo problema, y cuáles son sus límites?»*

Si no investigás antes de diseñar, corrés el riesgo de pasar semanas desarrollando algo que ya existe resuelto por dos dólares, o peor aún, tropezar con problemas técnicos que la industria ya superó hace años.

### 🔎 ¿Dónde y cómo buscar fuentes confiables?

No te limites a la primera página de Google ni le pidas a una IA que te invente un resumen genérico. Buscá en fuentes primarias de ingeniería:

1. **Soluciones Comerciales de Mercado:**
   * Buscá fabricantes, integradores y distribuidores de hardware IoT, telemetría o automatización industrial.
   * Analizá las fichas técnicas (*datasheets*), manuales de usuario y precios de venta al público.
2. **Proyectos Open Source y de la Comunidad:**
   * Buscá en **GitHub**, **Hackaday**, **Instructables** o foros técnicos de electrónica abierta usando palabras clave específicas en inglés y español (ej: *"ESP8266 low power datalogger"*, *"cold chain monitoring open hardware"*, *"ESP-NOW sensor network"*).
3. **Literatura Científica y Académica:**
   * **Google Scholar**, repositorios universitarios (**SEDICI**, **BDigital UNCuyo**) o actas de congresos argentinos de ciencias de la computación e informática (**CACIC**, **CONAIISI**, **WICC**, **JAIIO**).
   * Prestá atención a la sección *Metodología* y *Arquitectura de Red* de los artículos: allí se explica qué protocolos usaron y qué limitaciones encontraron.

---

## La Matriz Comparativa del Estado del Arte

Para que la investigación no quede en prosa dispersa, cada equipo debe sintetizar su relevamiento en una **tabla comparativa obligatoria**.

Deben relevar al menos:
* **2 Soluciones Comerciales** (productos cerrados que hoy compra una empresa o productor).
* **2 Proyectos Abiertos o Comunitarios** (desarrollos open source o académicos documentados).
* **Su Propuesta de Proyecto** (para contrastar en qué se diferencia).

### 📋 Ejemplo de Matriz Comparativa Resuelta:

| Solución / Producto | Tipo | Protocolo / Transmisión | Costo Aprox. | Dependencia de Infraestructura | Principal Limitación / Cuello de Botella |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Estación Comercial Marca A** | Comercial cerrada | Wi-Fi / Conexión a Nube propietaria | Alto (> USD 350) | Requiere Internet continuo y suscripción mensual en la nube | Si se corta Internet o la luz, deja de transmitir. Hardware cerrado imposible de auditar o reparar localmente. |
| **Datalogger Industrial Marca B** | Comercial cerrada | Almacenamiento en Tarjeta SD (sin red) | Medio (~ USD 90) | Ninguna (no tiene enlace inalámbrico) | No emite alertas en tiempo real; exige que un operario vaya físicamente a retirar la tarjeta de memoria. |
| **Proyecto Comunitario en GitHub (Repo C)** | Open Source | Wi-Fi estándar con HTTP POST | Bajo (~ USD 15) | Requiere router Wi-Fi dedicado y servidor encendido | Alto consumo de batería: la negociación TCP/HTTP demora más de 2 segundos, agotando pilas en pocos días. |
| **Proyecto en Foro Maker (Guía D)** | Open Source | Bluetooth BLE punto a punto | Bajo (~ USD 12) | Requiere un teléfono celular cerca | Alcance limitado (< 15 metros); inviable para monitoreo continuo o desatendido en galpón o campo. |
| **Nuestra Propuesta (Proyecto I+D+i)** | **Abierto / I+D+i** | **ESP-NOW punto a multipunto + Gateway MQTT local** | **Bajo (~ USD 20)** | **Red local autónoma (opera 100% sin conexión a Internet)** | **Optimizado para batería con tramas binarias de < 15 ms, buffer local ante fallas y detección de timeout.** |

---

## Los 5 Vectores de Innovación (El Valor Diferencial)

¿Por qué tiene sentido que desarrollen su propuesta frente a lo que ya existe? Deben justificar su aporte a través de los **5 vectores de innovación**, demostrando en cuáles de ellos su proyecto marca una diferencia:

### 1. ¿Es más barato? (Democratización de costos)
* ❌ **Mal justificado:** *"Es más barato porque compramos componentes chinos en Once o MercadoLibre."*
* ✅ **Bien justificado:** *"Las soluciones comerciales del sector oscilan entre USD 200 y USD 400 debido a licencias de software privativo y carcasas selladas. Nuestra propuesta utiliza microcontroladores de bajo costo con una lista de materiales (BOM) menor a USD 25, permitiendo que pequeños productores o talleres accedan a telemetría en tiempo real sin barreras de entrada económicas."*

### 2. ¿Es más rápido / eficiente? (Optimización de recursos y batería)
* ❌ **Mal justificado:** *"El ESP8266 o ESP32 procesa muy rápido los datos."*
* ✅ **Bien justificado:** *"Reemplazamos el stack TCP/IP y HTTP por comunicación liviana con ESP-NOW. Al eliminar el handshake de conexión de red, el nodo sensor pasa de estar encendido 2.500 ms a solo 12 ms por reporte, lo que permite alimentar el nodo con una celda Li-Ion 18650 durante más de 6 meses en modo Deep Sleep."*

### 3. ¿Es mejor / más robusto? (Adecuación al entorno real)
* ❌ **Mal justificado:** *"Es mejor porque el código está bien ordenado y tiene interfaz bonita."*
* ✅ **Bien justificado:** *"A diferencia de las soluciones comerciales que dependen de conectividad 4G o Wi-Fi con salida a Internet (que en galpones rurales o cámaras frigoríficas es nula o inestable), nuestro sistema opera sobre una red local independiente, almacenando las lecturas en memoria Flash si el receptor no acusa recibo (ACK)."*

### 4. ¿A mayor escala? (Escalabilidad de la red)
* ❌ **Mal justificado:** *"Se pueden conectar muchos sensores."*
* ✅ **Bien justificado:** *"El protocolo de transmisión adoptado admite hasta 20 nodos periféricos reportando a un concentrador central sin requerir reconfiguración de direccionamiento IP ni saturar la tabla DHCP de un router."*

### 5. ¿Código Abierto / Hardware Libre? (Soberanía tecnológica)
* ❌ **Mal justificado:** *"Usamos librerías libres de Arduino."*
* ✅ **Bien justificado:** *"El diseño completo del firmware y el esquemático de interconexión se publican bajo licencias abiertas (GPL / CERN OHL), garantizando que el usuario final no quede cautivo de un proveedor que discontinúe el servicio (vendor lock-in) y pueda mantener el sistema con repuestos de plaza."*

---

## Casos Reales de Referencia Regional

Estos cuatro escenarios reales —documentados en congresos argentinos (**CACIC**, **CONAIISI**, **WICC**), publicaciones **IEEE** y desarrollos de **UNCuyo** e **INTA Mendoza**— ilustran cómo articular el problema real con la transmisión de datos:

### Caso A: Monitoreo Microclimático de Heladas y Riego en Zonas Rurales (AgTech / Mendoza)
* **Problema real:** En viñedos y frutales de Cuyo, la temperatura y la humedad varían según cuadros y alturas del terreno. En el campo no hay cobertura Wi-Fi continua ni red eléctrica en cada hilera, y las estaciones comerciales importadas son inaccesibles para pequeños productores.
* **Estado del arte:** Redes WSN ensayadas por equipos de UNCuyo e INTA y artículos de telemetría agrícola con arquitectura híbrida **ESP-NOW + MQTT**.
* **Aporte en Transmisión de Datos:** Separar nodos sensores de ultra bajo consumo en campo respecto de un nodo concentrador (Gateway) en el casco de la finca, alertando si un nodo deja de reportar en su ventana de tiempo.

### Caso B: Trazabilidad de Cadena de Frío en Farmacias, Centros de Salud o Alimentos
* **Problema real:** Muchas heladeras de vacunas en centros de salud o cámaras de comercios se registran manualmente en planillas dos veces por día. Un corte nocturno de energía o una puerta mal cerrada provoca pérdidas graves que se descubren tarde.
* **Estado del arte:** Sistemas basados en microcontroladores Wi-Fi y protocolo **MQTT** utilizando calidad de servicio (*QoS*) y mensaje *Last Will and Testament (LWT)* para alertar caídas del enlace.
* **Aporte en Transmisión de Datos:** Monitorear no solo el umbral de temperatura, sino la **supervivencia del nodo** (*heartbeat* / *timeout*), detectando fallas de red antes de que se rompa la cadena de frío.

### Caso C: Calidad de Aire ($\text{CO}_2$) y Ventilación Inteligente en Aulas o Talleres
* **Problema real:** En aulas o talleres cerrados, el $\text{CO}_2$ sube rápidamente reduciendo el rendimiento cognitivo, pero dejar extractores o ventanas abiertas todo el invierno desperdicia energía térmica.
* **Estado del arte:** Redes universitarias de calidad de aire interior (*IAQ*) que desacoplan los nodos de medición en pupitres respecto de los nodos de actuación en tableros eléctricos vía Mosquitto y Node-RED.
* **Aporte en Transmisión de Datos:** Comunicación publicación/suscripción con confirmación de ejecución (*ACK*) y modo seguro local si el servidor central no responde.

### Caso D: Telemetría Preventiva de Bombas de Agua o Motores en Galpones
* **Problema real:** Bombas de pozo o motores de extracción suelen trabajar en vacío o sobrecalentarse lejos de la vista del operario hasta quemarse, generando paradas de planta muy costosas.
* **Estado del arte:** Sistemas de mantenimiento preventivo de bajo costo para PyMEs que monitorean vibración, temperatura o corriente sin tender cableados industriales caros.
* **Aporte en Transmisión de Datos:** Telemetría periódica combinada con envío inmediato de alarmas prioritarias por evento y corte de protección local si el gateway no acusa recibo dentro de una ventana de tiempo predeterminada (*timeout*).
