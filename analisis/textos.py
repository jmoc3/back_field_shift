"""Textos de cada opción armados con plantillas a partir de los valores reales (español o inglés)."""
from statistics import mean

ETIQUETAS = {
    "es": {"agua": "agua", "suelo": "salud del suelo", "economia": "precio de referencia", "equipos": "maquinaria"},
    "en": {"agua": "water", "suelo": "soil health", "economia": "reference price", "equipos": "machinery"},
}

TEXTOS = {
    "es": {
        "y": " y ",
        # porque
        "porque_actual": "Es la rotación que usas hoy; sirve de punto de comparación (aptitud climática media {apt}).",
        "porque_prioridad": "puntúa {v} de 1 en tu prioridad principal ({etiqueta})",
        "porque_leguminosa": "incluye {lista}, que fija nitrógeno",
        "porque_familia": "cambia de familia en cada ciclo",
        "porque_aptitud": "sus cultivos tienen una aptitud climática media de {apt} en tu ubicación",
        "porque_inicio": "Se sugiere porque ",
        "porque_exigente": ". Ojo: el clima de tu ubicación es exigente para todo el catálogo (aptitud media {apt}); "
                           "son las opciones menos alejadas de sus rangos.",
        # evidencia
        "lluvia_dato": "Lluvia anual", "lluvia_unidad": "mm/año",
        "lluvia_ok": "Dentro del rango de lluvia óptimo de EcoCrop para todos los cultivos.",
        "lluvia_bajo": "Por debajo del óptimo de EcoCrop para: {lista}.",
        "lluvia_alto": "Por encima del óptimo de EcoCrop para: {lista}.",
        "temp_dato": "Temperatura media",
        "temp_fuera": "Fuera del rango óptimo de EcoCrop para: {lista}.",
        "temp_ok": "Dentro del rango de temperatura óptimo de EcoCrop para todos los cultivos.",
        "tmin_dato": "Temperatura mínima registrada",
        "tmin_bajo": "Por debajo del umbral de helada de EcoCrop para: {lista}.",
        "tmin_ok": "Por encima del umbral de helada de EcoCrop de los cultivos que lo reportan.",
        "calor_dato": "Días de calor extremo (>35 °C)", "calor_unidad": "días/año",
        "calor_nota": "Temperatura máxima registrada: {t} °C.",
        "humedad_dato": "Humedad del suelo en raíces", "humedad_unidad": "fracción 0–1",
        "humedad_seco": "Suelo seco en la zona de raíces: conviene preferir cultivos tolerantes a sequía.",
        "humedad_humedo": "Suelo muy húmedo en la zona de raíces: atención al encharcamiento.",
        "humedad_media": "Humedad moderada en la zona de raíces.",
        # beneficios
        "ben_conocida": "Ya conoces su manejo.",
        "ben_nitrogeno": "{n} fija nitrógeno: puede reducir el fertilizante del cultivo siguiente.",
        "ben_familias": "Familias distintas ({lista}): interrumpe ciclos de plagas y enfermedades.",
        "ben_lluvia": "La lluvia anual ({l} mm) cubre la demanda mínima de todos los cultivos sin riego extra.",
        "ben_temp": "Todos los cultivos están en su rango óptimo de temperatura.",
        "ben_ninguno": "Sin beneficios destacados con los datos disponibles.",
        # riesgos
        "rie_repite": "{a} se repite en ciclos seguidos: favorece plagas y desgasta el suelo.",
        "rie_familia": "{a} y {b} son de la misma familia ({f}) y van seguidos: favorece plagas y enfermedades.",
        "rie_cereal": "Después de {a} (cereal) no viene una leguminosa que reponga nitrógeno.",
        "rie_lluvia_baja": "{n} necesita al menos {r} mm/año y la zona recibe {l} mm: podría requerir riego.",
        "rie_lluvia_alta": "La lluvia ({l} mm) supera el óptimo de {n} ({r} mm): riesgo de encharcamiento y enfermedades.",
        "rie_temp": "La temperatura media ({t} °C) está fuera del óptimo de {n} ({a}–{b} °C).",
        "rie_helada": "{n} sufre daño por helada bajo {k} °C y la mínima registrada fue {m} °C.",
        "rie_calor": "{n} tolera hasta {x} °C y se registraron {m} °C.",
        "rie_ninguno": "No se detectaron riesgos climáticos con los datos disponibles.",
        # vacíos
        "vac_suelo": "No conocemos el análisis de suelo de tu finca (pH, textura, materia orgánica).",
        "vac_celdas": "NASA POWER usa celdas de unos 50 km: no capta la altitud exacta ni los microclimas de la finca.",
        "vac_precios": "Los precios de economía son los que reciben los productores en Estados Unidos (USDA NASS, "
                       "USD/kg), no precios de Colombia, y no incluyen costos de producción.",
        "vac_sin_precio": "Sin precio de referencia para: {lista}; se usó un valor neutro en economía.",
        "vac_maquinaria": "La maquinaria se estima con FAO GAEZ (rendimiento con insumos altos y mecanización frente a "
                          "trabajo manual); no es un inventario de equipos ni de su costo.",
        "vac_sin_maquinaria": "FAO GAEZ no tiene datos de maquinaria para: {lista}; se usó un valor neutro en equipos.",
        "vac_aporte": "El aporte al suelo de los cultivos no leguminosos aún no está documentado.",
        "vac_helada": "EcoCrop no reporta temperatura de helada para: {lista}.",
        "vac_variedades": "Los rangos de EcoCrop son de la especie, no de las variedades locales.",
        "vac_mercado": "Precios locales y demanda de mercado no incluidos.",
    },
    "en": {
        "y": " and ",
        "porque_actual": "This is the rotation you use today; it serves as the baseline (average climate suitability {apt}).",
        "porque_prioridad": "scores {v} out of 1 on your top priority ({etiqueta})",
        "porque_leguminosa": "includes {lista}, which fixes nitrogen",
        "porque_familia": "changes plant family every cycle",
        "porque_aptitud": "its crops have an average climate suitability of {apt} at your location",
        "porque_inicio": "Suggested because it ",
        "porque_exigente": ". Note: your location's climate is demanding for the whole catalog (average suitability "
                           "{apt}); these are the options closest to their ranges.",
        "lluvia_dato": "Annual rainfall", "lluvia_unidad": "mm/year",
        "lluvia_ok": "Within EcoCrop's optimal rainfall range for all crops.",
        "lluvia_bajo": "Below EcoCrop's optimum for: {lista}.",
        "lluvia_alto": "Above EcoCrop's optimum for: {lista}.",
        "temp_dato": "Mean temperature",
        "temp_fuera": "Outside EcoCrop's optimal range for: {lista}.",
        "temp_ok": "Within EcoCrop's optimal temperature range for all crops.",
        "tmin_dato": "Lowest recorded temperature",
        "tmin_bajo": "Below EcoCrop's frost threshold for: {lista}.",
        "tmin_ok": "Above EcoCrop's frost threshold for the crops that report one.",
        "calor_dato": "Extreme heat days (>35 °C)", "calor_unidad": "days/year",
        "calor_nota": "Highest recorded temperature: {t} °C.",
        "humedad_dato": "Root-zone soil moisture", "humedad_unidad": "fraction 0–1",
        "humedad_seco": "Dry soil in the root zone: drought-tolerant crops are preferable.",
        "humedad_humedo": "Very wet soil in the root zone: watch out for waterlogging.",
        "humedad_media": "Moderate moisture in the root zone.",
        "ben_conocida": "You already know how to manage it.",
        "ben_nitrogeno": "{n} fixes nitrogen: it can reduce fertilizer for the next crop.",
        "ben_familias": "Different families ({lista}): breaks pest and disease cycles.",
        "ben_lluvia": "Annual rainfall ({l} mm) covers every crop's minimum demand without extra irrigation.",
        "ben_temp": "All crops are within their optimal temperature range.",
        "ben_ninguno": "No notable benefits with the available data.",
        "rie_repite": "{a} repeats in consecutive cycles: it encourages pests and depletes the soil.",
        "rie_familia": "{a} and {b} belong to the same family ({f}) and follow each other: it encourages pests and diseases.",
        "rie_cereal": "{a} (a cereal) is not followed by a legume to restore nitrogen.",
        "rie_lluvia_baja": "{n} needs at least {r} mm/year and the area receives {l} mm: it may need irrigation.",
        "rie_lluvia_alta": "Rainfall ({l} mm) exceeds the optimum for {n} ({r} mm): risk of waterlogging and disease.",
        "rie_temp": "Mean temperature ({t} °C) is outside the optimum for {n} ({a}–{b} °C).",
        "rie_helada": "{n} suffers frost damage below {k} °C and the recorded minimum was {m} °C.",
        "rie_calor": "{n} tolerates up to {x} °C and {m} °C was recorded.",
        "rie_ninguno": "No climate risks detected with the available data.",
        "vac_suelo": "We don't have your farm's soil analysis (pH, texture, organic matter).",
        "vac_celdas": "NASA POWER uses cells of about 50 km: it doesn't capture the farm's exact altitude or microclimates.",
        "vac_precios": "Economy prices are those received by producers in the United States (USDA NASS, USD/kg), "
                       "not Colombian prices, and they don't include production costs.",
        "vac_sin_precio": "No reference price for: {lista}; a neutral value was used for economy.",
        "vac_maquinaria": "Machinery is estimated with FAO GAEZ (high-input, mechanized yield vs. manual labor); "
                          "it is not an inventory of equipment or its cost.",
        "vac_sin_maquinaria": "FAO GAEZ has no machinery data for: {lista}; a neutral value was used for equipment.",
        "vac_aporte": "The soil contribution of non-legume crops is not documented yet.",
        "vac_helada": "EcoCrop reports no frost temperature for: {lista}.",
        "vac_variedades": "EcoCrop ranges are for the species, not for local varieties.",
        "vac_mercado": "Local prices and market demand are not included.",
    },
}


def _t(ctx, clave, **valores):
    return TEXTOS[ctx["idioma"]][clave].format(**valores)


def _n(ctx, c):
    """Nombre del cultivo en el idioma de la respuesta."""
    return c.get("nombre_en", c["nombre"]) if ctx["idioma"] == "en" else c["nombre"]


def _lista(ctx, nombres):
    nombres = list(dict.fromkeys(nombres))  # sin repetidos, conservando el orden
    if len(nombres) == 1:
        return nombres[0]
    return ", ".join(nombres[:-1]) + TEXTOS[ctx["idioma"]]["y"] + nombres[-1]


def _fuera_optimo_temp(c, t):
    return c["topmn"] is not None and not (c["topmn"] <= t <= c["topmx"])


def porque(ctx):
    sec, apt = ctx["secuencia"], ctx["aptitudes"]
    apt_media = f"{mean(max(0.0, apt[c['id']]) for c in sec):.0%}"
    if ctx["actual"]:
        return _t(ctx, "porque_actual", apt=apt_media)

    partes = []
    if ctx["prioridades"]:
        p = ctx["prioridades"][0]
        partes.append(_t(ctx, "porque_prioridad", v=f"{ctx['subpuntajes'][p]:.2f}",
                         etiqueta=ETIQUETAS[ctx["idioma"]][p]))
    leguminosas = [_n(ctx, c) for c in sec if c["fija_nitrogeno"]]
    if leguminosas:
        partes.append(_t(ctx, "porque_leguminosa", lista=_lista(ctx, leguminosas)))
    partes.append(_t(ctx, "porque_familia"))
    if mean(max(0.0, apt[c["id"]]) for c in sec) >= 0.5:
        partes.append(_t(ctx, "porque_aptitud", apt=apt_media))
        return _t(ctx, "porque_inicio") + _lista(ctx, partes) + "."
    return _t(ctx, "porque_inicio") + _lista(ctx, partes) + _t(ctx, "porque_exigente", apt=apt_media)


def evidencia(ctx):
    sec, clima = ctx["secuencia"], ctx["clima"]
    lluvia, t = clima["lluvia_anual_mm"], clima["temp_media_c"]
    items = []

    bajo = [f"{_n(ctx, c)} ({c['ropmn']:.0f} mm)" for c in sec if c["ropmn"] and lluvia < c["ropmn"]]
    alto = [f"{_n(ctx, c)} ({c['ropmx']:.0f} mm)" for c in sec if c["ropmx"] and lluvia > c["ropmx"]]
    if not bajo and not alto:
        nota = _t(ctx, "lluvia_ok")
    else:
        nota = " ".join(filter(None, [
            _t(ctx, "lluvia_bajo", lista=_lista(ctx, bajo)) if bajo else "",
            _t(ctx, "lluvia_alto", lista=_lista(ctx, alto)) if alto else "",
        ]))
    items.append({"dato": _t(ctx, "lluvia_dato"), "valor": lluvia, "unidad": _t(ctx, "lluvia_unidad"),
                  "fuente": "NASA POWER", "nota": nota})

    fuera = [f"{_n(ctx, c)} ({c['topmn']:.0f}–{c['topmx']:.0f} °C)" for c in sec if _fuera_optimo_temp(c, t)]
    nota = _t(ctx, "temp_fuera", lista=_lista(ctx, fuera)) if fuera else _t(ctx, "temp_ok")
    items.append({"dato": _t(ctx, "temp_dato"), "valor": t, "unidad": "°C", "fuente": "NASA POWER", "nota": nota})

    con_umbral = [c for c in sec if c["ktmp"] is not None]
    if con_umbral:
        t_min = clima["temp_min_abs_c"]
        sensibles = [f"{_n(ctx, c)} ({c['ktmp']:.0f} °C)" for c in con_umbral if t_min <= c["ktmp"]]
        nota = _t(ctx, "tmin_bajo", lista=_lista(ctx, sensibles)) if sensibles else _t(ctx, "tmin_ok")
        items.append({"dato": _t(ctx, "tmin_dato"), "valor": t_min, "unidad": "°C",
                      "fuente": "NASA POWER", "nota": nota})

    if clima["dias_calor"] > 0:
        items.append({"dato": _t(ctx, "calor_dato"), "valor": clima["dias_calor"], "unidad": _t(ctx, "calor_unidad"),
                      "fuente": "NASA POWER", "nota": _t(ctx, "calor_nota", t=clima["temp_max_abs_c"])})

    h = clima["humedad_suelo"]
    if h < 0.3:
        nota = _t(ctx, "humedad_seco")
    elif h > 0.7:
        nota = _t(ctx, "humedad_humedo")
    else:
        nota = _t(ctx, "humedad_media")
    items.append({"dato": _t(ctx, "humedad_dato"), "valor": h, "unidad": _t(ctx, "humedad_unidad"),
                  "fuente": "NASA POWER", "nota": nota})
    return items


def beneficios(ctx):
    sec, clima, subs = ctx["secuencia"], ctx["clima"], ctx["subpuntajes"]
    items = []
    if ctx["actual"]:
        items.append(_t(ctx, "ben_conocida"))
    for c in sec:
        if c["fija_nitrogeno"]:
            items.append(_t(ctx, "ben_nitrogeno", n=_n(ctx, c)))
    familias = [c["familia"] for c in sec]
    if not any(r["regla"] == "familia_repetida" for r in ctx["infracciones"]) and len(set(familias)) == len(sec):
        items.append(_t(ctx, "ben_familias", lista=_lista(ctx, familias)))
    if subs["agua"] >= 1:
        items.append(_t(ctx, "ben_lluvia", l=clima["lluvia_anual_mm"]))
    if not any(_fuera_optimo_temp(c, clima["temp_media_c"]) for c in sec):
        items.append(_t(ctx, "ben_temp"))
    return items or [_t(ctx, "ben_ninguno")]


def riesgos(ctx):
    sec, clima = ctx["secuencia"], ctx["clima"]
    lluvia, t = clima["lluvia_anual_mm"], clima["temp_media_c"]
    items = []

    vistos = set()
    for r in ctx["infracciones"]:
        a, b = r["a"], r["b"]
        if r["regla"] == "familia_repetida":
            par = frozenset((a["id"], b["id"]))
            if par in vistos:
                continue
            vistos.add(par)
            if a["id"] == b["id"]:
                items.append(_t(ctx, "rie_repite", a=_n(ctx, a)))
            else:
                items.append(_t(ctx, "rie_familia", a=_n(ctx, a), b=_n(ctx, b), f=a["familia"]))
        elif r["regla"] == "cereal_sin_leguminosa":
            items.append(_t(ctx, "rie_cereal", a=_n(ctx, a)))

    for c in sec:
        n = _n(ctx, c)
        if c["ropmn"] and lluvia < c["ropmn"]:
            items.append(_t(ctx, "rie_lluvia_baja", n=n, r=f"{c['ropmn']:.0f}", l=lluvia))
        if c["ropmx"] and lluvia > c["ropmx"]:
            items.append(_t(ctx, "rie_lluvia_alta", n=n, r=f"{c['ropmx']:.0f}", l=lluvia))
        if _fuera_optimo_temp(c, t):
            items.append(_t(ctx, "rie_temp", n=n, t=t, a=f"{c['topmn']:.0f}", b=f"{c['topmx']:.0f}"))
        if c["ktmp"] is not None and clima["temp_min_abs_c"] <= c["ktmp"]:
            items.append(_t(ctx, "rie_helada", n=n, k=f"{c['ktmp']:.0f}", m=clima["temp_min_abs_c"]))
        if c["tmax"] is not None and clima["temp_max_abs_c"] > c["tmax"]:
            items.append(_t(ctx, "rie_calor", n=n, x=f"{c['tmax']:.0f}", m=clima["temp_max_abs_c"]))

    return list(dict.fromkeys(items)) or [_t(ctx, "rie_ninguno")]


def vacios(ctx):
    sec = ctx["secuencia"]
    items = [_t(ctx, "vac_suelo"), _t(ctx, "vac_celdas")]
    if any(c.get("precio_usd_kg") is not None for c in sec):
        items.append(_t(ctx, "vac_precios"))
    sin_precio = [_n(ctx, c) for c in sec if c.get("precio_nivel") is None]
    if sin_precio:
        items.append(_t(ctx, "vac_sin_precio", lista=_lista(ctx, sin_precio)))
    if any(c["maquinaria"] is not None for c in sec):
        items.append(_t(ctx, "vac_maquinaria"))
    sin_maquinaria = [_n(ctx, c) for c in sec if c["maquinaria"] is None]
    if sin_maquinaria:
        items.append(_t(ctx, "vac_sin_maquinaria", lista=_lista(ctx, sin_maquinaria)))
    if any(c["aporte_suelo"] is None and not c["fija_nitrogeno"] for c in sec):
        items.append(_t(ctx, "vac_aporte"))
    sin_helada = [_n(ctx, c) for c in sec if c["ktmp"] is None]
    if sin_helada:
        items.append(_t(ctx, "vac_helada", lista=_lista(ctx, sin_helada)))
    items.append(_t(ctx, "vac_variedades"))
    items.append(_t(ctx, "vac_mercado"))
    return items


def armar(ctx):
    ctx = {"idioma": "es", **ctx}
    return {
        "porque": porque(ctx),
        "evidencia": evidencia(ctx),
        "beneficios": beneficios(ctx),
        "riesgos": riesgos(ctx),
        "vacios": vacios(ctx),
    }
