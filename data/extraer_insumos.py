"""Genera data/insumos.json con la maquinaria (FAO GAEZ v4) y el precio de referencia (USDA NASS) de cada cultivo.

Se ejecuta a mano, no en cada petición:

    python data/extraer_insumos.py gaez          # público, sin clave
    NASS_API_KEY=... python data/extraer_insumos.py nass   # clave gratuita en quickstats.nass.usda.gov/api

Cada paso actualiza solo su parte de insumos.json y al final regenera cultivos.json (lo que sirve GET
api/v1/cultivos) desde cargar_cultivos(), para que el análisis y el endpoint usen exactamente los mismos datos.

- Maquinaria: GAEZ calcula el rendimiento alcanzable con insumos altos (totalmente mecanizado, fertilizado) y
  bajos (trabajo manual, sin fertilizante). Cuanto más rinde un cultivo con insumos altos frente a bajos, más
  depende de maquinaria e insumos. Se usa la mediana de esa razón en zonas agrícolas de Colombia.
- Precio: precio que reciben los productores de EE. UU. (NASS, nacional, anual), promedio de los últimos años,
  convertido a USD/kg. No es un costo de producción ni un precio de Colombia.
"""
import json
import os
import sys
from datetime import date
from pathlib import Path
from statistics import mean, median

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from data.ecocrop import cargar_cultivos  # noqa: E402

RUTA_INSUMOS = Path(__file__).with_name("insumos.json")
RUTA_CULTIVOS = Path(__file__).with_name("cultivos.json")

# ---------- FAO GAEZ v4 ----------

GAEZ_SERVICIO = "https://gaez-services.fao.org/server/rest/services/res05/ImageServer"
RAZON_TOPE = 20.0  # rendimiento con insumos bajos = 0

# Código GAEZ de cada cultivo del catálogo (sin código = GAEZ no lo modela)
GAEZ_CODIGOS = {
    "maiz": "mze", "trigo": "whe", "cebada": "brl", "avena": "oat", "arroz": "rcw", "sorgo": "srg",
    "mijo": "pml", "centeno": "rye", "frijol": "phb", "arveja": "pea", "garbanzo": "chk", "soya": "soy",
    "mani": "grd", "caupi": "cow", "guandul": "pig", "alfalfa": "alf", "papa": "wpo", "yuca": "csv",
    "batata": "spo", "girasol": "sfl", "colza": "rsd", "algodon": "cot", "linaza": "flx",
    "trigo_sarraceno": "bck", "tomate": "tom", "cebolla": "oni", "zanahoria": "car",
}

# Zonas agrícolas de Colombia (lat, lon) donde se compara el rendimiento con insumos altos y bajos
PUNTOS_COLOMBIA = [
    (5.53, -73.36),   # Tunja, Boyacá
    (4.86, -74.05),   # Sabana de Bogotá
    (1.21, -77.28),   # Pasto, Nariño
    (6.15, -75.37),   # Rionegro, Antioquia
    (4.44, -75.23),   # Ibagué, Tolima
    (8.75, -75.88),   # Montería, Córdoba
    (4.14, -73.63),   # Villavicencio, Meta
    (6.99, -73.05),   # Piedecuesta, Santander
    (10.46, -73.25),  # Valledupar, Cesar
    (3.54, -76.30),   # Palmira, Valle del Cauca
]


def _gaez_raster_id(nombre):
    """objectid del ráster de rendimiento (secano, 1981-2010, clima observado CRUTS32)."""
    r = requests.get(f"{GAEZ_SERVICIO}/query", timeout=60, params={
        "where": f"name='{nombre}' AND year='1981-2010' AND model='CRUTS32'",
        "outFields": "objectid", "returnGeometry": "false", "f": "json",
    })
    r.raise_for_status()
    features = r.json().get("features", [])
    return features[0]["attributes"]["objectid"] if features else None


def _gaez_valores(raster_id):
    """Rendimiento (kg MS/ha) del ráster en cada punto; None donde el cultivo no es viable."""
    geometria = {"points": [[lon, lat] for lat, lon in PUNTOS_COLOMBIA], "spatialReference": {"wkid": 4326}}
    r = requests.get(f"{GAEZ_SERVICIO}/getSamples", timeout=90, params={
        "geometry": json.dumps(geometria),
        "geometryType": "esriGeometryMultipoint",
        "mosaicRule": json.dumps({"mosaicMethod": "esriMosaicLockRaster", "lockRasterIds": [raster_id]}),
        "returnFirstValueOnly": "true",
        "f": "json",
    })
    r.raise_for_status()
    valores = []
    for muestra in r.json().get("samples", []):
        try:
            valor = float(muestra["value"])
        except (KeyError, TypeError, ValueError):
            valor = None
        valores.append(valor if valor and valor > 0 else None)
    return valores


def extraer_gaez():
    resultado = {}
    for id_, codigo in GAEZ_CODIGOS.items():
        alto_id, bajo_id = _gaez_raster_id(f"yxHr_{codigo}"), _gaez_raster_id(f"yxLr_{codigo}")
        if not alto_id or not bajo_id:
            print(f"  {id_}: sin ráster GAEZ")
            continue
        altos, bajos = _gaez_valores(alto_id), _gaez_valores(bajo_id)
        # Si rinde con insumos altos pero nada con bajos, depende por completo de ellos: razón tope
        razones = [a / b if b else RAZON_TOPE for a, b in zip(altos, bajos) if a]
        if not razones:
            print(f"  {id_}: GAEZ no lo considera viable en los puntos de Colombia")
            continue
        resultado[id_] = {
            "gaez_codigo": codigo,
            "razon_insumos": round(median(razones), 2),
            "puntos_validos": len(razones),
        }
        print(f"  {id_}: razón alto/bajo {resultado[id_]['razon_insumos']} ({len(razones)} puntos)")

    # Terciles entre cultivos: la tercera parte que más depende de insumos altos -> maquinaria "alta"
    _niveles(resultado, "razon_insumos", "maquinaria", ("baja", "media", "alta"))
    return resultado


# ---------- USDA NASS QuickStats ----------

NASS_API = "https://quickstats.nass.usda.gov/api/api_GET/"
ANIOS = 5

KG_POR_LB = 0.45359237
# Peso oficial del bushel de cada producto en EE. UU. (lb)
LB_POR_BUSHEL = {"CORN": 56, "WHEAT": 60, "BARLEY": 48, "OATS": 32, "RYE": 56, "SOYBEANS": 60,
                 "FLAXSEED": 56, "MILLET": 50}

# commodity_desc de NASS para cada cultivo (sin entrada = NASS no publica su precio)
NASS_PRODUCTOS = {
    "maiz": "CORN", "trigo": "WHEAT", "cebada": "BARLEY", "avena": "OATS", "arroz": "RICE",
    "sorgo": "SORGHUM", "mijo": "MILLET", "centeno": "RYE", "frijol": "BEANS", "arveja": "PEAS",
    "garbanzo": "CHICKPEAS", "lenteja": "LENTILS", "soya": "SOYBEANS", "mani": "PEANUTS",
    "alfalfa": "HAY", "papa": "POTATOES", "batata": "SWEET POTATOES", "girasol": "SUNFLOWER",
    "colza": "CANOLA", "algodon": "COTTON", "cartamo": "SAFFLOWER", "linaza": "FLAXSEED",
    "tomate": "TOMATOES", "cebolla": "ONIONS", "zanahoria": "CARROTS", "ahuyama": "SQUASH",
}
# Cuando un producto tiene varias series de precio, se prefiere la que contenga este texto
NASS_SERIE = {"maiz": "GRAIN", "sorgo": "GRAIN", "frijol": "DRY EDIBLE", "arveja": "DRY EDIBLE",
              "alfalfa": "ALFALFA", "algodon": "LINT", "tomate": "FRESH MARKET", "cebolla": "",
              "zanahoria": "FRESH MARKET"}


def _usd_por_kg(valor, unidad, producto):
    unidad = unidad.replace(" ", "").upper()
    if unidad == "$/LB":
        return valor / KG_POR_LB
    if unidad == "$/CWT":
        return valor / (100 * KG_POR_LB)
    if unidad == "$/TON":
        return valor / (2000 * KG_POR_LB)
    if unidad == "$/BU" and producto in LB_POR_BUSHEL:
        return valor / (LB_POR_BUSHEL[producto] * KG_POR_LB)
    return None


def _nass_precio(clave, id_, producto):
    r = requests.get(NASS_API, timeout=60, params={
        "key": clave, "source_desc": "SURVEY", "commodity_desc": producto,
        "statisticcat_desc": "PRICE RECEIVED", "agg_level_desc": "NATIONAL", "freq_desc": "ANNUAL",
        "year__GE": str(date.today().year - ANIOS - 1), "format": "JSON",
    })
    if r.status_code != 200:  # NASS responde 400 cuando no hay registros
        return None
    filas = []
    for f in r.json().get("data", []):
        try:
            valor = float(str(f["Value"]).replace(",", ""))
        except ValueError:
            continue  # "(D)", "(NA)": dato no publicado
        kg = _usd_por_kg(valor, f["unit_desc"], producto)
        if kg:
            filas.append((f["short_desc"], int(f["year"]), kg))
    if not filas:
        return None

    preferida = NASS_SERIE.get(id_, "")
    series = sorted({s for s, _, _ in filas}, key=lambda s: (preferida not in s, len(s)))
    serie = series[0]
    # NASS publica a veces el mismo año como "MARKETING YEAR" y "YEAR": un valor (promedio) por año
    por_anio = {}
    for s, anio, kg in filas:
        if s == serie:
            por_anio.setdefault(anio, []).append(kg)
    anios = sorted(por_anio)[-ANIOS:]
    return {"nass_serie": serie, "precio_usd_kg": round(mean(mean(por_anio[a]) for a in anios), 3),
            "precio_anios": f"{anios[0]}-{anios[-1]}"}


def extraer_nass():
    clave = os.environ.get("NASS_API_KEY")
    if not clave:
        sys.exit("Falta la variable de entorno NASS_API_KEY (clave gratuita en quickstats.nass.usda.gov/api).")
    resultado = {}
    for id_, producto in NASS_PRODUCTOS.items():
        datos = _nass_precio(clave, id_, producto)
        if datos:
            resultado[id_] = datos
            print(f"  {id_}: {datos['precio_usd_kg']} USD/kg ({datos['nass_serie']}, {datos['precio_anios']})")
        else:
            print(f"  {id_}: sin precio en NASS")
    _niveles(resultado, "precio_usd_kg", "precio_nivel", ("bajo", "medio", "alto"))
    return resultado


# ---------- Común ----------

def _niveles(datos, campo, destino, etiquetas):
    """Asigna bajo/medio/alto por terciles del campo entre los cultivos que lo tienen."""
    orden = sorted(datos, key=lambda k: datos[k][campo])
    for i, id_ in enumerate(orden):
        datos[id_][destino] = etiquetas[min(2, i * 3 // len(orden))]


def guardar(parte, datos, fuente):
    insumos = json.loads(RUTA_INSUMOS.read_text(encoding="utf-8")) if RUTA_INSUMOS.exists() else {}
    insumos.setdefault("fuentes", {})[parte] = {**fuente, "fecha": date.today().isoformat()}
    cultivos = insumos.setdefault("cultivos", {})
    campos = {"gaez": ("gaez_codigo", "razon_insumos", "puntos_validos", "maquinaria"),
              "nass": ("nass_serie", "precio_usd_kg", "precio_anios", "precio_nivel")}[parte]
    for id_ in list(cultivos):  # se limpia lo anterior de esta parte
        for campo in campos:
            cultivos[id_].pop(campo, None)
    for id_, valores in datos.items():
        cultivos.setdefault(id_, {}).update(valores)
    RUTA_INSUMOS.write_text(json.dumps(insumos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    cargar_cultivos.cache_clear()
    RUTA_CULTIVOS.write_text(json.dumps(cargar_cultivos(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Guardado {RUTA_INSUMOS.name} ({len(datos)} cultivos con {parte}) y regenerado {RUTA_CULTIVOS.name}.")


if __name__ == "__main__":
    paso = sys.argv[1] if len(sys.argv) > 1 else ""
    if paso == "gaez":
        guardar("gaez", extraer_gaez(), {
            "nombre": "FAO GAEZ v4 (res05, yxHr/yxLr, secano, 1981-2010)",
            "puntos": [list(p) for p in PUNTOS_COLOMBIA],
        })
    elif paso == "nass":
        guardar("nass", extraer_nass(), {
            "nombre": "USDA NASS QuickStats (PRICE RECEIVED, nacional, anual)", "pais": "Estados Unidos",
        })
    else:
        sys.exit("Uso: python data/extraer_insumos.py gaez|nass")
