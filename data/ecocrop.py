"""Catálogo de cultivos de campo leído directamente de EcoCrop_DB.csv.

Provisional hasta que exista cultivos.json: devuelve las mismas llaves que tendrá ese archivo.
Los campos que EcoCrop no trae (aporte al suelo, costo, maquinaria) quedan en None.
"""
import csv
from functools import lru_cache
from pathlib import Path

RUTA_CSV = Path(__file__).with_name("EcoCrop_DB.csv")

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

LEGUMINOSAS = {"Leguminosae", "Fabaceae"}
CEREALES = {"Gramineae", "Poaceae"}


def _numero(valor):
    try:
        return float(valor)
    except (TypeError, ValueError):
        return None


@lru_cache(maxsize=1)
def cargar_cultivos():
    with open(RUTA_CSV, encoding="latin-1", newline="") as archivo:
        filas = {f["ScientificName"].strip(): f for f in csv.DictReader(archivo)}

    catalogo = []
    for id_, nombre, cientifico in CULTIVOS:
        f = filas[cientifico]
        familia = f["FAMNAME"].split(":")[-1].strip()
        catalogo.append({
            "id": id_,
            "nombre": nombre,
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
            "maquinaria": None,  # "baja" | "media" | "alta"
        })
    return catalogo
