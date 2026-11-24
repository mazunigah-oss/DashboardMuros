"""
PASO 3 — Asignar cada trozo de muro a los sitios que separa y agrupar en tramos.

1. Cada rama se recorre cada ~20 px; en cada punto se mira a ambos lados
   (perpendicular a la línea) qué sitio hay. Así un muro entre los sitios 8 y 12
   queda con la clave (8, 12). Si a un lado hay calle, la clave tiene un solo sitio.
2. Si la clave cambia a lo largo de una rama (p. ej. un muro trasero que pasa
   por detrás de varios sitios), la rama se corta en ese punto.
3. Los trozos cortos (retornos, ganchos en planta) se unen al muro vecino.
4. Se aplican las CORRECCIONES manuales de config.py.
Tramo = muro × zona (casa / patio).
Salida: intermedios/tramos.json y revision/control_tramos.jpg
"""
import json
from collections import defaultdict
import cv2
import numpy as np
from config import INTERMEDIOS, REVISION, PLANO_PNG, SITIOS, CORRECCIONES
from esqueleto import largo

regiones = np.load(INTERMEDIOS / "regiones.npy")
region_sitio = {r: int(n) for n, r in json.load(open(INTERMEDIOS / "sitio_region.json")).items()}
ALTO, ANCHO = regiones.shape
ramas = json.load(open(INTERMEDIOS / "ramas.json"))


def sitio_al_lado(p, normal, signo):
    """Primer sitio que se encuentra avanzando perpendicular a la línea (hasta 175 px)."""
    for d in range(25, 175, 10):
        q = (p + signo * d * normal).astype(int)
        if not (0 <= q[0] < ANCHO and 0 <= q[1] < ALTO):
            return None
        r = int(regiones[q[1], q[0]])
        if r in region_sitio:
            return region_sitio[r]
    return None


# 1-2. Clasificar puntos y cortar ramas donde cambia la clave
trozos = []
for rama in ramas:
    P = np.array(rama["pts"], float)
    puntos, claves = [], []
    for a, b in zip(P[:-1], P[1:]):
        d = b - a
        ln = np.hypot(*d)
        if ln < 1:
            continue
        normal = np.array([-d[1], d[0]]) / ln
        n = max(1, int(ln / 20))
        for t in np.arange(n) / n:
            p = a + t * d
            lados = {sitio_al_lado(p, normal, 1), sitio_al_lado(p, normal, -1)} - {None}
            puntos.append(p); claves.append(tuple(sorted(lados)))
    if not claves:
        continue
    puntos.append(P[-1]); claves.append(claves[-1])
    claves = [max(set(v), key=v.count) for v in (claves[max(0, i - 3):i + 4] for i in range(len(claves)))]  # suavizado
    ini = 0
    for i in range(1, len(claves) + 1):
        if i == len(claves) or claves[i] != claves[ini]:
            corrida = np.array(puntos[ini:min(i + 1, len(puntos))], np.float32)
            if len(corrida) >= 2:
                s = cv2.approxPolyDP(corrida.reshape(-1, 1, 2), 5, False).reshape(-1, 2)
                trozos.append(dict(zona=rama["zona"], pts=s.tolist(), clave=list(claves[ini])))
            ini = i
for t in trozos:
    t["largo"] = largo(t["pts"])


# 3. Unir trozos cortos / retornos al muro vecino
def dist_punto(x, B):
    mejor = 1e9
    for a, b in zip(B[:-1], B[1:]):
        d = b - a
        t = np.clip(np.dot(x - a, d) / max(np.dot(d, d), 1e-9), 0, 1)
        mejor = min(mejor, np.hypot(*(a + t * d - x)))
    return mejor


def dist_extremos(p, q):
    B = np.array(q["pts"], float)
    return min(dist_punto(np.array(p["pts"][i], float), B) for i in (0, -1))


def colineal(p, q):
    """|cos| del ángulo entre el extremo de p que toca q y el segmento de q más cercano."""
    B = np.array(q["pts"], float)
    i, j = min(((0, 1), (-1, -2)), key=lambda ij: dist_punto(np.array(p["pts"][ij[0]], float), B))
    x = np.array(p["pts"][i], float); v = np.array(p["pts"][j], float) - x
    k = min(range(len(B) - 1), key=lambda k: dist_punto(x, B[k:k + 2])); w = B[k + 1] - B[k]
    return abs(np.dot(v, w)) / (np.hypot(*v) * np.hypot(*w) + 1e-9)


cambio = True
while cambio:
    cambio = False
    total = defaultdict(float)
    for t in trozos:
        total[(tuple(t["clave"]), t["zona"])] += t["largo"]
    for p in trozos:
        kp = (tuple(p["clave"]), p["zona"])
        for q in sorted(trozos, key=lambda q: dist_extremos(p, q) if q is not p else 1e9):
            if q is p or q["clave"] == p["clave"]:
                continue
            if dist_extremos(p, q) > 30:
                break
            kq = (tuple(q["clave"]), q["zona"])
            if total[kq] < 200 or not q["clave"]:
                continue
            contenido = set(p["clave"]) <= set(q["clave"])
            corto_misma_zona = q["zona"] == p["zona"] and total[kp] < 200 and \
                ((contenido and len(q["clave"]) == 2) or not p["clave"])
            prolongacion = contenido and len(p["clave"]) < 2 and len(q["clave"]) == 2 and colineal(p, q) > 0.94
            if corto_misma_zona or prolongacion:
                p["clave"] = q["clave"]; cambio = True
                break
        if cambio:
            break

# 4. Correcciones manuales y limpieza
trozos = [t for t in trozos if t["largo"] >= 15]
for t in trozos:
    t["clave"] = list(CORRECCIONES.get(tuple(t["clave"]), tuple(t["clave"])))
json.dump(trozos, open(INTERMEDIOS / "tramos.json", "w"))

muros = defaultdict(dict)
for t in trozos:
    muros[tuple(t["clave"])][t["zona"]] = muros[tuple(t["clave"])].get(t["zona"], 0) + t["largo"]
print(f"Paso 3 listo: {len(muros)} muros, {sum(len(z) for z in muros.values())} tramos")

# Imagen de control: cada tramo con su nombre
REVISION.mkdir(exist_ok=True)
img = (cv2.imread(str(PLANO_PNG)) * 0.35 + 255 * 0.65).astype(np.uint8)
mayor = {}
for t in trozos:
    k = (tuple(t["clave"]), t["zona"])
    col = tuple(int(c) for c in np.random.RandomState(abs(hash(str(k))) % 2**31).randint(0, 200, 3))
    cv2.polylines(img, [np.array(t["pts"], np.int32)], False, col, 14)
    if k not in mayor or t["largo"] > mayor[k]["largo"]:
        mayor[k] = t
for k, t in mayor.items():
    P = np.array(t["pts"], int); m = (P[0] + P[-1]) // 2
    nombre = "-".join(map(str, k[0])) + ("/C" if k[1] == "casa" else "/P")
    cv2.putText(img, nombre, (int(m[0]) + 12, int(m[1])), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 0), 4)
cv2.imwrite(str(REVISION / "control_tramos.jpg"), img, [cv2.IMWRITE_JPEG_QUALITY, 80])
