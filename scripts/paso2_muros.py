"""
PASO 2 — Vectorizar los muros.
Se separan los píxeles rojos (fondo de patio) y cian (zona casa) y cada uno se
convierte en polilíneas.
Salida: intermedios/ramas.json  [{zona, pts}]
"""
import json
import cv2
from config import PLANO_PNG, INTERMEDIOS, COLOR_CASA, COLOR_PATIO
from esqueleto import mascara_color, ramas

hsv = cv2.cvtColor(cv2.imread(str(PLANO_PNG)), cv2.COLOR_BGR2HSV)
salida = []
for zona, cfg in (("patio", COLOR_PATIO), ("casa", COLOR_CASA)):
    for p in ramas(mascara_color(hsv, **cfg)):
        salida.append(dict(zona=zona, pts=p))
json.dump(salida, open(INTERMEDIOS / "ramas.json", "w"))
print(f"Paso 2 listo: {len(salida)} ramas de muro")
