# 3. Diagrama de Comunicación de Datos

Dado que el proyecto se desarrolla en la asignatura **Transmisión de Datos**, es indispensable modelar explícitamente cómo viaja la información entre los dispositivos de la red. Mientras que el diagrama de flujo muestra la lógica interna de pasos y decisiones dentro de cada microcontrolador, el **Diagrama de Comunicación de Datos (o Diagrama de Secuencia)** modela el intercambio de mensajes a lo largo del tiempo entre los distintos nodos de la arquitectura.

---

## 1. Ingeniería del Dato: Tabla de Variables de Transmisión

Antes de dibujar el diagrama de comunicación, cada equipo debe realizar la **Ingeniería del Dato**. Esto consiste en definir con precisión qué viaja por el aire, en qué formato y por qué con esa frecuencia temporal:

### 📋 Ejemplo de Tabla de Variables a Entregar:

| Variable Física / Evento | Identificador / Tópico | Tipo de Dato (C/C++) | Tamaño Payload | Frecuencia de Envío | Justificación Técnica de la Frecuencia |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Temperatura de Suelo** | `finca/c1/suelo/temp` | `float` | 4 bytes | Cada 15 minutos | La temperatura del suelo tiene gran inercia térmica; muestrear más rápido no aporta información y agotaría la batería. |
| **Humedad Relativa** | `finca/c1/aire/hum` | `uint16_t` | 2 bytes | Cada 5 minutos | Permite detectar el rocío previo a una helada con tiempo suficiente de alerta. |
| **Alarma de Helada Inminente** | `finca/c1/alarma` | `uint8_t` (código de evento) | 1 byte | Inmediato por evento | Disparo prioritario cuando la temperatura cae por debajo de 0.5 °C para activar aspersores o estufas. |
| **Nivel de Batería del Nodo** | `finca/c1/nodo1/vbat` | `uint16_t` (mV) | 2 bytes | Cada 6 horas | El voltaje de la celda Li-Ion decae lentamente; permite mantenimiento preventivo antes del apagado. |
| **Heartbeat (Supervivencia)** | `finca/c1/nodo1/ping` | `uint32_t` (uptime s) | 4 bytes | Cada 10 minutos | Informa al Gateway que el nodo sigue vivo incluso si los valores medidos no cambian. |

> 💡 **Criterio de Evaluación:** Si envían lecturas de temperatura cada 500 milisegundos en un sistema alimentado a batería, se considerará un error de diseño técnico. Todo intervalo debe estar justificado en base a la dinámica del fenómeno físico real.

---

## 2. Instrucciones para el Diagrama de Secuencia

Representen cada elemento del sistema como una columna vertical (línea de vida) y cada interacción como una flecha horizontal dirigida en orden cronológico descendente.

### Elementos obligatorios en cada flecha:
1. **Tipo de primitiva:** `"Lectura de sensor"`, `"Trama ESP-NOW"`, `"PUBLISH MQTT"`, `"ACK (Confirmación)"`, `"Comando de actuación"`.
2. **Protocolo:** Especificar si el salto es físico local (`I2C`/`ADC`), inalámbrico local (`ESP-NOW`), o sobre red IP (`MQTT`/`HTTP`).
3. **Contenido:** Indicar qué datos o parámetros viajan en la trama.
4. **Manejo de Fallas y Timeouts (Temporizadores):** Qué sucede cuando un nodo o el servidor no responde dentro de la ventana de tiempo esperada.

---

## 3. Ejemplo de Modelado: Operación Normal vs. Caso de Timeout

```
┌─────────────┐       ┌─────────────┐       ┌───────────────┐       ┌───────────────┐       ┌───────────────┐
│ Sensor Temp │       │ Nodo ESP #1 │       │ Servidor/MQTT │       │  Nodo ESP #2  │       │ Relé/Actuador │
└──────┬──────┘       └──────┬──────┘       └───────┬───────┘       └───────┬───────┘       └───────┬───────┘
       │                     │                      │                       │                       │
       │ === OPERACIÓN NORMAL (CICLO PERIÓDICO) === │                       │                       │
       │                     │                      │                       │                       │
       │ 1. Lectura ADC/I2C  │                      │                       │                       │
       │    Temp = 23.4 °C   │                      │                       │                       │
       │────────────────────>│                      │                       │                       │
       │                     │ 2. PUBLISH MQTT      │                       │                       │
       │                     │    tópico: temp/val  │                       │                       │
       │                     │─────────────────────>│                       │                       │
       │                     │                      │ 3. Notificación       │                       │
       │                     │                      │    a suscriptor       │                       │
       │                     │                      │──────────────────────>│                       │
       │                     │                      │                       │ 4. Conmuta Relé       │
       │                     │                      │                       │    Estado: ON         │
       │                     │                      │                       │──────────────────────>│
       │                     │                      │                       │                       │
       │ === CASO DE FALLA: TIMEOUT EN LA COMUNICACIÓN ===                  │                       │
       │                     │                      │                       │                       │
       │                     │ 5. PUBLISH MQTT      │                       │                       │
       │                     │    (Enlace caído)    │                       │                       │
       │                     │─────── - - - - - - ->X [Sin conexión]       │                       │
       │                     │                      │                       │                       │
       │                     │ [Inicia Timer: 500ms]│                       │                       │
       │                     │ ⏰ Timeout expirado! │                       │                       │
       │                     │                      │                       │                       │
       │                     │ 6. Reintento #1      │                       │                       │
       │                     │─────── - - - - - - ->X [Falla de nuevo]      │                       │
       │                     │                      │                       │                       │
       │                     │ 7. Política local:   │                       │                       │
       │                     │    Guarda en Flash   │                       │                       │
       │                     │    (SPIFFS/LittleFS) │                       │                       │
       │                     │    Pasa a Deep Sleep │                       │                       │
       │                     │──────┐               │                       │                       │
       │                     │      │ Contingencia  │                       │                       │
       │                     │<─────┘               │                       │                       │
┌──────┴──────┐       ┌──────┴──────┐       ┌───────┴───────┐       ┌───────┴───────┐       ┌───────┴───────┐
│ Sensor Temp │       │ Nodo ESP #1 │       │ Servidor/MQTT │       │  Nodo ESP #2  │       │ Relé/Actuador │
└─────────────┘       └─────────────┘       └───────────────┘       └───────────────┘       └───────────────┘
```

---

## 4. Política de Contingencia ante Fallos de Enlace

Un sistema de comunicaciones profesional nunca se queda bloqueado esperando una respuesta indefinidamente en un bucle infinito (`while(!connected);`).

En el informe del proyecto, cada equipo debe detallar su **estrategia ante fallas**:
1. **Definición del Timeout:** ¿Cuántos milisegundos espera el nodo antes de dar por perdido un paquete? (ej. 200 ms para ESP-NOW; 1.500 ms para TCP/MQTT).
2. **Cantidad de Reintentos:** Cuántas veces se reintenta el envío (se recomienda un máximo de 2 a 3 intentos).
3. **Acción de Respaldo (*Fallback*):**
   * *Si es un nodo sensor alimentado a batería:* Debe almacenar el paquete en una cola en memoria Flash local (para no perder el dato histórico) y entrar inmediatamente en suspensión profunda (*Deep Sleep*), reintentando enviar el lote acumulado en la siguiente ventana de reporte.
   * *Si es un nodo actuador:* Debe contar con un estado seguro (*failsafe*). Por ejemplo, si una bomba o calefactor no recibe comando de control en más de 20 minutos, debe apagarse preventivamente para evitar accidentes.
