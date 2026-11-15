"""Catálogo de cultivos de campo leído directamente de EcoCrop_DB.csv.

Provisional hasta que exista cultivos.json: devuelve las mismas llaves que tendrá ese archivo.
Los campos que EcoCrop no trae (aporte al suelo, costo) quedan en None; maquinaria y precio salen de insumos.json.
"""
import csv
import json
from functools import lru_cache
from pathlib import Path

RUTA_CSV = Path(__file__).with_name("EcoCrop_DB.csv")
# Maquinaria (FAO GAEZ) y precio de referencia (USDA NASS), generado por data/extraer_insumos.py
RUTA_INSUMOS = Path(__file__).with_name("insumos.json")

# id, nombre en español, nombre científico en EcoCrop
CULTIVOS = [
    ("maiz", "Maíz", "Zea mays"),
    ("trigo", "Trigo", "Triticum aestivum"),
    ("cebada", "Cebada", "Hordeum vulgare"),
    ("avena", "Avena", "Avena sativa"),
    ("arroz", "Arroz", "Oryza sativa"),
    ("sorgo", "Sorgo", "Sorghum bicolor"),
    ("mijo", "Mijo perla", "Pennisetum glaucum"),
    ("centeno", "Centeno", "Secale cereale"),
    ("quinua", "Quinua", "Chenopodium quinoa"),
    ("amaranto", "Amaranto", "Amaranthus caudatus"),
    ("frijol", "Fríjol", "Phaseolus vulgaris"),
    ("arveja", "Arveja", "Pisum sativum"),
    ("haba", "Haba", "Vicia faba"),
    ("garbanzo", "Garbanzo", "Cicer arietinum"),
    ("lenteja", "Lenteja", "Lens culinaris"),
    ("soya", "Soya", "Glycine max"),
    ("mani", "Maní", "Arachis hypogaea"),
    ("caupi", "Caupí", "Vigna unguiculata"),
    ("guandul", "Guandul", "Cajanus cajan"),
    ("alfalfa", "Alfalfa", "Medicago sativa"),
    ("trebol_rojo", "Trébol rojo", "Trifolium pratense"),
    ("tarwi", "Tarwi (chocho)", "Lupinus mutabilis"),
    ("frijol_mungo", "Fríjol mungo", "Vigna radiata"),
    ("mucuna", "Mucuna", "Mucuna pruriens"),
    ("canavalia", "Canavalia", "Canavalia ensiformis"),
    ("papa", "Papa", "Solanum tuberosum"),
    ("yuca", "Yuca", "Manihot esculenta"),
    ("batata", "Batata", "Ipomoea batatas"),
    ("malanga", "Malanga", "Colocasia esculenta"),
    ("girasol", "Girasol", "Helianthus annuus"),
    ("colza", "Colza", "Brassica napus"),
    ("algodon", "Algodón", "Gossypium hirsutum"),
    ("ajonjoli", "Ajonjolí", "Sesamum indicum"),
    ("cartamo", "Cártamo", "Carthamus tinctorius"),
    ("linaza", "Linaza", "Linum usitatissimum"),
    ("trigo_sarraceno", "Trigo sarraceno", "Fagopyrum esculentum"),
    ("tomate", "Tomate", "Lycopersicon esculentum"),
    ("cebolla", "Cebolla", "Allium cepa"),
    ("zanahoria", "Zanahoria", "Daucus carota"),
    ("ahuyama", "Ahuyama", "Cucurbita moschata"),
    ("remolacha", "Remolacha", "Beta vulgaris"),
]

# Nombre común en inglés (respuestas con Accept-Language: en)
NOMBRES_EN = {
    "maiz": "Maize", "trigo": "Wheat", "cebada": "Barley", "avena": "Oats", "arroz": "Rice",
    "sorgo": "Sorghum", "mijo": "Pearl millet", "centeno": "Rye", "quinua": "Quinoa", "amaranto": "Amaranth",
    "frijol": "Common bean", "arveja": "Pea", "haba": "Faba bean", "garbanzo": "Chickpea", "lenteja": "Lentil",
    "soya": "Soybean", "mani": "Peanut", "caupi": "Cowpea", "guandul": "Pigeon pea", "alfalfa": "Alfalfa",
    "trebol_rojo": "Red clover", "tarwi": "Tarwi (Andean lupin)", "frijol_mungo": "Mung bean",
    "mucuna": "Velvet bean", "canavalia": "Jack bean", "papa": "Potato", "yuca": "Cassava",
    "batata": "Sweet potato", "malanga": "Taro", "girasol": "Sunflower", "colza": "Rapeseed",
    "algodon": "Cotton", "ajonjoli": "Sesame", "cartamo": "Safflower", "linaza": "Flax",
    "trigo_sarraceno": "Buckwheat", "tomate": "Tomato", "cebolla": "Onion", "zanahoria": "Carrot",
    "ahuyama": "Squash", "remolacha": "Beet",
}

LEGUMINOSAS = {"Leguminosae", "Fabaceae"}
CEREALES = {"Gramineae", "Poaceae"}


def _numero(valor):
    try:
        return float(valor)
    except (TypeError, ValueError):
        return None


def _insumos():
    if not RUTA_INSUMOS.exists():
        return {}
    return json.loads(RUTA_INSUMOS.read_text(encoding="utf-8")).get("cultivos", {})


@lru_cache(maxsize=1)
def cargar_cultivos():
    with open(RUTA_CSV, encoding="latin-1", newline="") as archivo:
        filas = {f["ScientificName"].strip(): f for f in csv.DictReader(archivo)}
    insumos = _insumos()

    catalogo = []
    for id_, nombre, cientifico in CULTIVOS:
        f = filas[cientifico]
        familia = f["FAMNAME"].split(":")[-1].strip()
        extra = insumos.get(id_, {})
        catalogo.append({
            "id": id_,
            "nombre": nombre,
            "nombre_en": NOMBRES_EN[id_],
            "nombre_cientifico": cientifico,
            "familia": familia,
            "topmn": _numero(f["TOPMN"]),
            "topmx": _numero(f["TOPMX"]),
            "tmin": _numero(f["TMIN"]),
            "tmax": _numero(f["TMAX"]),
            "ropmn": _numero(f["ROPMN"]),
            "ropmx": _numero(f["ROPMX"]),
            "rmin": _numero(f["RMIN"]),
            "rmax": _numero(f["RMAX"]),
            "ktmp": _numero(f["KTMP"]),
            "gmin": _numero(f["GMIN"]),
            "gmax": _numero(f["GMAX"]),
            "fija_nitrogeno": familia in LEGUMINOSAS,
            "cereal": familia in CEREALES,
            # No vienen en EcoCrop: se completan a mano en cultivos.json.
            "aporte_suelo": None,
            "costo": None,       # "bajo" | "medio" | "alto"
            # De insumos.json (None si la fuente no cubre el cultivo)
            "maquinaria": extra.get("maquinaria"),        # "baja" | "media" | "alta" (FAO GAEZ)
            "precio_usd_kg": extra.get("precio_usd_kg"),  # precio al productor en EE. UU. (USDA NASS)
            "precio_nivel": extra.get("precio_nivel"),    # "bajo" | "medio" | "alto"
        })
    return catalogo
