"""
PASO 5 — Armar el dashboard.
Inserta el texto del DXF dentro de la plantilla HTML. El HTML resultante es un
solo archivo autosuficiente: trae el plano y guarda el avance en sí mismo.
Si ya existe un dashboard con avance registrado, se conserva ese avance.
"""
import json
import re
from config import DXF_SALIDA, DASHBOARD, PLANTILLA

datos = {"dxf": DXF_SALIDA.read_text(), "estado": {}, "guardado": 0}
if DASHBOARD.exists():  # conservar el avance ya marcado
    m = re.search(r'<script id="datos" type="application/json">(.*?)</script>', DASHBOARD.read_text(), re.S)
    if m:
        previo = json.loads(m.group(1))
        datos["estado"], datos["guardado"] = previo.get("estado", {}), previo.get("guardado", 0)

json_seguro = json.dumps(datos).replace("<", "\\u003c")   # evita cerrar el <script> por accidente
DASHBOARD.write_text(PLANTILLA.read_text().replace("__DATOS__", json_seguro))
print(f"Paso 5 listo: {DASHBOARD.name} ({len(datos['estado'])} tramos con avance conservado)")
