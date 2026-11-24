"""
PASO 4 — Escribir el DXF.
Capas:
  M_<muro>_CASA / M_<muro>_PATIO  -> un tramo de muro por capa (ej. M_08-12_CASA)
  BASE_DESLINDES, BASE_LIMITE, BASE_EDIFICIOS, TEXTO_SITIOS -> plano de fondo
El dashboard reconoce los tramos SOLO por el nombre de la capa; para corregir un
tramo basta con cambiarlo de capa en AutoCAD.
"""
import json
import os
import pickle
import cv2
import ezdxf
import numpy as np
from ezdxf.enums import TextEntityAlignment
from config import PLANO_PNG, DXF_SALIDA, INTERMEDIOS, ESCALA, SITIOS
from esqueleto import ramas, largo

img = cv2.imread(str(PLANO_PNG))
ALTO = img.shape[0]
H, S, V = cv2.split(cv2.cvtColor(img, cv2.COLOR_BGR2HSV))
azul = (H >= 108) & (H <= 132) & (S > 80)


def xy(p):  # píxel -> coordenada DXF (el eje Y de la imagen va hacia abajo)
    return round(p[0] * ESCALA, 3), round((ALTO - p[1]) * ESCALA, 3)


doc = ezdxf.new("R2010", setup=True)
doc.units = ezdxf.units.M
msp = doc.modelspace()


def capa(nombre, color, tipo="Continuous"):
    if nombre not in doc.layers:
        doc.layers.add(nombre, color=color, linetype=tipo)


capa("BASE_DESLINDES", 8); capa("BASE_LIMITE", 6); capa("BASE_EDIFICIOS", 5); capa("TEXTO_SITIOS", 7)

# Fondo: deslindes (líneas oscuras) y límite (magenta). El esqueleto de los
# deslindes es lento (~5 min), por eso se guarda en caché.
fondos = (("BASE_DESLINDES", (V < 140) & ~azul),
          ("BASE_LIMITE", (H >= 140) & (H <= 160) & (S > 120) & (V > 220)))
for nombre, mascara in fondos:
    cache = INTERMEDIOS / f"cache_{nombre}.pkl"
    if os.path.exists(cache):
        polis = pickle.load(open(cache, "rb"))
    else:
        polis = ramas(mascara); pickle.dump(polis, open(cache, "wb"))
    for p in polis:
        if largo(p) >= 25:
            msp.add_lwpolyline([xy(q) for q in p], dxfattribs={"layer": nombre})

# Edificios: contornos azules grandes
cerrado = cv2.morphologyEx(azul.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8))
for c in cv2.findContours(cerrado, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]:
    if max(cv2.boundingRect(c)[2:]) > 600:
        msp.add_lwpolyline([xy(q) for q in cv2.boxPoints(cv2.minAreaRect(c))], close=True,
                           dxfattribs={"layer": "BASE_EDIFICIOS"})

# Rótulos de sitio
for n, (x, y, tipo) in SITIOS.items():
    msp.add_text(f"SITIO {n}", height=0.55, dxfattribs={"layer": "TEXTO_SITIOS"}) \
        .set_placement(xy((x - 150, y)), align=TextEntityAlignment.MIDDLE_CENTER)
    msp.add_text(tipo, height=0.45, dxfattribs={"layer": "TEXTO_SITIOS"}) \
        .set_placement(xy((x - 150, y + 75)), align=TextEntityAlignment.MIDDLE_CENTER)

# Muros: una capa por tramo
for t in json.load(open(INTERMEDIOS / "tramos.json")):
    muro = "-".join(f"{n:02d}" for n in t["clave"])
    nombre = f"M_{muro}_{t['zona'].upper()}"
    capa(nombre, 4 if t["zona"] == "casa" else 1, "Continuous" if t["zona"] == "casa" else "DASHED")
    msp.add_lwpolyline([xy(q) for q in t["pts"]], dxfattribs={"layer": nombre})

doc.saveas(DXF_SALIDA)
n_tramos = len([l for l in doc.layers if l.dxf.name.startswith("M_")])
print(f"Paso 4 listo: {DXF_SALIDA.name} ({n_tramos} tramos)")
