"""
PASO 1 — Regiones de cada sitio.
Las líneas oscuras (deslindes) y los muros de color se usan como "paredes"; el
espacio libre que queda se separa en regiones cerradas. La región que contiene
el rótulo "SITIO N" es el sitio N.
Salida: intermedios/regiones.npy (mapa de regiones) y intermedios/sitio_region.json
"""
import json
import cv2
import numpy as np
from config import PLANO_PNG, INTERMEDIOS, SITIOS

INTERMEDIOS.mkdir(exist_ok=True)
img = cv2.imread(str(PLANO_PNG))
H, S, V = cv2.split(cv2.cvtColor(img, cv2.COLOR_BGR2HSV))
azul = (H >= 108) & (H <= 132) & (S > 80)            # textos y edificios (no son barrera)
oscuro = (V < 140) & ~azul                            # deslindes
color = (S > 100) & (V > 100) & ~azul                 # muros y límites de color
barrera = cv2.dilate((oscuro | color).astype(np.uint8), np.ones((7, 7), np.uint8))
_, regiones = cv2.connectedComponents((1 - barrera).astype(np.uint8), connectivity=4)
np.save(INTERMEDIOS / "regiones.npy", regiones)

sitio_region, usadas = {}, {}
for n, (x, y, _) in SITIOS.items():
    ventana = regiones[y - 40:y + 40, x - 80:x + 80]
    vals, cuenta = np.unique(ventana[ventana > 0], return_counts=True)
    r = int(vals[cuenta.argmax()])
    sitio_region[n] = r
    usadas.setdefault(r, []).append(n)
for r, ns in usadas.items():
    if len(ns) > 1:
        print("ATENCIÓN: sitios en la misma región (revisar posición del rótulo):", ns)
json.dump(sitio_region, open(INTERMEDIOS / "sitio_region.json", "w"))
print(f"Paso 1 listo: {len(usadas)} regiones de sitio")
