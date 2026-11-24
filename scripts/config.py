"""
Configuración del proyecto. Es el ÚNICO archivo que hay que editar para adaptar
el proceso a otro plano u otra obra.
"""
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent          # carpeta de entrega
PLANO_PNG = RAIZ / "plano" / "plano_original.jpg"        # plano de entrada (imagen)
DXF_SALIDA = RAIZ / "plano" / "muros_loma_la_cruz.dxf"   # DXF generado
DASHBOARD = RAIZ / "dashboard_muros.html"                # dashboard generado
PLANTILLA = RAIZ / "codigo" / "plantilla_dashboard.html"
INTERMEDIOS = RAIZ / "codigo" / "intermedios"            # archivos de trabajo entre pasos
REVISION = RAIZ / "revision"                             # imágenes de control visual

# Escala del DXF: 1 píxel de la imagen = ESCALA unidades de dibujo.
# El PNG no trae escala real; para tener metros, escalar el DXF en CAD con una cota conocida.
ESCALA = 0.01

# Colores de los muros en el plano (espacio HSV de OpenCV: H 0-179, S y V 0-255)
#   rojo  -> fondo de patio      cian -> zona casa
COLOR_PATIO = dict(h=[(0, 10), (172, 179)], s_min=110, v_min=110)
COLOR_CASA = dict(h=[(84, 100)], s_min=110, v_min=110)

# Posición (px en la imagen original) del rótulo de cada sitio y su tipología.
# Se usa para saber a qué sitio pertenece cada región del plano.
SITIOS = {
    1: (4770, 3285, 'C1'), 2: (4710, 2995, 'A1'), 3: (4340, 2475, 'C2'), 4: (4010, 2190, 'B1'),
    5: (3725, 1945, 'C3'), 6: (3300, 1880, 'C4'), 7: (2970, 1810, 'C5'), 8: (2655, 1710, 'C6'),
    9: (2425, 2530, 'B2'), 10: (2270, 2825, 'C7'), 11: (2105, 3170, 'A2'), 12: (1850, 1225, 'C8'),
    13: (1780, 1578, 'C9'), 14: (1695, 1945, 'B3'), 15: (1580, 2320, 'B4'), 16: (1365, 2670, 'B5'),
    17: (900, 2770, 'B6'), 18: (975, 3500, 'A3'), 19: (1085, 3870, 'A4'), 20: (1260, 4190, 'A5'),
    21: (1435, 4690, 'A6'), 22: (1690, 5085, 'A7'), 23: (1915, 5470, 'A8'), 24: (2135, 5895, 'A9'),
    25: (3090, 5490, 'B7'), 26: (2550, 6210, 'B8'), 27: (2995, 6430, 'B9'), 28: (3375, 6575, 'B10'),
    29: (3775, 6730, 'B11'), 30: (4200, 6810, 'A10'), 31: (4720, 6690, 'B12'), 32: (5110, 6690, 'B13'),
    33: (5060, 5820, 'C10'), 34: (5030, 5470, 'C11'), 35: (5030, 5140, 'C12'), 36: (5030, 4770, 'C13'),
    37: (3290, 5760, 'C14'), 38: (3690, 5800, 'B14'), 39: (4200, 5850, 'A11'), 40: (2080, 3735, 'A12'),
    41: (2225, 4270, 'B15'), 42: (2500, 4620, 'C15'), 43: (2685, 4930, 'C16'), 44: (3380, 5030, 'C17'),
    45: (3745, 5040, 'B16'), 46: (4130, 4995, 'A13'), 47: (4815, 4505, 'B17'), 48: (5160, 4340, 'B18'),
}

# Correcciones manuales hechas tras revisar visualmente la detección automática
# (muro detectado -> muro correcto). Un muro se identifica por los sitios que separa.
CORRECCIONES = {
    (37, 45): (45,),     # trozo mínimo detrás del sitio 45
    (8, 13): (8, 12),    # muro poniente del sitio 8 (da al pasaje)
    (8, 14): (8, 12),
    (16, 18): (16, 17),  # continuación del muro 16-17
    (31, 33): (32, 33),  # continuación del muro 32-33 sobre la calle
    (2,): (1, 2),        # retorno del muro 1-2
    (4,): (3, 4),        # muro entre sitios 3 y 4 (desplazado del deslinde)
}
