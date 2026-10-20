# Transmisión de Datos · Prácticas con Mininet

Instituto Tecnológico Universitario (ITU) · Universidad Nacional de Cuyo

Repositorio de prácticas de laboratorio de la cátedra. Cada práctica vive en su propia carpeta y
se agregan nuevas a medida que avanza el cursado.

| Carpeta | Práctica | Unidad |
| :--- | :--- | :--- |
| [`actividad1/`](actividad1/) | Topología mínima, ARP e ICMP con captura en Wireshark | 2 |

Presentación de la clase: <https://fosshlab.org/itu-txd/presentacion-mininet/>

## 1. Clonar el repositorio en la VM de Mininet

Conectate a tu VM (usuario y clave `mininet`) y ejecutá:

```bash
git clone https://github.com/mendezgarabetti/itu-transmision-de-datos.git
cd itu-transmision-de-datos
```

## 2. Traer las prácticas nuevas

Antes de cada clase:

```bash
cd ~/itu-transmision-de-datos
git pull
```

> **No modifiques los archivos originales.** Si querés experimentar, copiá el script con otro
> nombre (`cp actividad1_topologia.py mi_topologia.py`). Así `git pull` nunca entra en conflicto.
> Las capturas (`.pcap`) y los resúmenes que generan los scripts ya están ignorados por git.

Si `git pull` se queja de cambios locales, descartalos con `git checkout -- .` y repetí el `pull`.

## 3. Sin `git` o sin acceso a GitHub

Descargá el repositorio comprimido:

```bash
wget https://github.com/mendezgarabetti/itu-transmision-de-datos/archive/refs/heads/main.zip
unzip main.zip && cd itu-transmision-de-datos-main
```

## Requisitos

- VM oficial de Mininet (<https://mininet.org/download/>), con Mininet, Open vSwitch y Wireshark.
- Los scripts son compatibles con Python 3.5 o superior (VM con Ubuntu 16.04 en adelante).
- Siempre se ejecutan con `sudo`; si algo queda trabado: `sudo mn -c`.
