"""Motor de recomendación de rotaciones: aptitud climática, reglas, puntaje y selección."""
from itertools import permutations
from statistics import mean

from analisis import textos

TOP_APTOS = 12
LARGO_ROTACION = 3
PESOS_POR_ORDEN = [0.4, 0.3, 0.2, 0.1]
PRIORIDADES = ["agua", "suelo", "economia", "equipos"]
NIVEL_INVERSO = {"bajo": 1.0, "baja": 1.0, "medio": 0.5, "media": 0.5, "alto": 0.0, "alta": 0.0}
NIVEL_DIRECTO = {"bajo": 0.0, "medio": 0.5, "alto": 1.0}
NEUTRO = 0.5  # cuando el dato no existe
CLAVES_CLIMA = ["lluvia_anual_mm", "temp_media_c", "dias_calor", "riesgo_helada", "humedad_suelo", "fuente"]
AVISO = {
    "es": "Herramienta de apoyo: revisa estas opciones con un agrónomo local.",
    "en": "Support tool: review these options with a local agronomist.",
}
ETIQUETAS_CLIMA = {
    "es": {"baja": "baja", "media": "media", "alta": "alta", "seco": "seco", "moderado": "moderado",
           "húmedo": "húmedo", "frío": "frío", "templado": "templado", "cálido": "cálido"},
    "en": {"baja": "low", "media": "medium", "alta": "high", "seco": "dry", "moderado": "moderate",
           "húmedo": "humid", "frío": "cold", "templado": "temperate", "cálido": "warm"},
}


def nombre_cultivo(c, idioma="es"):
    return c.get("nombre_en", c["nombre"]) if idioma == "en" else c["nombre"]


# ---------- Aptitud climática ----------

def _rango(valor, abs_min, opt_min, opt_max, abs_max):
    """1 dentro del óptimo, baja en línea recta hasta 0 en el límite absoluto.

    Fuera del límite absoluto sigue bajando (negativo) para poder ordenar cuál está menos lejos;
    al mostrarse se recorta a 0.
    """
    if None in (abs_min, opt_min, opt_max, abs_max):
        return NEUTRO
    if opt_min <= valor <= opt_max:
        return 1.0
    if valor < opt_min:
        return (valor - abs_min) / (opt_min - abs_min)
    return (abs_max - valor) / (abs_max - opt_max)


def aptitud(cultivo, clima):
    """Factor más limitante entre temperatura, lluvia y helada (1 = ideal, <= 0 = no apto)."""
    temp = _rango(clima["temp_media_c"], cultivo["tmin"], cultivo["topmn"], cultivo["topmx"], cultivo["tmax"])
    lluvia = _rango(clima["lluvia_anual_mm"], cultivo["rmin"], cultivo["ropmn"], cultivo["ropmx"], cultivo["rmax"])
    helada = 0.5 if cultivo["ktmp"] is not None and clima["temp_min_abs_c"] <= cultivo["ktmp"] else 1.0
    return min(temp, lluvia, helada)


# ---------- Reglas ----------

def _pares(secuencia):
    """Pares consecutivos, incluyendo el paso del último al primero (siguiente ciclo)."""
    return [(secuencia[i], secuencia[(i + 1) % len(secuencia)]) for i in range(len(secuencia))]


def infracciones(secuencia, ultimo_actual=None):
    resultado = []
    for a, b in _pares(secuencia):
        if a["familia"] == b["familia"]:
            resultado.append({"regla": "familia_repetida", "a": a, "b": b})
        if a["cereal"] and not b["fija_nitrogeno"]:
            resultado.append({"regla": "cereal_sin_leguminosa", "a": a, "b": b})
    if ultimo_actual and secuencia[0]["id"] == ultimo_actual:
        resultado.append({"regla": "repite_ultimo", "a": secuencia[0], "b": None})
    return resultado


# ---------- Puntaje ----------

def subpuntajes(secuencia, clima):
    lluvia = clima["lluvia_anual_mm"]

    def agua(c):
        demanda = c["ropmn"] or c["rmin"]
        return min(1.0, lluvia / demanda) if demanda else NEUTRO

    def suelo(c):
        if c["fija_nitrogeno"]:
            return 1.0
        return NEUTRO if c["aporte_suelo"] else 0.0

    def economia(c):
        # Precio de referencia al productor (USDA NASS, EE. UU.): más alto, mejor. Si no hay, el costo (inverso).
        if c.get("precio_nivel"):
            return NIVEL_DIRECTO[c["precio_nivel"]]
        return NIVEL_INVERSO.get(c["costo"], NEUTRO)

    return {
        "agua": mean(agua(c) for c in secuencia),
        "suelo": mean(suelo(c) for c in secuencia),
        "economia": mean(economia(c) for c in secuencia),
        "equipos": mean(NIVEL_INVERSO.get(c["maquinaria"], NEUTRO) for c in secuencia),
    }


def pesos(prioridades):
    validas = [p for p in dict.fromkeys(prioridades) if p in PRIORIDADES] or PRIORIDADES
    crudos = dict(zip(validas, PESOS_POR_ORDEN))
    total = sum(crudos.values())
    return {p: w / total for p, w in crudos.items()}


def puntaje(subs, pesos_):
    return sum(w * subs[p] for p, w in pesos_.items())


# ---------- Análisis completo ----------

def etiquetas_clima(clima, idioma="es"):
    """Categorías legibles para las tarjetas del front."""
    h, lluvia, t = clima["humedad_suelo"], clima["lluvia_anual_mm"], clima["temp_media_c"]
    humedad = "baja" if h < 0.3 else "alta" if h > 0.7 else "media"
    hidrico = "seco" if lluvia < 600 else "húmedo" if lluvia > 1500 else "moderado"
    termico = "frío" if t < 12 else "cálido" if t > 22 else "templado"
    e = ETIQUETAS_CLIMA[idioma]
    return {"humedad_nivel": e[humedad], "clima_tipo": f"{e[hidrico]}/{e[termico]}"}


def _demanda_agua(secuencia):
    """Lluvia anual que piden los cultivos según EcoCrop (promedio de ROPMN, o RMIN si falta)."""
    valores = [c["ropmn"] or c["rmin"] for c in secuencia if c["ropmn"] or c["rmin"]]
    return mean(valores) if valores else None


def aporte(secuencia, actual, clima):
    """Comparación contra la rotación actual (referencia)."""
    demanda, demanda_ref = _demanda_agua(secuencia), _demanda_agua(actual)
    agua = round(100 * demanda / demanda_ref) if demanda and demanda_ref else None
    suelo = subpuntajes(secuencia, clima)["suelo"]
    suelo_ref = subpuntajes(actual, clima)["suelo"]
    return {
        "agua": {"referencia": 100, "rotacion": agua, "cambio_pct": None if agua is None else agua - 100},
        "suelo": {
            "referencia": round(suelo_ref, 2),
            "rotacion": round(suelo, 2),
            "nivel": "mayor" if suelo > suelo_ref else "menor" if suelo < suelo_ref else "igual",
        },
    }


def _opcion(id_, secuencia, clima, pesos_, aptitudes, es_actual, reglas, actual, idioma="es"):
    subs = subpuntajes(secuencia, clima)
    contexto = {
        "idioma": idioma,
        "secuencia": secuencia,
        "clima": clima,
        "subpuntajes": subs,
        "aptitudes": aptitudes,
        "prioridades": list(pesos_),
        "infracciones": reglas,
        "actual": es_actual,
    }
    return {
        "id": id_,
        "actual": es_actual,
        "nombre": " → ".join(nombre_cultivo(c, idioma) for c in secuencia),
        "cultivos": [c["id"] for c in secuencia],
        "puntaje": round(puntaje(subs, pesos_), 2),
        **textos.armar(contexto),
        "aporte": aporte(secuencia, actual, clima),
    }


def analizar(lat, lon, rotacion, prioridades, clima=None, catalogo=None, idioma="es"):
    if clima is None:
        from data.nasa_power import obtener_clima
        clima = obtener_clima(lat, lon)
    if catalogo is None:
        from data.ecocrop import cargar_cultivos
        catalogo = cargar_cultivos()

    por_id = {c["id"]: c for c in catalogo}
    desconocidos = [r for r in rotacion if r not in por_id]
    if desconocidos:
        raise ValueError(f"Cultivos desconocidos: {', '.join(desconocidos)}")

    actual = [por_id[r] for r in rotacion]
    aptitudes = {c["id"]: aptitud(c, clima) for c in catalogo}
    pesos_ = pesos(prioridades)

    # Los 12 más aptos (empate por id para que sea determinista) + los de la rotación actual.
    ordenados = sorted(catalogo, key=lambda c: (-aptitudes[c["id"]], c["id"]))
    ids_pool = [c["id"] for c in ordenados[:TOP_APTOS]]
    ids_pool += [r for r in dict.fromkeys(rotacion) if r not in ids_pool]
    pool = [por_id[i] for i in ids_pool]

    # Candidatas válidas, distintas a la rotación actual.
    conjunto_actual = sorted(rotacion)
    candidatas = [
        s for s in permutations(pool, LARGO_ROTACION)
        if not infracciones(s, rotacion[-1]) and sorted(c["id"] for c in s) != conjunto_actual
    ]

    def orden(s):
        return (
            -puntaje(subpuntajes(s, clima), pesos_),
            -mean(aptitudes[c["id"]] for c in s),
            [c["id"] for c in s],
        )

    candidatas.sort(key=orden)

    # Las 2 mejores que no sean casi iguales (comparten como máximo 1 cultivo).
    elegidas = []
    for s in candidatas:
        ids = {c["id"] for c in s}
        if all(len(ids & {c["id"] for c in e}) <= 1 for e in elegidas):
            elegidas.append(s)
        if len(elegidas) == 2:
            break

    opciones = [_opcion("actual", actual, clima, pesos_, aptitudes, True, infracciones(actual), actual, idioma)]
    for i, s in enumerate(elegidas, start=1):
        opciones.append(_opcion(f"opcion_{i}", list(s), clima, pesos_, aptitudes, False, [], actual, idioma))

    return {
        "version": "1.0",
        "clima": {**{k: clima[k] for k in CLAVES_CLIMA}, **etiquetas_clima(clima, idioma)},
        "opciones": opciones,
        "aviso": AVISO[idioma],
    }
