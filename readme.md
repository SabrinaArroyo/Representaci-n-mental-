# Tarea de Representación Mental – Metáforas Espaciales

Tarea experimental de neurociencia cognitiva en la que los participantes leen metáforas y arrastran las palabras clave a los cuadrantes de una cuadrícula 2×2 que mejor representen la relación espacial de la metáfora.

---

## Requisitos

- **Python 3.8+**
- **tkinter** (incluido en Python estándar, Anaconda y la mayoría de distribuciones)
- **Sin dependencias externas** — no se instala nada con pip

Verifica antes de empezar:
```bash
python -c "import tkinter; print('tkinter OK')"
```

Si tkinter no está instalado:

| Sistema | Comando |
|---|---|
| Ubuntu / Debian | `sudo apt-get install python3-tk` |
| macOS (Homebrew) | `brew install python-tk@3.11` |
| Windows | incluido al instalar desde [python.org](https://python.org) |
| Anaconda | `conda install tk` |

---

## Instalación y ejecución

### 1. Clonar el repositorio

```bash
git clone https://github.com/SabrinaArroyo/Representaci-n-mental-.git
cd Representaci-n-mental-
```

---

### Opción A — Con Anaconda / Miniconda

```bash
conda activate base
python Tarea_prueba.py
```

Si tkinter no estuviera disponible en el entorno:
```bash
conda install tk
python Tarea_prueba.py
```

---

### Opción B — Sin conda (Python estándar + entorno virtual)

```bash
# Crear entorno virtual (solo la primera vez)
python -m venv .mivirtualenv

# Activar
source .mivirtualenv/bin/activate        # macOS / Linux
.venv\Scripts\activate            # Windows

# Verificar tkinter y correr
python -c "import tkinter; print('tkinter OK')"
python Tarea_prueba.py
```

> **Nota:** no hay paquetes que instalar con `pip install -r requirements.txt`  
> porque el proyecto usa únicamente la biblioteca estándar.  
> El archivo `requirements.txt` documenta las dependencias y cómo instalar tkinter por sistema.

---

### Opción C — Python directamente (sin entorno virtual)

```bash
python Tarea_prueba.py
# o en sistemas donde python apunta a Python 2:
python3 Tarea_prueba.py
```

> ⚠️ **macOS únicamente:** el Python del sistema (`/usr/bin/python3`) puede lanzar el error  
> `macOS 13 (1307) or later required` y cerrarse al abrir la ventana.  
> Usa Anaconda (Opción A) o un entorno virtual (Opción B) en su lugar.

---

## Estructura del experimento

| Bloque | Ensayos | Selección |
|---|---|---|
| Práctica | 4 (2 determinadas + 2 indeterminadas) | Fijos, con retroalimentación |
| Tarea | 16 (8 determinadas + 8 indeterminadas) | Aleatorios de las 24+24 disponibles |

Los 16 ensayos de la tarea son distintos en cada corrida.

---

## Estructura de la cuadrícula

```
┌──────────────────┬──────────────────┐
│  Q1              │  Q2              │
│  Arriba Izq.     │  Arriba Der.     │
├──────────────────┼──────────────────┤
│  Q3              │  Q4              │
│  Abajo Izq.      │  Abajo Der.      │
└──────────────────┴──────────────────┘
```

---

## Tipos de metáforas

- **Determinadas**: relación espacial clara (arriba, abajo, izquierda, derecha, sobre, dentro…). Configuraciones válidas restringidas.
- **Indeterminadas**: relación espacial ambigua. Acepta configuraciones diagonales, laterales, o cualquier par distinto según el grado de ambigüedad.

### Relaciones y configuraciones válidas

| Relación | Configuraciones válidas (sujeto → objeto) |
|---|---|
| `arriba` / `sobre` / `encima` | Q1→Q3, Q1→Q4, Q2→Q3, Q2→Q4 |
| `abajo` / `bajo` / `debajo` | Q3→Q1, Q3→Q2, Q4→Q1, Q4→Q2 |
| `izquierda` | Q1→Q2, Q3→Q4 |
| `derecha` | Q2→Q1, Q4→Q3 |
| `diagonal_opuesta` | Q1↔Q4, Q2↔Q3 |
| `diagonal_o_lateral` | diagonal + lateral (8 configs) |
| `lateral_superior` | Q1↔Q2 |
| `lateral_inferior` | Q3↔Q4 |
| `dentro` | pares adyacentes (8 configs) |
| `indeterminada` | cualquier par distinto (12 configs) |

---

## Calificación

- **Total (0 / 100):** la pareja (q_sujeto, q_objeto) debe estar en la lista de configuraciones válidas de la relación.
- **Parcial (0–100):** porcentaje de las 2 palabras principales colocadas en cuadrantes que aparecen en al menos alguna configuración válida.

---

## Salida de datos

Los resultados se guardan automáticamente en la carpeta `data/` al finalizar la tarea:

```
data/<participante_id>_Metaforas_Espaciales_<YYYYMMDD_HHMMSS>.csv
```

### Columnas del CSV

| Columna | Descripción |
|---|---|
| `participante` | ID ingresado en la pantalla de inicio |
| `num_ensayo` | Número de ensayo (1-16) |
| `tipo_metafora` | `determinada` / `indeterminada` |
| `texto_metafora` | Texto completo de la metáfora |
| `relacion` | Relación espacial asignada |
| `sujeto` / `objeto` | Las dos palabras arrastrables |
| `q_sujeto_participante` | Cuadrante donde colocó el sujeto (1-4) |
| `q_objeto_participante` | Cuadrante donde colocó el objeto (1-4) |
| `config_valida` | `True` / `False` |
| `configs_validas` | Lista de todas las configuraciones válidas |
| `total_score` | 100 si config válida, 0 si no |
| `parcial_score` | % de palabras bien ubicadas (0-100) |
| `respuesta_boton` | `Listo` / `No se puede determinar` |
| `rt_lectura_s` | Tiempo de lectura (segundos) |
| `rt_inferencia_s` | Tiempo de respuesta en la tarea (segundos) |
| `fecha_hora` | Marca de tiempo del ensayo |

---

## Parámetros configurables

En la sección `PARÁMETROS CONFIGURABLES` de `Tarea_prueba.py`:

```python
FIXATION_DURATION_MS    = 500    # duración cruz de fijación (ms)
READING_TIME_MS         = 4000   # tiempo máximo de lectura (ms)
ITI_MS                  = 1000   # intervalo entre ensayos (ms)
PRACTICE_PASS_THRESHOLD = 0.75   # mínimo para pasar la práctica (75%)
PILOT_MODE              = True   # True = 8+8 ensayos; False = tarea completa
PILOT_TRIALS            = 8      # ensayos por tipo en modo piloto
FULL_TASK_MODE          = False  # True = usa las 48 metáforas completas
```
