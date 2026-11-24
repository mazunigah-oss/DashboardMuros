"""
Herramienta común: convierte una máscara de píxeles (una línea dibujada de cierto
color) en polilíneas vectoriales.

Método: se adelgaza la línea a 1 px (esqueleto), se cortan las bifurcaciones y
cada rama se recorre de punta a punta y se simplifica (Douglas-Peucker).
"""
import cv2
import numpy as np
from skimage.morphology import skeletonize

VECINOS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


def mascara_color(hsv, h, s_min, v_min):
    """Píxeles cuyo tono está en alguno de los rangos h=[(min,max),...]."""
    H, S, V = cv2.split(hsv)
    m = np.zeros(H.shape, bool)
    for a, b in h:
        m |= (H >= a) & (H <= b)
    return m & (S > s_min) & (V > v_min)


def ramas(mascara, tolerancia=5):
    """Devuelve una lista de polilíneas [[x,y],...] en píxeles."""
    m = cv2.morphologyEx(mascara.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    esq = skeletonize(m > 0).astype(np.uint8)
    n_vec = cv2.filter2D(esq, -1, np.ones((3, 3)), borderType=0) - 1
    juntas = cv2.dilate(((esq == 1) & (n_vec > 2)).astype(np.uint8), np.ones((3, 3), np.uint8))
    sin_juntas = esq & (1 - juntas)
    n, etiquetas = cv2.connectedComponents(sin_juntas, connectivity=8)
    _, etq_j, _, centros_j = cv2.connectedComponentsWithStats(juntas, connectivity=8)

    salida = []
    for i in range(1, n):
        ys, xs = np.where(etiquetas == i)
        if len(xs) < 8:
            continue
        pts = set(zip(xs.tolist(), ys.tolist()))
        puntas = [p for p in pts if sum((p[0] + dx, p[1] + dy) in pts for dx, dy in VECINOS) <= 1] or [next(iter(pts))]
        # recorrer la rama desde una punta
        camino, visto = [puntas[0]], {puntas[0]}
        while True:
            c = camino[-1]
            sig = [(c[0] + dx, c[1] + dy) for dx, dy in VECINOS
                   if (c[0] + dx, c[1] + dy) in pts and (c[0] + dx, c[1] + dy) not in visto]
            if not sig:
                break
            camino.append(sig[0]); visto.add(sig[0])
        # prolongar los extremos hasta la bifurcación vecina (para que no queden huecos)
        for idx in (0, -1):
            x0, y0 = camino[idx]
            ventana = etq_j[max(0, y0 - 3):y0 + 4, max(0, x0 - 3):x0 + 4]
            js = set(ventana[ventana > 0].ravel())
            if js:
                c = centros_j[min(js)]
                q = (int(round(c[0])), int(round(c[1])))
                camino.insert(0, q) if idx == 0 else camino.append(q)
        simpl = cv2.approxPolyDP(np.array(camino, np.int32).reshape(-1, 1, 2), tolerancia, False)
        salida.append(simpl.reshape(-1, 2).tolist())
    return salida


def largo(poli):
    P = np.array(poli, float)
    return float(np.hypot(*np.diff(P, axis=0).T).sum()) if len(P) > 1 else 0.0
