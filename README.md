# Dashboard de avance — Muros de contención · Loma La Cruz Norte

Constructora Bravo Izquierdo · Práctica profesional (Oficina Técnica)

Sistema para registrar y visualizar sobre el plano el avance de los muros de contención,
**tramo por tramo**. Cada muro de deslinde se divide en **zona casa** (hasta donde termina la terraza)
y **fondo de patio** (el resto).

---

## 1. Contenido de la carpeta

```
Dashboard_Muros_Loma_La_Cruz/
├── dashboard_muros.html        ← EL DASHBOARD (abrir con doble clic en Chrome/Edge)
├── README.md                   ← este documento
├── plano/
│   ├── plano_original.jpg      ← plano de muros entregado (imagen, entrada del proceso)
│   ├── leyenda_categorias.png  ← categorías de avance definidas
│   └── muros_loma_la_cruz.dxf  ← plano vectorizado (geometría de muros por capas)
├── codigo/                     ← código Python que genera el DXF y el dashboard
│   ├── config.py               ← ÚNICO archivo a editar para otro proyecto
│   ├── esqueleto.py            ← herramienta: imagen de una línea → polilínea
│   ├── paso1_regiones.py       ← detecta la región de cada sitio
│   ├── paso2_muros.py          ← vectoriza los muros rojos y cian
│   ├── paso3_agrupar.py        ← asigna cada trozo a sus sitios y arma los tramos
│   ├── paso4_dxf.py            ← escribe el DXF
│   ├── paso5_dashboard.py      ← inserta el DXF dentro del HTML
│   ├── ejecutar_todo.py        ← corre los 5 pasos en orden
│   ├── plantilla_dashboard.html← código del dashboard (HTML + JavaScript)
│   └── requirements.txt
└── revision/
    ├── control_tramos.jpg      ← plano con el nombre de cada tramo detectado (para revisar)
    └── captura_dashboard.png
```

---

## 2. Uso del dashboard (día a día)

1. Abrir `dashboard_muros.html` en **Chrome o Edge** (no requiere internet ni instalar nada).
2. **Clic** sobre un tramo para seleccionarlo (**Shift + clic** para varios). También se puede hacer
   clic en un sitio de la tabla *Por sitio* para seleccionar todos sus tramos.
3. Elegir el estado en **Marcar estado**. Queda registrada la fecha del cambio.
4. **💾 Guardar en el HTML**: escribe el avance dentro del mismo archivo. En Chrome/Edge se puede
   elegir el mismo archivo y sobrescribirlo; en otros navegadores se descarga una copia con fecha.
   Además, cada cambio se respalda automáticamente en el navegador.
5. Exportar:
   - **📄 Reporte CSV** — tabla por tramo (separador `;`, se abre directo en Excel).
   - **🖼 Plano PNG** — plano coloreado por estado con leyenda, fecha y % de avance.
6. Rueda del mouse = zoom · arrastrar = mover el plano · pasar el mouse sobre un tramo = detalle.

### Estados y ponderación

| Estado | Color | Avance ponderado |
|---|---|---|
| Sin iniciar | gris | 0 % |
| Excavación | amarillo | 40 % |
| Emplantillado | verde limón | 42 % |
| Zapata + enfierradura | verde | 57 % |
| Hormigón MC + moldaje | verde agua | 77 % |
| Impermeabilización | celeste | 100 % |
| Relleno | azul | 100 % |

El **% de avance global** es el promedio de la ponderación de cada tramo, pesado por su largo.
Línea continua = zona casa · línea segmentada = fondo de patio.

### Regla de asignación a sitios
Un muro se nombra por los sitios que separa (ej. `08-12`) y **se asigna al sitio de menor número**
(muro entre X y X+1 → sitio X). Muros que dan a calle/pasaje llevan un solo número (ej. `46`).
Por eso el sitio 2 no aparece en la tabla: su único muro (1-2) se asigna al sitio 1.

---

## 3. Cómo funciona

### 3.1 Del PNG al DXF (Python)

El plano solo existía como imagen, así que se vectorizó por color:

| Paso | Qué hace |
|---|---|
| 1. Regiones | Las líneas oscuras (deslindes) y los muros de color se tratan como "paredes"; el espacio libre se divide en regiones cerradas. La región que contiene el rótulo "SITIO N" es el sitio N. |
| 2. Muros | Se aíslan los píxeles **rojos (fondo de patio)** y **cian (zona casa)**, se adelgazan a 1 px (esqueleto) y se convierten en polilíneas. |
| 3. Agrupar | Cada ~20 px de muro se mira a ambos lados qué sitio hay → el muro queda identificado por sus sitios. Si eso cambia a lo largo de una línea, se corta. Los retornos y ganchos cortos se unen al muro vecino. Se aplican correcciones manuales (`CORRECCIONES` en `config.py`). |
| 4. DXF | Una capa por tramo: `M_<muro>_CASA` y `M_<muro>_PATIO` (ej. `M_08-12_PATIO`), más capas de fondo `BASE_*` y `TEXTO_SITIOS`. |
| 5. Dashboard | El texto del DXF se incrusta en la plantilla HTML. Si ya había avance registrado, se conserva. |

**Resultado: 52 muros, 97 tramos** (ver tabla al final).

### 3.2 El dashboard (HTML + JavaScript, un solo archivo)

- Dentro del HTML hay un bloque `<script id="datos">` con: el DXF completo, el estado de cada tramo
  (`{"08-12/P": {"e": 3, "f": "2026-11-23"}}`) y la fecha del último guardado.
- Al abrir, el propio HTML lee el DXF (líneas, polilíneas y textos), identifica los tramos por el
  **nombre de capa** y los dibuja en SVG con el color de su estado.
- *Guardar en el HTML* vuelve a escribir el archivo completo con el bloque de datos actualizado.
- *Cargar DXF* reemplaza el plano por otro DXF que use la misma convención de capas; el avance de los
  tramos con el mismo nombre se mantiene.
- Al inicio del código hay un bloque **CONFIGURACIÓN** (nombre del proyecto, estados, colores,
  ponderación y patrón de capas) para adaptarlo a otras obras sin tocar el resto.

---

## 4. Modificar o reutilizar

**Corregir un tramo mal asignado:** en AutoCAD, mover la polilínea a la capa correcta
(o renombrar la capa) → en el dashboard, *Cargar DXF* → *Guardar en el HTML*.

**Agregar un muro nuevo:** dibujar la polilínea en una capa `M_<muro>_CASA` o `M_<muro>_PATIO`.

**Escala real:** el PNG no trae escala, así que el DXF está en unidades de imagen
(1 px = 0,01 unidades). El dashboard no muestra metros y el % ponderado no depende de la escala.
Para tener largos reales en el CSV, escalar el DXF en AutoCAD con una cota conocida
(`ESCALA` → `Referencia`) y volver a cargarlo.

**Otro proyecto que parte desde CAD:** basta con dibujar los muros en capas `M_..._CASA` /
`M_..._PATIO` y cargar el DXF en el dashboard. El código Python solo es necesario cuando el plano
viene como imagen.

**Regenerar todo desde la imagen:**
```bash
cd codigo
pip install -r requirements.txt
python ejecutar_todo.py        # ~2 min (la primera vez ~8 min por los deslindes)
```
Para otra imagen: cambiar en `config.py` la ruta del plano, los colores de los muros, las
posiciones de los rótulos de sitio y las correcciones; luego revisar `revision/control_tramos.jpg`.

---

## 5. Limitaciones conocidas

- La detección es automática a partir de colores; se revisó visualmente y se corrigieron 7 casos
  (`CORRECCIONES` en `config.py`). Conviene confirmar en terreno los muros traseros de los sitios
  44, 45 y 46 y el muro poniente del sitio 8.
- Los contornos de los edificios centrales quedaron incompletos (solo afecta el fondo).
- El respaldo automático del navegador es propio de cada computador; el registro "oficial" es el
  que queda guardado dentro del HTML.

---

## 6. Listado de muros

| Muro | Sitio asignado | Zona casa | Fondo de patio |
|---|---|---|---|
| 01 | 1 | ✓ | ✓ |
| 01-02 | 1 | ✓ | — |
| 03-04 | 3 | ✓ | ✓ |
| 04-05 | 4 | ✓ | ✓ |
| 05-06 | 5 | ✓ | — |
| 06-07 | 6 | ✓ | ✓ |
| 07-08 | 7 | ✓ | ✓ |
| 08-12 | 8 | ✓ | ✓ |
| 09-10 | 9 | ✓ | ✓ |
| 10-11 | 10 | ✓ | ✓ |
| 11-40 | 11 | ✓ | ✓ |
| 12-13 | 12 | ✓ | ✓ |
| 13-14 | 13 | ✓ | ✓ |
| 14-15 | 14 | ✓ | ✓ |
| 15-16 | 15 | ✓ | ✓ |
| 16-17 | 16 | ✓ | ✓ |
| 17-18 | 17 | ✓ | ✓ |
| 18-19 | 18 | ✓ | ✓ |
| 19-20 | 19 | ✓ | ✓ |
| 20-21 | 20 | ✓ | ✓ |
| 21-22 | 21 | ✓ | ✓ |
| 22-23 | 22 | ✓ | ✓ |
| 23-24 | 23 | ✓ | ✓ |
| 24-26 | 24 | ✓ | ✓ |
| 25-37 | 25 | ✓ | ✓ |
| 25-43 | 25 | ✓ | ✓ |
| 25-44 | 25 | — | ✓ |
| 26-27 | 26 | ✓ | ✓ |
| 27-28 | 27 | ✓ | ✓ |
| 28-29 | 28 | ✓ | ✓ |
| 29-30 | 29 | ✓ | ✓ |
| 30-31 | 30 | ✓ | ✓ |
| 31-32 | 31 | ✓ | ✓ |
| 32-33 | 32 | ✓ | ✓ |
| 33-34 | 33 | ✓ | ✓ |
| 34-35 | 34 | ✓ | ✓ |
| 35-36 | 35 | ✓ | ✓ |
| 36-47 | 36 | ✓ | ✓ |
| 36-48 | 36 | — | ✓ |
| 37-38 | 37 | ✓ | ✓ |
| 37-44 | 37 | — | ✓ |
| 38-39 | 38 | ✓ | ✓ |
| 39 | 39 | ✓ | ✓ |
| 40-41 | 40 | ✓ | ✓ |
| 41-42 | 41 | ✓ | ✓ |
| 42-43 | 42 | ✓ | ✓ |
| 44-45 | 44 | ✓ | ✓ |
| 45 | 45 | — | ✓ |
| 45-46 | 45 | ✓ | ✓ |
| 46 | 46 | ✓ | ✓ |
| 47-48 | 47 | ✓ | ✓ |
| 48 | 48 | ✓ | — |
