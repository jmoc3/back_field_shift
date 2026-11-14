"""Motor de recomendación de rotaciones: aptitud climática, reglas, puntaje y selección."""
from itertools import permutations
from statistics import mean

from analisis import textos

TOP_APTOS = 12
LARGO_ROTACION = 3
PESOS_POR_ORDEN = [0.4, 0.3, 0.2, 0.1]
PRIORIDADES = ["agua", "suelo", "economia", "equipos"]
NIVEL_INVERSO = {"bajo": 1.0, "baja": 1.0, "medio": 0.5, "media": 0.5, "alto": 0.0, "alta": 0.0}
NEUTRO = 0.5  # cuando el dato no existe
CLAVES_CLIMA = ["lluvia_anual_mm", "temp_media_c", "dias_calor", "riesgo_helada", "humedad_suelo", "fuente"]
AVISO = "Herramienta de apoyo: revisa estas opciones con un agrónomo local."


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

    return {
        "agua": mean(agua(c) for c in secuencia),
        "suelo": mean(suelo(c) for c in secuencia),
        "economia": mean(NIVEL_INVERSO.get(c["costo"], NEUTRO) for c in secuencia),
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

def _opcion(id_, secuencia, clima, pesos_, aptitudes, es_actual, reglas):
    subs = subpuntajes(secuencia, clima)
    contexto = {
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
        "nombre": " → ".join(c["nombre"] for c in secuencia),
        "cultivos": [c["id"] for c in secuencia],
        "puntaje": round(puntaje(subs, pesos_), 2),
        **textos.armar(contexto),
    }


def analizar(lat, lon, rotacion, prioridades, clima=None, catalogo=None):
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

    opciones = [_opcion("actual", actual, clima, pesos_, aptitudes, True, infracciones(actual))]
    for i, s in enumerate(elegidas, start=1):
        opciones.append(_opcion(f"opcion_{i}", list(s), clima, pesos_, aptitudes, False, []))

    return {
        "version": "1.0",
        "clima": {k: clima[k] for k in CLAVES_CLIMA},
        "opciones": opciones,
        "aviso": AVISO,
    }
