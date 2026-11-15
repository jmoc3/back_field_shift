"""Actividad reciente para la pantalla de Inicio: historial de la finca + clima reciente + temporada."""
from datetime import date
from statistics import mean

from data.nasa_power import obtener_clima, obtener_reciente
from .idioma import nombre_rotacion, traducir_rotacion

MESES = {
    "es": ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
           "septiembre", "octubre", "noviembre", "diciembre"],
    "en": ["January", "February", "March", "April", "May", "June", "July", "August",
           "September", "October", "November", "December"],
}

TEXTOS = {
    "es": {
        "fecha": "{dia} de {mes}",
        "baja": "baja", "media": "media", "alta": "alta",
        "tu_finca": "Tu finca",
        "analisis_titulo": "Análisis de rotaciones realizado",
        "analisis_extra_1": " y 1 alternativa más", "analisis_extra_n": " y {n} alternativas más",
        "rotacion_titulo": "Rotación actual registrada",
        "igual": "igual a lo normal", "mas": "{p} % más que lo normal", "menos": "{p} % menos que lo normal",
        "lluvia_detalle": "{mm} mm · {comparacion} para esta época",
        "lluvia_sin_normal": "{mm} mm · normalmente no llueve en esta época",
        "lluvia_titulo": "Lluvia de los últimos {dias} días",
        "humedad_titulo": "Humedad del suelo esta semana",
        "humedad_detalle": "{nivel} ({h}) frente a su promedio ({normal})",
        "helada_titulo": "Helada registrada", "calor_titulo": "Calor extremo registrado",
        "extremo_detalle": "{t} °C el {fecha}",
        "seco": "{mes} suele ser seco", "seco_consejo": "planea riego o un cultivo tolerante a sequía",
        "lluvioso": "{mes} suele ser muy lluvioso", "lluvioso_consejo": "atención a encharcamiento y enfermedades",
        "normal": "{mes} suele tener lluvia normal", "normal_consejo": "sin cambios fuertes frente al resto del año",
        "temporada_detalle": "{mm} mm en promedio (el mes típico tiene {promedio} mm): {consejo}",
        "riesgo_helada_titulo": "Riesgo de helada en {mes}",
        "riesgo_helada_detalle": "{dias} días de helada en promedio: protege o evita cultivos sensibles",
    },
    "en": {
        "fecha": "{mes} {dia}",
        "baja": "low", "media": "medium", "alta": "high",
        "tu_finca": "Your farm",
        "analisis_titulo": "Rotation analysis completed",
        "analisis_extra_1": " and 1 more alternative", "analisis_extra_n": " and {n} more alternatives",
        "rotacion_titulo": "Current rotation recorded",
        "igual": "same as normal", "mas": "{p} % more than normal", "menos": "{p} % less than normal",
        "lluvia_detalle": "{mm} mm · {comparacion} for this time of year",
        "lluvia_sin_normal": "{mm} mm · it doesn't usually rain at this time of year",
        "lluvia_titulo": "Rainfall over the last {dias} days",
        "humedad_titulo": "Soil moisture this week",
        "humedad_detalle": "{nivel} ({h}) vs. its average ({normal})",
        "helada_titulo": "Frost recorded", "calor_titulo": "Extreme heat recorded",
        "extremo_detalle": "{t} °C on {fecha}",
        "seco": "{mes} is usually dry", "seco_consejo": "plan irrigation or a drought-tolerant crop",
        "lluvioso": "{mes} is usually very rainy", "lluvioso_consejo": "watch for waterlogging and disease",
        "normal": "{mes} usually has normal rainfall", "normal_consejo": "no big changes compared with the rest of the year",
        "temporada_detalle": "{mm} mm on average (a typical month has {promedio} mm): {consejo}",
        "riesgo_helada_titulo": "Frost risk in {mes}",
        "riesgo_helada_detalle": "{dias} frost days on average: protect or avoid sensitive crops",
    },
}


def _fecha_legible(iso, idioma):
    anio, mes, dia = iso.split("-")
    return TEXTOS[idioma]["fecha"].format(dia=int(dia), mes=MESES[idioma][int(mes) - 1])


def _nivel_humedad(h, idioma):
    return TEXTOS[idioma]["baja" if h < 0.3 else "alta" if h > 0.7 else "media"]


def _historial(usuario, idioma):
    """Idea 3: último estado guardado en la tabla rotaciones."""
    t = TEXTOS[idioma]
    activas = list(usuario.rotaciones.filter(activa=True))
    if not activas:
        return []
    fechas = [r.fecha for r in activas if getattr(r, "fecha", None)]  # requiere el campo `fecha`
    fecha = max(fechas).isoformat() if fechas else None

    opciones = sorted(
        (r.data for r in activas if str(r.data.get("id", "")).startswith("opcion")),
        key=lambda d: d["id"],
    )
    if opciones:
        extra = len(opciones) - 1
        # El nombre se arma con los ids para que salga en el idioma pedido, no en el del análisis guardado
        primera = opciones[0]
        nombre = nombre_rotacion(primera["cultivos"], idioma) if primera.get("cultivos") else primera["nombre"]
        sufijo = "" if not extra else t["analisis_extra_1"] if extra == 1 else t["analisis_extra_n"].format(n=extra)
        return [{"tipo": "analisis", "titulo": t["analisis_titulo"], "detalle": nombre + sufijo,
                 "fecha": fecha, "fuente": t["tu_finca"]}]

    actual = next((r for r in activas if r.data.get("id") == "actual"), activas[0])
    return [{"tipo": "rotacion", "titulo": t["rotacion_titulo"],
             "detalle": traducir_rotacion(actual.rotacion, idioma), "fecha": fecha, "fuente": t["tu_finca"]}]


def _clima_reciente(lat, lon, idioma):
    """Idea 1: últimos 7 días comparados con lo normal para esas fechas."""
    t = TEXTOS[idioma]
    r = obtener_reciente(lat, lon)
    items = []

    lluvia, normal = r["lluvia_mm"], r["lluvia_normal_mm"]
    if normal:
        cambio = round((lluvia - normal) / normal * 100)
        comparacion = (t["igual"] if cambio == 0 else
                       t["mas" if cambio > 0 else "menos"].format(p=abs(cambio)))
        detalle = t["lluvia_detalle"].format(mm=lluvia, comparacion=comparacion)
    else:
        detalle = t["lluvia_sin_normal"].format(mm=lluvia)
    items.append({"tipo": "lluvia", "titulo": t["lluvia_titulo"].format(dias=r["dias"]), "detalle": detalle,
                  "fecha": r["hasta"], "fuente": r["fuente"]})

    if r["humedad_suelo"] is not None and r["humedad_normal"] is not None:
        items.append({
            "tipo": "humedad",
            "titulo": t["humedad_titulo"],
            "detalle": t["humedad_detalle"].format(nivel=_nivel_humedad(r["humedad_suelo"], idioma).capitalize(),
                                                   h=r["humedad_suelo"], normal=r["humedad_normal"]),
            "fecha": r["hasta"], "fuente": r["fuente"],
        })

    if r["helada"]:
        items.append({"tipo": "helada", "titulo": t["helada_titulo"],
                      "detalle": t["extremo_detalle"].format(t=r["helada"]["temp_c"],
                                                             fecha=_fecha_legible(r["helada"]["fecha"], idioma)),
                      "fecha": r["helada"]["fecha"], "fuente": r["fuente"]})
    if r["calor"]:
        items.append({"tipo": "calor", "titulo": t["calor_titulo"],
                      "detalle": t["extremo_detalle"].format(t=r["calor"]["temp_c"],
                                                             fecha=_fecha_legible(r["calor"]["fecha"], idioma)),
                      "fecha": r["calor"]["fecha"], "fuente": r["fuente"]})
    return items


def _temporada(lat, lon, hoy, idioma):
    """Idea 2: qué suele pasar el mes que viene según 2016-2025."""
    t = TEXTOS[idioma]
    clima = obtener_clima(lat, lon)
    anio, mes = (hoy.year + 1, 1) if hoy.month == 12 else (hoy.year, hoy.month + 1)
    nombre = MESES[idioma][mes - 1].capitalize()
    lluvia_mes = clima["lluvia_mensual_mm"][mes - 1]
    promedio = mean(clima["lluvia_mensual_mm"])
    fecha = f"{anio}-{mes:02d}"
    items = []

    if lluvia_mes < 0.5 * promedio:
        clave = "seco"
    elif lluvia_mes > 1.5 * promedio:
        clave = "lluvioso"
    else:
        clave = "normal"
    items.append({"tipo": "temporada", "titulo": t[clave].format(mes=nombre),
                  "detalle": t["temporada_detalle"].format(mm=f"{lluvia_mes:.0f}", promedio=f"{promedio:.0f}",
                                                           consejo=t[clave + "_consejo"]),
                  "fecha": fecha, "fuente": clima["fuente"]})

    dias_helada = clima["dias_helada_mensual"][mes - 1]
    if dias_helada >= 1:
        items.append({"tipo": "helada", "titulo": t["riesgo_helada_titulo"].format(mes=MESES[idioma][mes - 1]),
                      "detalle": t["riesgo_helada_detalle"].format(dias=f"{dias_helada:.0f}"),
                      "fecha": fecha, "fuente": clima["fuente"]})
    return items


def armar_actividad(usuario, lat, lon, hoy=None, idioma="es"):
    items = _historial(usuario, idioma)
    try:
        items += _clima_reciente(lat, lon, idioma)
        items += _temporada(lat, lon, hoy or date.today(), idioma)
    except RuntimeError:
        pass  # Si NASA POWER falla se devuelve al menos el historial.
    return {"version": "1.0", "actividad": items}
