"""Textos de cada opción armados con plantillas a partir de los valores reales."""
from statistics import mean

ETIQUETAS = {"agua": "agua", "suelo": "salud del suelo", "economia": "precio de referencia", "equipos": "maquinaria"}


def _lista(nombres):
    nombres = list(dict.fromkeys(nombres))  # sin repetidos, conservando el orden
    return nombres[0] if len(nombres) == 1 else ", ".join(nombres[:-1]) + " y " + nombres[-1]


def _fuera_optimo_temp(c, t):
    return c["topmn"] is not None and not (c["topmn"] <= t <= c["topmx"])


def porque(ctx):
    sec, apt = ctx["secuencia"], ctx["aptitudes"]
    apt_media = mean(max(0.0, apt[c["id"]]) for c in sec)
    if ctx["actual"]:
        return (f"Es la rotación que usas hoy; sirve de punto de comparación "
                f"(aptitud climática media {apt_media:.0%}).")

    partes = []
    if ctx["prioridades"]:
        p = ctx["prioridades"][0]
        partes.append(f"puntúa {ctx['subpuntajes'][p]:.2f} de 1 en tu prioridad principal ({ETIQUETAS[p]})")
    leguminosas = [c["nombre"] for c in sec if c["fija_nitrogeno"]]
    if leguminosas:
        partes.append(f"incluye {_lista(leguminosas)}, que fija nitrógeno")
    partes.append("cambia de familia en cada ciclo")
    if apt_media >= 0.5:
        partes.append(f"sus cultivos tienen una aptitud climática media de {apt_media:.0%} en tu ubicación")
        return "Se sugiere porque " + _lista(partes) + "."
    return ("Se sugiere porque " + _lista(partes) + ". Ojo: el clima de tu ubicación es exigente para todo el "
            f"catálogo (aptitud media {apt_media:.0%}); son las opciones menos alejadas de sus rangos.")


def evidencia(ctx):
    sec, clima = ctx["secuencia"], ctx["clima"]
    lluvia, t = clima["lluvia_anual_mm"], clima["temp_media_c"]
    items = []

    bajo = [f"{c['nombre']} ({c['ropmn']:.0f} mm)" for c in sec if c["ropmn"] and lluvia < c["ropmn"]]
    alto = [f"{c['nombre']} ({c['ropmx']:.0f} mm)" for c in sec if c["ropmx"] and lluvia > c["ropmx"]]
    if not bajo and not alto:
        nota = "Dentro del rango de lluvia óptimo de EcoCrop para todos los cultivos."
    else:
        nota = " ".join(filter(None, [
            f"Por debajo del óptimo de EcoCrop para: {_lista(bajo)}." if bajo else "",
            f"Por encima del óptimo de EcoCrop para: {_lista(alto)}." if alto else "",
        ]))
    items.append({"dato": "Lluvia anual", "valor": lluvia, "unidad": "mm/año", "fuente": "NASA POWER", "nota": nota})

    fuera = [f"{c['nombre']} ({c['topmn']:.0f}–{c['topmx']:.0f} °C)" for c in sec if _fuera_optimo_temp(c, t)]
    nota = (f"Fuera del rango óptimo de EcoCrop para: {_lista(fuera)}." if fuera
            else "Dentro del rango de temperatura óptimo de EcoCrop para todos los cultivos.")
    items.append({"dato": "Temperatura media", "valor": t, "unidad": "°C", "fuente": "NASA POWER", "nota": nota})

    con_umbral = [c for c in sec if c["ktmp"] is not None]
    if con_umbral:
        t_min = clima["temp_min_abs_c"]
        sensibles = [f"{c['nombre']} ({c['ktmp']:.0f} °C)" for c in con_umbral if t_min <= c["ktmp"]]
        nota = (f"Por debajo del umbral de helada de EcoCrop para: {_lista(sensibles)}." if sensibles
                else "Por encima del umbral de helada de EcoCrop de los cultivos que lo reportan.")
        items.append({"dato": "Temperatura mínima registrada", "valor": t_min, "unidad": "°C",
                      "fuente": "NASA POWER", "nota": nota})

    if clima["dias_calor"] > 0:
        items.append({"dato": "Días de calor extremo (>35 °C)", "valor": clima["dias_calor"], "unidad": "días/año",
                      "fuente": "NASA POWER", "nota": f"Temperatura máxima registrada: {clima['temp_max_abs_c']} °C."})

    h = clima["humedad_suelo"]
    if h < 0.3:
        nota = "Suelo seco en la zona de raíces: conviene preferir cultivos tolerantes a sequía."
    elif h > 0.7:
        nota = "Suelo muy húmedo en la zona de raíces: atención al encharcamiento."
    else:
        nota = "Humedad moderada en la zona de raíces."
    items.append({"dato": "Humedad del suelo en raíces", "valor": h, "unidad": "fracción 0–1",
                  "fuente": "NASA POWER", "nota": nota})
    return items


def beneficios(ctx):
    sec, clima, subs = ctx["secuencia"], ctx["clima"], ctx["subpuntajes"]
    items = []
    if ctx["actual"]:
        items.append("Ya conoces su manejo.")
    for c in sec:
        if c["fija_nitrogeno"]:
            items.append(f"{c['nombre']} fija nitrógeno: puede reducir el fertilizante del cultivo siguiente.")
    familias = [c["familia"] for c in sec]
    if not any(r["regla"] == "familia_repetida" for r in ctx["infracciones"]) and len(set(familias)) == len(sec):
        items.append(f"Familias distintas ({_lista(familias)}): interrumpe ciclos de plagas y enfermedades.")
    if subs["agua"] >= 1:
        items.append(f"La lluvia anual ({clima['lluvia_anual_mm']} mm) cubre la demanda mínima de todos los "
                     f"cultivos sin riego extra.")
    if not any(_fuera_optimo_temp(c, clima["temp_media_c"]) for c in sec):
        items.append("Todos los cultivos están en su rango óptimo de temperatura.")
    return items or ["Sin beneficios destacados con los datos disponibles."]


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
                items.append(f"{a['nombre']} se repite en ciclos seguidos: favorece plagas y desgasta el suelo.")
            else:
                items.append(f"{a['nombre']} y {b['nombre']} son de la misma familia ({a['familia']}) y van "
                             f"seguidos: favorece plagas y enfermedades.")
        elif r["regla"] == "cereal_sin_leguminosa":
            items.append(f"Después de {a['nombre']} (cereal) no viene una leguminosa que reponga nitrógeno.")

    for c in sec:
        if c["ropmn"] and lluvia < c["ropmn"]:
            items.append(f"{c['nombre']} necesita al menos {c['ropmn']:.0f} mm/año y la zona recibe {lluvia} mm: "
                         f"podría requerir riego.")
        if c["ropmx"] and lluvia > c["ropmx"]:
            items.append(f"La lluvia ({lluvia} mm) supera el óptimo de {c['nombre']} ({c['ropmx']:.0f} mm): "
                         f"riesgo de encharcamiento y enfermedades.")
        if _fuera_optimo_temp(c, t):
            items.append(f"La temperatura media ({t} °C) está fuera del óptimo de {c['nombre']} "
                         f"({c['topmn']:.0f}–{c['topmx']:.0f} °C).")
        if c["ktmp"] is not None and clima["temp_min_abs_c"] <= c["ktmp"]:
            items.append(f"{c['nombre']} sufre daño por helada bajo {c['ktmp']:.0f} °C y la mínima registrada "
                         f"fue {clima['temp_min_abs_c']} °C.")
        if c["tmax"] is not None and clima["temp_max_abs_c"] > c["tmax"]:
            items.append(f"{c['nombre']} tolera hasta {c['tmax']:.0f} °C y se registraron "
                         f"{clima['temp_max_abs_c']} °C.")

    return list(dict.fromkeys(items)) or ["No se detectaron riesgos climáticos con los datos disponibles."]


def vacios(ctx):
    sec = ctx["secuencia"]
    items = [
        "No conocemos el análisis de suelo de tu finca (pH, textura, materia orgánica).",
        "NASA POWER usa celdas de unos 50 km: no capta la altitud exacta ni los microclimas de la finca.",
    ]
    con_precio = [c for c in sec if c.get("precio_usd_kg") is not None]
    if con_precio:
        items.append("Los precios de economía son los que reciben los productores en Estados Unidos (USDA NASS, "
                     "USD/kg), no precios de Colombia, y no incluyen costos de producción.")
    sin_precio = [c["nombre"] for c in sec if c.get("precio_nivel") is None]
    if sin_precio:
        items.append(f"Sin precio de referencia para: {_lista(sin_precio)}; se usó un valor neutro en economía.")
    if any(c["maquinaria"] is not None for c in sec):
        items.append("La maquinaria se estima con FAO GAEZ (rendimiento con insumos altos y mecanización frente a "
                     "trabajo manual); no es un inventario de equipos ni de su costo.")
    sin_maquinaria = [c["nombre"] for c in sec if c["maquinaria"] is None]
    if sin_maquinaria:
        items.append(f"FAO GAEZ no tiene datos de maquinaria para: {_lista(sin_maquinaria)}; "
                     f"se usó un valor neutro en equipos.")
    if any(c["aporte_suelo"] is None and not c["fija_nitrogeno"] for c in sec):
        items.append("El aporte al suelo de los cultivos no leguminosos aún no está documentado.")
    sin_helada = [c["nombre"] for c in sec if c["ktmp"] is None]
    if sin_helada:
        items.append(f"EcoCrop no reporta temperatura de helada para: {_lista(dict.fromkeys(sin_helada))}.")
    items.append("Los rangos de EcoCrop son de la especie, no de las variedades locales.")
    items.append("Precios locales y demanda de mercado no incluidos.")
    return items


def armar(ctx):
    return {
        "porque": porque(ctx),
        "evidencia": evidencia(ctx),
        "beneficios": beneficios(ctx),
        "riesgos": riesgos(ctx),
        "vacios": vacios(ctx),
    }
