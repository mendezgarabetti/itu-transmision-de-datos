# 4. Consigna de Entrega, Rúbrica y Pautas

* **Asignatura:** Transmisión de Datos — ITU, Universidad Nacional de Cuyo
* **Modalidad:** Grupal (equipos constituidos de la cátedra)
* **Fecha límite de entrega:** **Viernes 27 de noviembre de 2026**
* **Formato:** Archivo PDF único denominado `GRUPOX_Proyecto_IDI_TxDatos.pdf`
* **Canal de entrega:** A través de Discord, cada integrante sube el PDF a su canal privado `#entrega-nombre-apellido`.

---

## Objetivo Central

Formalizar la evolución del proyecto previo aplicando la metodología de **Investigación, Desarrollo e Innovación (I+D+i)**:
1. **No agregar complejidad artificial:** Prohibido sumar sensores, displays o placas sin justificación técnica.
2. **Impacto en el mundo real:** Delimitar un problema concreto y tangible.
3. **Investigación del Estado del Arte:** Contrastar su desarrollo frente a soluciones comerciales y comunitarias existentes.
4. **Ingeniería de la Transmisión de Datos:** Especificar variables, protocolos y diagramas de secuencia con manejo de *timeouts*.

---

## Estructura Obligatoria del Documento (PDF)

El informe debe seguir rigurosamente las siguientes secciones:

### 1. Carátula e Identificación
* Título formal del proyecto (orientado a la solución del problema real).
* Número de grupo, comisión (A o B) y nómina completa de integrantes (Apellido, Nombre y Correo).

### 2. Diagnóstico Crítico del Prototipo Previo (Línea Base)
* **Qué resolvía el prototipo anterior:** breve descripción funcional y componentes empleados.
* **Por qué no alcanzaba para el mundo real:** identificar al menos **3 limitaciones técnicas concretas** del prototipo anterior (ej. nodo único centralizado, dependencia de Wi-Fi de hogar, ausencia de control de errores o timeouts, alto consumo de batería, alcance insuficiente).

### 3. Problema Real Situado y Justificación
* **Definición del problema:** contexto concreto (agro/riego/heladas, cadena de frío en salud/alimentos, ventilación en aulas, telemetría de bombas industriales, etc.), quién padece el problema y qué pérdidas o riesgos genera hoy.
* **Justificación de la arquitectura inalámbrica:** por qué las condiciones del entorno impiden tender cables y exigen dos o más nodos inalámbricos distribuidos.

### 4. Relevamiento Sistemático del Estado del Arte (La "I" de I+D+i)
* **Soluciones comerciales existentes:** análisis de al menos **2 productos del mercado**, describiendo tecnologías, arquitectura y limitaciones (costo elevado, nube propietaria cerrada, dependencia de conexión a Internet permanente).
* **Proyectos abiertos o literatura técnica:** análisis de al menos **2 proyectos open source o publicaciones académicas** (GitHub, Hackaday, IEEE, congresos CACIC/CONAIISI/WICC) que hayan abordado problemas análogos.
* **Matriz Comparativa del Estado del Arte:** tabla completa comparando las 4 soluciones relevadas frente a la propuesta del grupo (evaluando tecnología de transmisión, costo, dependencias y limitaciones superadas).

### 5. Propuesta de Valor y los 5 Vectores de Innovación (La "i")
* Justificación rigurosa de en cuáles de los 5 vectores el proyecto genera un aporte diferencial:
  1. **¿Más barato?** (Democratización de costos frente a alternativas industriales).
  2. **¿Más rápido / eficiente?** (Optimización de consumo energético y payload).
  3. **¿Mejor / más robusto?** (Operación local offline y tolerancia a fallos).
  4. **¿A mayor escala?** (Capacidad de expansión de nodos).
  5. **¿Código Abierto / Hardware Libre?** (Soberanía tecnológica y ausencia de vendor lock-in).

### 6. Ingeniería de la Transmisión de Datos (La "D")
* **Tabla de Variables de Transmisión:** variables físicas, identificador/tópico, tipo de dato en C/C++, tamaño en bytes, frecuencia de envío e intervalo justificado técnicamente.
* **Justificación de Protocolos:** explicación de la elección de los protocolos de capa de aplicación y transporte (ESP-NOW, MQTT, HTTP, etc.) en base a las restricciones del entorno.

### 7. Diagramas Técnicos de Diseño
* **Diagrama de Flujo de Ejecución:** utilizando las 6 figuras normalizadas (óvalo, rectángulo, rombo, paralelogramo, flechas, círculo) que modele la lógica y toma de decisiones de los nodos.
* **Diagrama de Comunicación de Datos (Secuencia con Timeout):** líneas de vida de los dispositivos, mensajes cronológicos, primitivas de protocolo y el modelado explícito de la política de contingencia ante caídas de enlace (timeout, reintentos y fallback a memoria Flash).

### 8. Referencias Bibliográficas
* Citas completas de todas las fuentes comerciales, datasheets, artículos y repositorios consultados (formato IEEE o APA con enlaces accesibles).

---

## Rúbrica de Calificación

| Dimensión de Evaluación | Excelente (10 - 9 pts) | Suficiente (8 - 6 pts) | Insuficiente (5 - 1 pts) |
| :--- | :--- | :--- | :--- |
| **1. Estado del Arte e Investigación (40%)** | Relevamiento exhaustivo y riguroso de al menos 2 soluciones comerciales y 2 abiertas. Matriz comparativa impecable con análisis crítico de cuellos de botella y limitaciones reales. | Releva las fuentes pero el análisis es superficial o describe folletos comerciales sin profundizar en las limitaciones técnicas. Matriz incompleta. | No investiga soluciones existentes o incluye datos ficticios/copiados sin rigor. Ausencia de matriz comparativa. |
| **2. Justificación Técnica y Valor Diferencial (30%)** | Fundamentación sólida de los vectores de innovación. Cero complejidad artificial: cada componente y nodo nuevo está técnicamente justificado por el problema real. | La propuesta tiene valor pero arrastra elementos innecesarios o la justificación de los vectores es vaga (ej. «es más barato porque sí»). | Complejidad artificial evidente (sensores o pantallas agregadas sin sentido de transmisión) o copia directa de un tutorial existente sin valor nuevo. |
| **3. Ingeniería del Dato y Diagramas Técnicos (30%)** | Tabla de variables con tamaños en bytes y frecuencias plenamente justificadas. Diagrama de flujo normalizado y diagrama de secuencia con modelado riguroso de timeouts y contingencia. | Los diagramas son comprensibles pero omiten el caso de fallo/timeout o la tabla de variables no justifica los intervalos de muestreo. | Diagramas informales, ilegibles o ausentes. No se modela la transmisión de datos ni la recuperación ante caídas de enlace. |

---

## Modalidad de Entrega en Discord

1. Cada integrante ingresa a su canal privado **`#entrega-nombre-apellido`** en el servidor de Discord.
2. Sube el archivo PDF (`GRUPOX_Proyecto_IDI_TxDatos.pdf`).
3. En el texto del mensaje debe indicar:
   * **Nombre del Proyecto / Grupo**
   * **Comisión (A o B)**
   * **Listado de todos los integrantes del equipo**
4. Fecha límite impostergable: **Viernes 27 de noviembre de 2026 a las 23:59 hs**.
