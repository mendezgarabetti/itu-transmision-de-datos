# 2. Diseño de la Solución: Diagrama de Flujo

Antes de programar debemos tener claro qué debe hacer nuestro proyecto y cómo responde a las necesidades del problema real identificado.

## Creación de un Diagrama de Flujo de Ejecución

### Objetivo
Crear un diagrama de flujo que describa, a nivel conceptual, cómo debería comportarse el proyecto que están evolucionando con los nodos inalámbricos (**ESP8266 / ESP32**), sin necesidad de utilizar código de programación. El diagrama les permitirá visualizar la secuencia de pasos y decisiones que tomará cada nodo dentro del sistema, facilitando la comprensión del funcionamiento general antes de la implementación técnica.

---

## Instrucciones

### 1. Planteamiento del Proyecto
Antes de crear el diagrama, revisen el problema real validado en el estado del arte y piensen en los siguientes aspectos:
* ¿Qué acciones realizarán los nodos ESP8266 / ESP32?
* ¿Qué información o datos medirán, recibirán o enviarán?
* ¿Qué decisiones deberán tomar los nodos en función de los datos que reciben o ante la falta de respuesta de otro nodo?

### 2. Creación del Diagrama
* Usen una herramienta como **draw.io (diagrams.net)**, **Lucidchart** o similar para crear el diagrama de flujo.
* El diagrama debe representar claramente los pasos que seguirá el sistema, desde el inicio hasta la resolución del ciclo de trabajo.
* Incluyan los siguientes elementos:
  * **Inicio:** Representa el punto donde comienza el sistema o ciclo del nodo.
  * **Acciones:** Como `"Leer datos del sensor"`, `"Enviar paquete por MQTT/ESP-NOW"`, `"Activar relé"`, etc.
  * **Decisiones:** Como `"¿El valor del sensor supera el umbral?"` o `"¿Se recibió confirmación antes del timeout?"`, que guían el flujo hacia diferentes caminos según las respuestas (**Sí** o **No**).
  * **Finalización / Retorno al ciclo:** Indica cuándo el sistema ha cumplido su objetivo o regresa al estado de espera/monitoreo.

---

## Ejemplo Explicado: Sistema de Control de Luz Automática con ESP8266

### Descripción del Proyecto Base
Imaginemos un sistema sencillo que enciende una luz automáticamente cuando se detecta movimiento y la apaga si no hay movimiento después de cierto tiempo:

1. **Inicio:** El sistema está en espera.
2. **Acción:** El nodo ESP8266 recibe información del sensor de movimiento.
3. **Decisión:** ¿Se ha detectado movimiento?
   * **Sí:** El ESP8266 envía una señal para encender la luz.
   * **No:** El sistema sigue en espera.
4. **Acción:** Después de encender la luz, el sistema espera un período de tiempo.
5. **Decisión:** ¿Hay movimiento nuevamente?
   * **Sí:** Mantener la luz encendida.
   * **No:** El ESP8266 apaga la luz.
6. **Fin:** El sistema regresa al estado inicial, esperando más movimiento.

> **Nota para su proyecto de I+D+i:** Dado que su proyecto involucra al menos dos nodos comunicándose para resolver un problema real, el diagrama de flujo debe reflejar con claridad la lógica de adquisición, transmisión, decisión y respuesta ante fallos de comunicación.

---

## Figuras Estandarizadas de un Diagrama de Flujo

En un diagrama de flujo se utilizan figuras estandarizadas para representar diferentes tipos de acciones, procesos o decisiones:

### 1. Óvalo (Inicio / Fin)
* **Descripción:** Se utiliza para marcar el inicio o el fin del proceso.
* **Uso:** Siempre debe haber al menos un óvalo que indique el **Inicio** y otro que indique el **Fin** del flujo.
* **Ejemplo de texto:** `"Inicio"` o `"Fin"`.

### 2. Rectángulo (Proceso o Acción)
* **Descripción:** Representa una acción o proceso interno que se debe realizar.
* **Uso:** Describir una tarea o actividad concreta del nodo.
* **Ejemplo de texto:** `"Inicializar conexión"`, `"Procesar promedio de lecturas"` o `"Activar relé de bomba"`.

### 3. Rombo (Decisión)
* **Descripción:** Representa un punto donde el flujo toma una decisión basada en una condición (**Sí / No** o **Verdadero / Falso**).
* **Uso:** El rombo siempre tiene al menos dos flechas de salida rotuladas, una para cada resultado de la decisión.
* **Ejemplo de texto:** `"¿Humedad < 30%?"` o `"¿Hubo respuesta antes del timeout?"`.

### 4. Flechas (Conector de Flujo)
* **Descripción:** Indican la dirección y el orden temporal del flujo del proceso.
* **Uso:** Conectan las figuras entre sí y guían al lector en la secuencia exacta de pasos.

### 5. Paralelogramo (Entrada / Salida de Datos)
* **Descripción:** Se usa para representar entradas o salidas de datos hacia o desde el exterior del nodo.
* **Uso:** Indica cuándo el sistema está leyendo un sensor, recibiendo un paquete de red o enviando información.
* **Ejemplo de texto:** `"Leer temperatura del sensor"`, `"Publicar payload MQTT"` o `"Mostrar alerta en pantalla"`.

### 6. Círculo (Conector dentro del flujo)
* **Descripción:** Se utiliza para enlazar partes del diagrama que están muy separadas.
* **Uso:** Dentro de un diagrama extenso, un círculo con una letra o número (por ejemplo, `"A"`) indica que el flujo continúa en otro punto marcado con la misma letra.
