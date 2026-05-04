#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tarea de Representación Mental – Metáforas Espaciales
======================================================
Cada ensayo muestra una metáfora; el participante arrastra palabras
a los cuadrantes de una cuadrícula 2×2.

Lógica de calificación:
  Se definen RELACIONES ESPACIALES abstractas (arriba, abajo, izquierda,
  derecha, diagonal, etc.) y para cada relación se calculan
  TODAS las configuraciones de cuadrante válidas.
  No hay una respuesta única: cualquier configuración que respete
  la relación espacial de la metáfora es correcta.

Cuadrantes:
    1 = arriba_izquierda  |  2 = arriba_derecha
    ─────────────────────────────────────────────
    3 = abajo_izquierda   |  4 = abajo_derecha

Interfaz : tkinter (biblioteca estándar de Python)
Datos    : data/<participante>_Metaforas_Espaciales_<timestamp>.csv

SUPUESTOS DOCUMENTADOS:
  1. Metáforas sin anotación de cuadrante en el .docx → relación inferida
     por la preposición espacial dominante de la metáfora.
  2. Todos los ensayos (determinados e indeterminados) presentan exactamente
     2 palabras arrastrables: sujeto y objeto.
     La diferencia entre tipos está en el número de configuraciones válidas,
     no en el número de palabras mostradas.
  3. Para metáforas indeterminadas las configuraciones válidas son más
     permisivas: cualquier configuración que respete la relación es válida.
  4. Se usa tkinter en lugar de PsychoPy porque tkinter es estándar y
     portable. Para precisión de ms en TR se recomienda migrar a PsychoPy.
"""

import tkinter as tk
import csv
import os
import random
import time
from datetime import datetime
from itertools import permutations

# ═══════════════════════════════════════════════════════════════════════
# CONVENCIÓN DE CUADRANTES
# ═══════════════════════════════════════════════════════════════════════
QUADRANTS = {
    1: "arriba_izquierda",
    2: "arriba_derecha",
    3: "abajo_izquierda",
    4: "abajo_derecha",
}

# Propiedades geométricas de cada cuadrante
# fila: 0=arriba, 1=abajo  |  col: 0=izquierda, 1=derecha
QUADRANT_PROPS = {
    1: {"fila": 0, "col": 0},
    2: {"fila": 0, "col": 1},
    3: {"fila": 1, "col": 0},
    4: {"fila": 1, "col": 1},
}

# ═══════════════════════════════════════════════════════════════════════
# MOTOR DE RELACIONES ESPACIALES
# Genera TODAS las configuraciones válidas (sujeto_q, objeto_q)
# para una relación dada sobre una cuadrícula 2×2.
# ═══════════════════════════════════════════════════════════════════════

def _pares_distintos():
    """Devuelve todos los pares (q_a, q_b) con q_a ≠ q_b."""
    qs = list(QUADRANT_PROPS.keys())
    return [(a, b) for a in qs for b in qs if a != b]

def configuraciones_arriba():
    """Sujeto en fila superior, objeto en fila inferior (misma col o distinta)."""
    return [(a, b) for a, b in _pares_distintos()
            if QUADRANT_PROPS[a]["fila"] < QUADRANT_PROPS[b]["fila"]]
    # → (1,3), (1,4), (2,3), (2,4)

def configuraciones_abajo():
    """Sujeto en fila inferior, objeto en fila superior."""
    return [(a, b) for a, b in _pares_distintos()
            if QUADRANT_PROPS[a]["fila"] > QUADRANT_PROPS[b]["fila"]]
    # → (3,1), (3,2), (4,1), (4,2)

def configuraciones_izquierda():
    """Sujeto en columna izquierda, objeto en columna derecha."""
    return [(a, b) for a, b in _pares_distintos()
            if QUADRANT_PROPS[a]["col"] < QUADRANT_PROPS[b]["col"]]
    # → (1,2), (3,4)

def configuraciones_derecha():
    """Sujeto en columna derecha, objeto en columna izquierda."""
    return [(a, b) for a, b in _pares_distintos()
            if QUADRANT_PROPS[a]["col"] > QUADRANT_PROPS[b]["col"]]
    # → (2,1), (4,3)

def configuraciones_diagonal_opuesta():
    """Sujeto y objeto en cuadrantes diagonalmente opuestos (1↔4, 2↔3)."""
    return [(1,4),(4,1),(2,3),(3,2)]

def configuraciones_lateral_superior():
    """Ambos en fila superior pero columnas distintas (frente a frente horizontal)."""
    return [(1,2),(2,1)]

def configuraciones_lateral_inferior():
    """Ambos en fila inferior pero columnas distintas."""
    return [(3,4),(4,3)]

def configuraciones_diagonal_o_lateral():
    """
    Relación espacial ambigua: válido tanto en diagonal opuesta como
    en posición lateral (misma fila, distinta columna).
    Cubre 8 configuraciones:
      diagonal : (1,4),(4,1),(2,3),(3,2)
      lateral  : (1,2),(2,1),(3,4),(4,3)
    """
    return [(1,4),(4,1),(2,3),(3,2),(1,2),(2,1),(3,4),(4,3)]

def configuraciones_dentro():
    """
    'Dentro de' / 'dentro del': relación contenedor.
    Convenio: sujeto en cualquier cuadrante, objeto en cuadrante adyacente.
    Adyacentes = comparten fila o columna (no diagonales opuestos).
    """
    adyacentes = [(1,2),(2,1),(1,3),(3,1),(2,4),(4,2),(3,4),(4,3)]
    return adyacentes

def configuraciones_sobre():
    """Alias de arriba (sobre = encima de)."""
    return configuraciones_arriba()

def configuraciones_bajo():
    """Alias de abajo (bajo = debajo de)."""
    return configuraciones_abajo()

def configuraciones_indeterminada():
    """
    Para metáforas indeterminadas/abstractas: cualquier par distinto es válido.
    El participante puede colocar las palabras en cualquier configuración
    siempre que cada palabra esté en un cuadrante diferente.
    """
    return _pares_distintos()

# Mapa de nombre_relacion → función generadora
RELACION_A_CONFIGURACIONES = {
    "arriba":              configuraciones_arriba,
    "sobre":               configuraciones_sobre,
    "encima":              configuraciones_arriba,
    "abajo":               configuraciones_abajo,
    "bajo":                configuraciones_bajo,
    "debajo":              configuraciones_abajo,
    "izquierda":           configuraciones_izquierda,
    "derecha":             configuraciones_derecha,
    "diagonal_opuesta":    configuraciones_diagonal_opuesta,
    "lateral_superior":    configuraciones_lateral_superior,
    "lateral_inferior":    configuraciones_lateral_inferior,
    "diagonal_o_lateral":  configuraciones_diagonal_o_lateral,
    "dentro":              configuraciones_dentro,
    "indeterminada":       configuraciones_indeterminada,
}

def obtener_configuraciones_validas(relacion: str):
    """
    Devuelve lista de tuplas (q_sujeto, q_objeto) válidas para la relación dada.
    Si la relación no se reconoce, devuelve todos los pares distintos.
    """
    fn = RELACION_A_CONFIGURACIONES.get(relacion, configuraciones_indeterminada)
    return fn()

# ═══════════════════════════════════════════════════════════════════════
# PARÁMETROS CONFIGURABLES
# ═══════════════════════════════════════════════════════════════════════
FIXATION_DURATION_MS    = 500   # duración cruz de fijación (ms)
READING_TIME_MS         = 4000  # tiempo máximo de lectura (ms)
ITI_MS                  = 1000  # intervalo entre ensayos (ms)
PRACTICE_PASS_THRESHOLD = 0.75  # mínimo para pasar la práctica
WINDOW_WIDTH            = 1100
WINDOW_HEIGHT           = 750
BG_COLOR                = "#1a1a2e"
GRID_COLOR              = "#e0e0e0"
TEXT_COLOR              = "#ffffff"

# ── Modo piloto ────────────────────────────────────────────────────────
# PILOT_MODE = True  → 3 determinadas + 3 indeterminadas (PILOT_TRIALS cada tipo)
# PILOT_MODE = False → tarea completa (FULL_TASK_MODE)
PILOT_MODE      = True
PILOT_TRIALS    = 8      # ensayos POR TIPO en modo piloto (8 det + 8 indet = 16 total)
FULL_TASK_MODE  = False

# ═══════════════════════════════════════════════════════════════════════
# ESTÍMULOS
# ═══════════════════════════════════════════════════════════════════════
#
# Cada ensayo tiene:
#   texto     : metáfora que se muestra al participante
#   tipo      : "determinada" | "indeterminada" | "distractor" | "practica_*"
#   sujeto    : primera palabra (la que "actúa" sobre la otra)
#   objeto    : segunda palabra (referencia espacial)
#   relacion  : clave de RELACION_A_CONFIGURACIONES
#   palabras_extra: palabras adicionales para metáforas indeterminadas (lista)
#
# Las configuraciones válidas se calculan DINÁMICAMENTE según la relación.
# No hay una sola respuesta correcta codificada a mano.

METAFORAS_DETERMINADAS = [
    # ── Con relación explícita en el documento ────────────────────────
    {"texto": "La lámpara cuida al libro justo arriba de él",
     "tipo": "determinada", "sujeto": "Lámpara", "objeto": "Libro",
     "relacion": "arriba", "palabras_extra": []},

    {"texto": "El reloj se posa debajo de la silla silenciosa",
     "tipo": "determinada", "sujeto": "Reloj", "objeto": "Silla",
     "relacion": "abajo", "palabras_extra": []},

    {"texto": "La taza permanece a la izquierda del cuaderno abierto",
     "tipo": "determinada", "sujeto": "Taza", "objeto": "Cuaderno",
     "relacion": "izquierda", "palabras_extra": []},

    {"texto": "El espejo vive a la derecha del jarrón antiguo",
     "tipo": "determinada", "sujeto": "Espejo", "objeto": "Jarrón",
     "relacion": "derecha", "palabras_extra": []},

    {"texto": "La pluma flota sobre el vaso en calma ligera",
     "tipo": "determinada", "sujeto": "Pluma", "objeto": "Vaso",
     "relacion": "sobre", "palabras_extra": []},

    {"texto": "El cuadro descansa bajo la mesa en sombra leve",
     "tipo": "determinada", "sujeto": "Cuadro", "objeto": "Mesa",
     "relacion": "bajo", "palabras_extra": []},

    {"texto": "La botella duerme a la izquierda del plato limpio",
     "tipo": "determinada", "sujeto": "Botella", "objeto": "Plato",
     "relacion": "izquierda", "palabras_extra": []},

    {"texto": "El teléfono se queda a la derecha del lápiz fino",
     "tipo": "determinada", "sujeto": "Teléfono", "objeto": "Lápiz",
     "relacion": "derecha", "palabras_extra": []},

    {"texto": "El libro reposa abajo a la izquierda de la taza",
     "tipo": "determinada", "sujeto": "Libro", "objeto": "Taza",
     "relacion": "abajo", "palabras_extra": []},

    {"texto": "El cuadro observa desde la izquierda a la mesa",
     "tipo": "determinada", "sujeto": "Cuadro", "objeto": "Mesa",
     "relacion": "izquierda", "palabras_extra": []},

    {"texto": "La silla respira a la derecha del espejo frío",
     "tipo": "determinada", "sujeto": "Silla", "objeto": "Espejo",
     "relacion": "derecha", "palabras_extra": []},

    {"texto": "La lámpara inclina su luz hacia el costado del libro",
     "tipo": "determinada", "sujeto": "Lámpara", "objeto": "Libro",
     "relacion": "izquierda", "palabras_extra": []},

    # ── Relación inferida por preposición dominante (SUPUESTO) ────────
    {"texto": "La luna está arriba del mar tranquilo y oscuro",
     "tipo": "determinada", "sujeto": "Luna", "objeto": "Mar",
     "relacion": "arriba", "palabras_extra": []},

    {"texto": "El sol brilla sobre la montaña firme y silenciosa",
     "tipo": "determinada", "sujeto": "Sol", "objeto": "Montaña",
     "relacion": "sobre", "palabras_extra": []},

    {"texto": "La raíz se esconde bajo la tierra húmeda fértil",
     "tipo": "determinada", "sujeto": "Raíz", "objeto": "Tierra",
     "relacion": "bajo", "palabras_extra": []},

    {"texto": "El puente se extiende sobre el río ancho caudaloso",
     "tipo": "determinada", "sujeto": "Puente", "objeto": "Río",
     "relacion": "sobre", "palabras_extra": []},

    {"texto": "La estrella brilla encima del desierto vasto infinito",
     "tipo": "determinada", "sujeto": "Estrella", "objeto": "Desierto",
     "relacion": "encima", "palabras_extra": []},

    {"texto": "El techo protege sobre las paredes firmes del hogar",
     "tipo": "determinada", "sujeto": "Techo", "objeto": "Paredes",
     "relacion": "sobre", "palabras_extra": []},

    {"texto": "La llave encaja dentro del candado cerrado metálico",
     "tipo": "determinada", "sujeto": "Llave", "objeto": "Candado",
     "relacion": "dentro", "palabras_extra": []},

    {"texto": "La columna sostiene bajo el arco antiguo del templo",
     "tipo": "determinada", "sujeto": "Columna", "objeto": "Arco",
     "relacion": "bajo", "palabras_extra": []},

    {"texto": "El mapa descansa sobre la mesa amplia ordenada",
     "tipo": "determinada", "sujeto": "Mapa", "objeto": "Mesa",
     "relacion": "sobre", "palabras_extra": []},

    {"texto": "La cabeza se apoya sobre los hombros fuertes rectos",
     "tipo": "determinada", "sujeto": "Cabeza", "objeto": "Hombros",
     "relacion": "sobre", "palabras_extra": []},

    {"texto": "El pilar sostiene bajo el arco sólido de piedra",
     "tipo": "determinada", "sujeto": "Pilar", "objeto": "Arco",
     "relacion": "bajo", "palabras_extra": []},

    {"texto": "La nube flota arriba del valle verde iluminado",
     "tipo": "determinada", "sujeto": "Nube", "objeto": "Valle",
     "relacion": "arriba", "palabras_extra": []},
]  # 24 determinadas

METAFORAS_INDETERMINADAS = [
    # ── Relación: diagonal_opuesta (vigilancia/observación desde esquina) ──
    {"texto": "La lámpara vigila al libro desde una esquina callada",
     "tipo": "indeterminada", "sujeto": "Lámpara", "objeto": "Libro",
     "relacion": "diagonal_opuesta", "palabras_extra": ["Esquina", "Silencio"]},

    {"texto": "El reloj observa la silla desde un rincón distante",
     "tipo": "indeterminada", "sujeto": "Reloj", "objeto": "Silla",
     "relacion": "diagonal_o_lateral", "palabras_extra": ["Rincón", "Distancia"]},

    {"texto": "El espejo sigue al jarrón desde una esquina opuesta",
     "tipo": "indeterminada", "sujeto": "Espejo", "objeto": "Jarrón",
     "relacion": "diagonal_opuesta", "palabras_extra": ["Esquina", "Opuesto"]},

    {"texto": "El foco espía al cuaderno desde un rincón silencioso",
     "tipo": "indeterminada", "sujeto": "Foco", "objeto": "Cuaderno",
     "relacion": "diagonal_o_lateral", "palabras_extra": ["Rincón", "Silencio"]},

    {"texto": "La mochila observa la lámpara desde un borde lejano",
     "tipo": "indeterminada", "sujeto": "Mochila", "objeto": "Lámpara",
     "relacion": "diagonal_o_lateral", "palabras_extra": ["Borde", "Lejanía"]},

    {"texto": "El reloj persigue la taza desde una esquina incierta",
     "tipo": "indeterminada", "sujeto": "Reloj", "objeto": "Taza",
     "relacion": "diagonal_o_lateral", "palabras_extra": ["Esquina", "Movimiento"]},

    {"texto": "El cuadro mira la mesa desde un ángulo apartado",
     "tipo": "indeterminada", "sujeto": "Cuadro", "objeto": "Mesa",
     "relacion": "diagonal_o_lateral", "palabras_extra": ["Ángulo", "Lejanía"]},

    {"texto": "La botella ilumina el libro desde un ángulo remoto",
     "tipo": "indeterminada", "sujeto": "Botella", "objeto": "Libro",
     "relacion": "diagonal_o_lateral", "palabras_extra": ["Ángulo", "Remoto"]},

    {"texto": "El lápiz encuentra la taza desde un rincón lejano",
     "tipo": "indeterminada", "sujeto": "Lápiz", "objeto": "Taza",
     "relacion": "diagonal_o_lateral", "palabras_extra": ["Rincón", "Lejanía"]},

    # ── Relación: lateral_superior (frente a frente, misma fila) ──────
    {"texto": "La taza acompaña al cuaderno desde un borde tranquilo",
     "tipo": "indeterminada", "sujeto": "Taza", "objeto": "Cuaderno",
     "relacion": "diagonal_o_lateral", "palabras_extra": ["Borde", "Calma"]},

    {"texto": "La pluma descansa frente al vaso en silencio leve",
     "tipo": "indeterminada", "sujeto": "Pluma", "objeto": "Vaso",
     "relacion": "lateral_superior", "palabras_extra": ["Frente", "Silencio"]},

    {"texto": "La libreta descansa frente al teléfono en calma leve",
     "tipo": "indeterminada", "sujeto": "Libreta", "objeto": "Teléfono",
     "relacion": "lateral_superior", "palabras_extra": ["Frente", "Calma"]},

    # ── Relación: lateral_inferior (cercanía horizontal, fila inferior) ──
    {"texto": "El teléfono acompaña al lápiz desde una zona difusa",
     "tipo": "indeterminada", "sujeto": "Teléfono", "objeto": "Lápiz",
     "relacion": "diagonal_o_lateral", "palabras_extra": ["Zona", "Difuso"]},

    {"texto": "El vaso acompaña al plato desde un lado tranquilo",
     "tipo": "indeterminada", "sujeto": "Vaso", "objeto": "Plato",
     "relacion": "diagonal_o_lateral", "palabras_extra": ["Lado", "Calma"]},

    # ── Relación: indeterminada pura (abstractas/abiertas) ────────────
    {"texto": "La vela ilumina al reloj desde un sitio indefinido",
     "tipo": "indeterminada", "sujeto": "Vela", "objeto": "Reloj",
     "relacion": "indeterminada", "palabras_extra": ["Luz", "Indefinido"]},

    {"texto": "El libro encuentra la taza desde un rincón incierto",
     "tipo": "indeterminada", "sujeto": "Libro", "objeto": "Taza",
     "relacion": "indeterminada", "palabras_extra": ["Rincón", "Incierto"]},

    {"texto": "El cuadro rodea la silla desde un punto difuso",
     "tipo": "indeterminada", "sujeto": "Cuadro", "objeto": "Silla",
     "relacion": "indeterminada", "palabras_extra": ["Punto", "Difuso"]},

    {"texto": "La esperanza cuelga en el horizonte rojo distante",
     "tipo": "indeterminada", "sujeto": "Esperanza", "objeto": "Horizonte",
     "relacion": "indeterminada", "palabras_extra": ["Rojo", "Distancia"]},

    {"texto": "La duda se disuelve en el aire tenue ligero",
     "tipo": "indeterminada", "sujeto": "Duda", "objeto": "Aire",
     "relacion": "indeterminada", "palabras_extra": ["Tenue", "Ligero"]},

    {"texto": "La promesa se eleva sobre el humo gris efímero",
     "tipo": "indeterminada", "sujeto": "Promesa", "objeto": "Humo",
     "relacion": "indeterminada", "palabras_extra": ["Elevación", "Efímero"]},

    {"texto": "El papel vigila la vela desde una esquina oscura",
     "tipo": "indeterminada", "sujeto": "Papel", "objeto": "Vela",
     "relacion": "indeterminada", "palabras_extra": ["Esquina", "Oscuridad"]},

    {"texto": "El violín espía la silla desde un ángulo difuso",
     "tipo": "indeterminada", "sujeto": "Violín", "objeto": "Silla",
     "relacion": "indeterminada", "palabras_extra": ["Ángulo", "Difuso"]},

    {"texto": "La ventana escucha al zapato desde un rincón olvidado",
     "tipo": "indeterminada", "sujeto": "Ventana", "objeto": "Zapato",
     "relacion": "indeterminada", "palabras_extra": ["Rincón", "Olvido"]},

    {"texto": "La campana persigue al pez desde una esquina apagada",
     "tipo": "indeterminada", "sujeto": "Campana", "objeto": "Pez",
     "relacion": "indeterminada", "palabras_extra": ["Esquina", "Silencio"]},
]  # 24 indeterminadas

# Práctica: 2 determinadas + 2 indeterminadas (sin literales)
PRACTICA_TRIALS = [
    {"texto": "La luna está arriba del mar tranquilo y oscuro",
     "tipo": "practica_determinada", "sujeto": "Luna", "objeto": "Mar",
     "relacion": "arriba", "palabras_extra": []},

    {"texto": "El sol brilla sobre la montaña firme y silenciosa",
     "tipo": "practica_determinada", "sujeto": "Sol", "objeto": "Montaña",
     "relacion": "sobre", "palabras_extra": []},

    {"texto": "La lámpara vigila al libro desde una esquina callada",
     "tipo": "practica_indeterminada", "sujeto": "Lámpara", "objeto": "Libro",
     "relacion": "diagonal_opuesta", "palabras_extra": []},

    {"texto": "El reloj observa la silla desde un rincón distante",
     "tipo": "practica_indeterminada", "sujeto": "Reloj", "objeto": "Silla",
     "relacion": "diagonal_o_lateral", "palabras_extra": []},
]

DISTRACTORES = [
    {"texto": "El cuadrado azul está encima del círculo rojo",
     "tipo": "distractor", "sujeto": "Cuadrado", "objeto": "Círculo",
     "relacion": "encima", "palabras_extra": []},

    {"texto": "La silla de madera está a la izquierda de la puerta",
     "tipo": "distractor", "sujeto": "Silla", "objeto": "Puerta",
     "relacion": "izquierda", "palabras_extra": []},

    {"texto": "El vaso de agua descansa sobre el plato blanco",
     "tipo": "distractor", "sujeto": "Vaso", "objeto": "Plato",
     "relacion": "sobre", "palabras_extra": []},

    {"texto": "El libro azul está debajo del cuaderno verde",
     "tipo": "distractor", "sujeto": "Libro", "objeto": "Cuaderno",
     "relacion": "debajo", "palabras_extra": []},
]


# ═══════════════════════════════════════════════════════════════════════
# SISTEMA DE CALIFICACIÓN
# ═══════════════════════════════════════════════════════════════════════

def evaluar_respuesta(trial, resp_participante):
    """
    Evalúa si la respuesta del participante es correcta.

    Parámetros
    ----------
    trial             : dict del estímulo (con campos sujeto, objeto, relacion)
    resp_participante : dict {palabra: cuadrante_int (1-4) o None}

    Retorna
    -------
    total_score         : 100.0 si la config es válida, 0.0 si no
    parcial_score       : % de palabras principales bien colocadas (0-100)
    config_es_valida    : bool
    configuraciones_validas : list de tuplas (q_sujeto, q_objeto)
    """
    configs_validas = obtener_configuraciones_validas(trial["relacion"])

    q_sujeto = resp_participante.get(trial["sujeto"])
    q_objeto  = resp_participante.get(trial["objeto"])

    # Calificación total: la pareja (sujeto, objeto) debe estar en configs_validas
    config_es_valida = (q_sujeto is not None and q_objeto is not None
                        and (q_sujeto, q_objeto) in configs_validas)
    total_score = 100.0 if config_es_valida else 0.0

    # Calificación parcial: cuántas palabras principales están "bien"
    # Una palabra está bien si al menos en alguna config válida ocupa ese cuadrante
    cuadrantes_sujeto_validos = {c[0] for c in configs_validas}
    cuadrantes_objeto_validos  = {c[1] for c in configs_validas}

    sujeto_ok = int(q_sujeto in cuadrantes_sujeto_validos) if q_sujeto is not None else 0
    objeto_ok  = int(q_objeto  in cuadrantes_objeto_validos)  if q_objeto  is not None else 0
    parcial_score = (sujeto_ok + objeto_ok) / 2 * 100

    return total_score, parcial_score, config_es_valida, configs_validas


# ═══════════════════════════════════════════════════════════════════════
# CLASE PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════

class ExperimentoMetaforas:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Representación Mental – Metáforas Espaciales")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)

        self.participante_id    = "001"
        self.resultados         = []
        self.num_ensayo_global  = 0

        # Drag-and-drop state
        self._drag_item     = None
        self._drag_offset_x = 0
        self._drag_offset_y = 0

        self.frame = tk.Frame(self.root, bg=BG_COLOR)
        self.frame.place(x=0, y=0, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)

    # ── Utilidades ────────────────────────────────────────────────────

    def limpiar(self):
        for w in self.frame.winfo_children():
            w.destroy()

    def lbl(self, texto, fuente, color=TEXT_COLOR, rely=0.5, wraplength=920):
        l = tk.Label(self.frame, text=texto, font=fuente,
                     fg=color, bg=BG_COLOR, justify="center",
                     wraplength=wraplength)
        l.place(relx=0.5, rely=rely, anchor="center")
        return l

    # ── Pantalla de inicio ────────────────────────────────────────────

    def pantalla_inicio(self):
        self.limpiar()
        self.root.unbind("<space>")

        self.lbl("Tarea de Representación Mental",
                 ("Helvetica", 22, "bold"), color="#f0e68c", rely=0.28)
        self.lbl("Metáforas Espaciales",
                 ("Helvetica", 15), color="#aaaaaa", rely=0.36)
        self.lbl("ID del participante:", ("Helvetica", 14), rely=0.48)

        var = tk.StringVar(value="001")
        entry = tk.Entry(self.frame, textvariable=var, font=("Helvetica", 16),
                         width=12, justify="center", bg="#16213e", fg=TEXT_COLOR,
                         insertbackground=TEXT_COLOR, relief="solid", bd=1)
        entry.place(relx=0.5, rely=0.56, anchor="center")
        entry.focus_set()

        def iniciar(event=None):
            self.participante_id = var.get().strip() or "001"
            self.pantalla_bienvenida()

        tk.Button(self.frame, text="Comenzar →",
                  font=("Helvetica", 14, "bold"),
                  bg="#f39c12", fg="#1a1a2e", relief="flat",
                  padx=20, pady=8, command=iniciar
                  ).place(relx=0.5, rely=0.67, anchor="center")
        entry.bind("<Return>", iniciar)

    # ── Bienvenida ────────────────────────────────────────────────────

    def pantalla_bienvenida(self):
        self.limpiar()
        self.root.unbind("<space>")
        texto = (
            "Bienvenido/a\n\n"
            "En esta tarea leerás una serie de metáforas.\n"
            "Después de leer cada una, aparecerán palabras que deberás\n"
            "arrastrar y colocar dentro de los cuadrantes de la cuadrícula\n"
            "según la posición espacial que sugiera la metáfora.\n\n"
            "La cuadrícula tiene 4 cuadrantes:\n"
            "  Q1 = Arriba izquierda    Q2 = Arriba derecha\n"
            "  Q3 = Abajo izquierda     Q4 = Abajo derecha\n\n"
            "Puede haber más de una configuración correcta.\n"
            "Coloca las palabras donde creas que la metáfora las ubica.\n\n"
            "Cuando termines, presiona  [✔ Listo]  o\n"
            "si la metáfora no tiene posición espacial clara, presiona\n"
            "[✘ No se puede determinar]\n\n"
            "Primero harás 6 ensayos de práctica con retroalimentación.\n\n"
            "Presiona  ESPACIO  para comenzar."
        )
        self.lbl(texto, ("Helvetica", 13), rely=0.5)
        self.root.bind("<space>", lambda e: self.iniciar_practica())

    # ── Cruz de fijación ──────────────────────────────────────────────

    def pantalla_fijacion(self, callback):
        self.limpiar()
        self.root.unbind("<space>")
        self.lbl("+", ("Helvetica", 60, "bold"))
        self.root.after(FIXATION_DURATION_MS, callback)

    # ── Lectura ───────────────────────────────────────────────────────

    def pantalla_lectura(self, trial, callback):
        self.limpiar()
        self.root.unbind("<space>")
        inicio = time.time()

        self.lbl("Lee la siguiente frase con atención:",
                 ("Helvetica", 13), color="#aaaaaa", rely=0.35)
        self.lbl(trial["texto"], ("Helvetica", 20, "italic"),
                 color="#f0e68c", rely=0.50)
        self.lbl("Presiona ESPACIO para continuar",
                 ("Helvetica", 11), color="#777777", rely=0.65)

        def avanzar(event=None):
            self.root.unbind("<space>")
            callback(time.time() - inicio)

        tid = self.root.after(READING_TIME_MS, avanzar)
        self.root.bind("<space>", lambda e: (self.root.after_cancel(tid), avanzar()))

    # ── Retroalimentación (solo práctica) ─────────────────────────────

    def pantalla_retro(self, config_valida, configs_validas, trial, callback):
        self.limpiar()
        self.root.unbind("<space>")

        if config_valida:
            msg   = "✔  ¡Correcto!\nEsa configuración respeta la relación espacial."
            color = "#2ecc71"
        else:
            ejemplos = ", ".join(
                f"({QUADRANTS[a][:3].upper()} → {QUADRANTS[b][:3].upper()})"
                for a, b in configs_validas[:3]
            )
            msg = (f"✘  No del todo.\n"
                   f"La relación es '{trial['relacion']}'. "
                   f"Algunos ejemplos válidos: {ejemplos}…")
            color = "#e74c3c"

        self.lbl(msg, ("Helvetica", 15, "bold"), color=color, rely=0.45)
        self.root.after(2200, callback)

    # ── TAREA (drag-and-drop) ─────────────────────────────────────────

    def pantalla_tarea(self, trial, rt_lectura, callback):
        self.limpiar()
        self.root.unbind("<space>")
        inicio_tarea = time.time()

        # Solo 2 palabras arrastrables: sujeto y objeto.
        # La diferencia entre tipos de metáfora está en las configs válidas,
        # no en el número de palabras presentadas.
        palabras = [trial["sujeto"], trial["objeto"]]
        random.shuffle(palabras)

        word_positions = {p: None for p in palabras}

        # ── Layout ────────────────────────────────────────────────────
        GRID_SIZE = 340
        GRID_X    = (WINDOW_WIDTH - GRID_SIZE) // 2
        GRID_Y    = 145
        HALF      = GRID_SIZE // 2

        qb = {
            1: (GRID_X,        GRID_Y,        GRID_X + HALF,      GRID_Y + HALF),
            2: (GRID_X + HALF, GRID_Y,        GRID_X + GRID_SIZE, GRID_Y + HALF),
            3: (GRID_X,        GRID_Y + HALF, GRID_X + HALF,      GRID_Y + GRID_SIZE),
            4: (GRID_X + HALF, GRID_Y + HALF, GRID_X + GRID_SIZE, GRID_Y + GRID_SIZE),
        }

        # ── Canvas base ───────────────────────────────────────────────
        c = tk.Canvas(self.frame, width=WINDOW_WIDTH, height=WINDOW_HEIGHT,
                      bg=BG_COLOR, highlightthickness=0)
        c.place(x=0, y=0)

        # Texto metáfora
        c.create_text(WINDOW_WIDTH // 2, 72,
                      text=trial["texto"],
                      font=("Helvetica", 17, "italic"),
                      fill="#f0e68c", width=880, justify="center")

        # Cuadrícula
        c.create_rectangle(GRID_X, GRID_Y,
                           GRID_X + GRID_SIZE, GRID_Y + GRID_SIZE,
                           outline=GRID_COLOR, width=2)
        c.create_line(GRID_X + HALF, GRID_Y,
                      GRID_X + HALF, GRID_Y + GRID_SIZE,
                      fill=GRID_COLOR, width=2)
        c.create_line(GRID_X, GRID_Y + HALF,
                      GRID_X + GRID_SIZE, GRID_Y + HALF,
                      fill=GRID_COLOR, width=2)

        # Etiquetas y flechas de orientación
        labels = {1: "Q1\n▲ Arr. Izq.", 2: "Q2\n▲ Arr. Der.",
                  3: "Q3\n▼ Abj. Izq.", 4: "Q4\n▼ Abj. Der."}
        for q, (x1, y1, x2, y2) in qb.items():
            c.create_text((x1 + x2) // 2, y1 + 22,
                          text=labels[q], font=("Helvetica", 10),
                          fill="#888888", justify="center")

        # Zona de palabras
        WORD_Y = GRID_Y + GRID_SIZE + 52
        total_w = len(palabras) * 130
        sx = (WINDOW_WIDTH - total_w) // 2 + 65
        c.create_text(WINDOW_WIDTH // 2, WORD_Y - 22,
                      text="Arrastra cada palabra al cuadrante que corresponda",
                      font=("Helvetica", 11), fill="#888888")

        for i, p in enumerate(palabras):
            wx = sx + i * 130
            lbl_w = tk.Label(self.frame, text=p,
                             font=("Helvetica", 13, "bold"),
                             fg=TEXT_COLOR, bg="#0f3460",
                             relief="raised", padx=8, pady=5,
                             cursor="hand2")
            lbl_w.place(x=wx - 45, y=WORD_Y)
            lbl_w._palabra = p
            lbl_w._orig_x  = wx - 45
            lbl_w._orig_y  = WORD_Y

            lbl_w.bind("<ButtonPress-1>",   lambda e, w=lbl_w: self._drag_start(e, w))
            lbl_w.bind("<B1-Motion>",       lambda e, w=lbl_w: self._drag_move(e, w))
            lbl_w.bind("<ButtonRelease-1>",
                       lambda e, w=lbl_w, bounds=qb, wp=word_positions:
                       self._drag_drop(e, w, bounds, wp))

        # Botones
        def confirmar(boton):
            rt_inf = time.time() - inicio_tarea
            total_s, parcial_s, config_ok, configs_val = evaluar_respuesta(
                trial, word_positions)

            resultado = {
                "participante":             self.participante_id,
                "tipo_metafora":            trial["tipo"],
                "texto_metafora":           trial["texto"],
                "relacion":                 trial["relacion"],
                "sujeto":                   trial["sujeto"],
                "objeto":                   trial["objeto"],
                "palabras_presentadas":     "|".join(palabras),
                "q_sujeto_participante":    word_positions.get(trial["sujeto"]),
                "q_objeto_participante":    word_positions.get(trial["objeto"]),
                "config_valida":            config_ok,
                "configs_validas":          str(configs_val),
                "total_score":              round(total_s, 2),
                "parcial_score":            round(parcial_s, 2),
                "respuesta_boton":          boton,
                "rt_lectura_s":             round(rt_lectura, 4),
                "rt_inferencia_s":          round(rt_inf, 4),
                "fecha_hora":               datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            callback(resultado)

        btn_listo = tk.Button(self.frame, text="✔ Listo",
                  font=("Helvetica", 13, "bold"),
                  bg="#00d2a0", fg="#0a0a1a", relief="raised", bd=2,
                  padx=20, pady=8,
                  command=lambda: confirmar("Listo"))
        btn_listo.place(x=WINDOW_WIDTH - 210, y=WINDOW_HEIGHT - 72)
        btn_listo.lift()

        btn_no = tk.Button(self.frame, text="✘ No se puede determinar",
                  font=("Helvetica", 12, "bold"),
                  bg="#f1c40f", fg="#1a1a2e", relief="raised", bd=2,
                  padx=12, pady=8,
                  command=lambda: confirmar("No se puede determinar"))
        btn_no.place(x=40, y=WINDOW_HEIGHT - 72)
        btn_no.lift()

    # ── Drag-and-drop ─────────────────────────────────────────────────

    def _drag_start(self, event, w):
        self._drag_item     = w
        self._drag_offset_x = event.x
        self._drag_offset_y = event.y
        w.lift()

    def _drag_move(self, event, w):
        if self._drag_item is w:
            w.place(x=w.winfo_x() + event.x - self._drag_offset_x,
                    y=w.winfo_y() + event.y - self._drag_offset_y)

    def _drag_drop(self, event, w, qb, wp):
        if self._drag_item is not w:
            return
        cx = w.winfo_x() + w.winfo_width()  // 2
        cy = w.winfo_y() + w.winfo_height() // 2
        snapped = False
        for q, (x1, y1, x2, y2) in qb.items():
            if x1 <= cx <= x2 and y1 <= cy <= y2:
                w.place(x=x1 + (x2-x1)//2 - w.winfo_width()//2,
                        y=y1 + (y2-y1)//2 - w.winfo_height()//2)
                wp[w._palabra] = q
                snapped = True
                break
        if not snapped:
            w.place(x=w._orig_x, y=w._orig_y)
            wp[w._palabra] = None
        self._drag_item = None

    # ── Práctica ──────────────────────────────────────────────────────

    def iniciar_practica(self):
        self.root.unbind("<space>")
        self._p_trials = PRACTICA_TRIALS[:]
        random.shuffle(self._p_trials)
        self._p_res = []
        self._p_idx = 0
        self._practica_siguiente()

    def _practica_siguiente(self):
        if self._p_idx >= len(self._p_trials):
            self._practica_evaluar()
            return
        t = self._p_trials[self._p_idx]
        self.pantalla_fijacion(lambda: self.pantalla_lectura(
            t, lambda rt: self.pantalla_tarea(
                t, rt, lambda res: self._practica_post(res))))

    def _practica_post(self, res):
        self._p_res.append(res)
        self._p_idx += 1
        self.pantalla_retro(
            res["config_valida"],
            obtener_configuraciones_validas(self._p_trials[self._p_idx - 1]["relacion"]),
            self._p_trials[self._p_idx - 1],
            self._practica_siguiente
        )

    def _practica_evaluar(self):
        ok = sum(1 for r in self._p_res if r["config_valida"])
        if ok / len(self._p_res) >= PRACTICE_PASS_THRESHOLD:
            self.limpiar()
            self.lbl("¡Excelente! Superaste la práctica.\n\nPresiona ESPACIO para comenzar.",
                     ("Helvetica", 18), color="#2ecc71")
            self.root.bind("<space>", lambda e: self.iniciar_experimento())
        else:
            self.limpiar()
            self.lbl("Necesitas ≥75% para continuar.\nPresiona ESPACIO para repetir.",
                     ("Helvetica", 18), color="#e74c3c")
            self.root.bind("<space>", lambda e: self.iniciar_practica())

    # ── Bloque experimental ───────────────────────────────────────────

    def iniciar_experimento(self):
        self.root.unbind("<space>")
        if PILOT_MODE and not FULL_TASK_MODE:
            det   = random.sample(METAFORAS_DETERMINADAS,   PILOT_TRIALS)
            indet = random.sample(METAFORAS_INDETERMINADAS, PILOT_TRIALS)
            self._exp_trials = det + indet
            random.shuffle(self._exp_trials)
        else:
            self._exp_trials = (METAFORAS_DETERMINADAS
                                + METAFORAS_INDETERMINADAS
                                + DISTRACTORES)
            random.shuffle(self._exp_trials)
        self._exp_idx = 0
        self._exp_siguiente()

    def _exp_siguiente(self):
        if self._exp_idx >= len(self._exp_trials):
            self._guardar()
            self._pantalla_cierre()
            return
        t = self._exp_trials[self._exp_idx]
        self.pantalla_fijacion(lambda: self.pantalla_lectura(
            t, lambda rt: self.pantalla_tarea(
                t, rt, lambda res: self._exp_registrar(res))))

    def _exp_registrar(self, res):
        self.num_ensayo_global += 1
        res["num_ensayo"] = self.num_ensayo_global
        self.resultados.append(res)
        self._exp_idx += 1
        self.limpiar()
        self.root.after(ITI_MS, self._exp_siguiente)

    # ── Cierre ────────────────────────────────────────────────────────

    def _pantalla_cierre(self):
        self.limpiar()
        self.root.unbind("<space>")
        self.lbl("¡Has terminado!\n\nMuchas gracias por tu participación.\nTus datos han sido guardados.",
                 ("Helvetica", 22), rely=0.42)
        tk.Button(self.frame, text="Salir",
                  font=("Helvetica", 14, "bold"),
                  bg="#e84393", fg="white", relief="flat",
                  padx=20, pady=8, command=self.root.destroy
                  ).place(relx=0.5, rely=0.65, anchor="center")

    # ── Guardado CSV ──────────────────────────────────────────────────

    def _guardar(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(base_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        ts  = datetime.now().strftime("%Y%m%d_%H%M%S")
        fn  = os.path.join(data_dir, f"{self.participante_id}_Metaforas_Espaciales_{ts}.csv")
        cols = [
            "participante", "num_ensayo", "tipo_metafora", "texto_metafora",
            "relacion", "sujeto", "objeto", "palabras_presentadas",
            "q_sujeto_participante", "q_objeto_participante",
            "config_valida", "configs_validas",
            "total_score", "parcial_score",
            "respuesta_boton", "rt_lectura_s", "rt_inferencia_s", "fecha_hora",
        ]
        with open(fn, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            for r in self.resultados:
                w.writerow({c: r.get(c, "") for c in cols})
        print(f"[INFO] Datos guardados: {fn}")

    # ── Run ───────────────────────────────────────────────────────────

    def run(self):
        self.pantalla_inicio()
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.after(200, lambda: self.root.attributes("-topmost", False))
        self.root.focus_force()
        self.root.mainloop()


if __name__ == "__main__":
    ExperimentoMetaforas().run()
