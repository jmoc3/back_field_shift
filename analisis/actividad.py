"""Actividad reciente para la pantalla de Inicio: historial de la finca + clima reciente + temporada."""
from datetime import date
from statistics import mean

from data.nasa_power import obtener_clima, obtener_reciente

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]


def _fecha_legible(iso):
    anio, mes, dia = iso.split("-")
    return f"{int(dia)} de {MESES[int(mes) - 1]}"


def _nivel_humedad(h):
    return "baja" if h < 0.3 else "alta" if h > 0.7 else "media"


def _historial(usuario):
    """Idea 3: último estado guardado en la tabla rotaciones."""
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
        detalle = opciones[0]["nombre"] + (f" y {extra} alternativa{'s' if extra > 1 else ''} más" if extra else "")
        return [{"tipo": "analisis", "titulo": "Análisis de rotaciones realizado", "detalle": detalle,
                 "fecha": fecha, "fuente": "Tu finca"}]

    actual = next((r for r in activas if r.data.get("id") == "actual"), activas[0])
    return [{"tipo": "rotacion", "titulo": "Rotación actual registrada", "detalle": actual.rotacion,
             "fecha": fecha, "fuente": "Tu finca"}]


def _clima_reciente(lat, lon):
    """Idea 1: últimos 7 días comparados con lo normal para esas fechas."""
    r = obtener_reciente(lat, lon)
    items = []

    lluvia, normal = r["lluvia_mm"], r["lluvia_normal_mm"]
    if normal:
        cambio = round((lluvia - normal) / normal * 100)
        comparacion = ("igual a lo normal" if cambio == 0 else
                       f"{abs(cambio)} % {'más' if cambio > 0 else 'menos'} que lo normal")
        detalle = f"{lluvia} mm · {comparacion} para esta época"
    else:
        detalle = f"{lluvia} mm · normalmente no llueve en esta época"
    items.append({"tipo": "lluvia", "titulo": f"Lluvia de los últimos {r['dias']} días", "detalle": detalle,
                  "fecha": r["hasta"], "fuente": r["fuente"]})

    if r["humedad_suelo"] is not None and r["humedad_normal"] is not None:
        items.append({
            "tipo": "humedad",
            "titulo": "Humedad del suelo esta semana",
            "detalle": (f"{_nivel_humedad(r['humedad_suelo']).capitalize()} ({r['humedad_suelo']}) "
                        f"frente a su promedio ({r['humedad_normal']})"),
            "fecha": r["hasta"], "fuente": r["fuente"],
        })

    if r["helada"]:
        items.append({"tipo": "helada", "titulo": "Helada registrada",
                      "detalle": f"{r['helada']['temp_c']} °C el {_fecha_legible(r['helada']['fecha'])}",
                      "fecha": r["helada"]["fecha"], "fuente": r["fuente"]})
    if r["calor"]:
        items.append({"tipo": "calor", "titulo": "Calor extremo registrado",
                      "detalle": f"{r['calor']['temp_c']} °C el {_fecha_legible(r['calor']['fecha'])}",
                      "fecha": r["calor"]["fecha"], "fuente": r["fuente"]})
    return items


def _temporada(lat, lon, hoy):
    """Idea 2: qué suele pasar el mes que viene según 2016-2025."""
    clima = obtener_clima(lat, lon)
    anio, mes = (hoy.year + 1, 1) if hoy.month == 12 else (hoy.year, hoy.month + 1)
    nombre = MESES[mes - 1].capitalize()
    lluvia_mes = clima["lluvia_mensual_mm"][mes - 1]
    promedio = mean(clima["lluvia_mensual_mm"])
    fecha = f"{anio}-{mes:02d}"
    items = []

    if lluvia_mes < 0.5 * promedio:
        titulo, consejo = f"{nombre} suele ser seco", "planea riego o un cultivo tolerante a sequía"
    elif lluvia_mes > 1.5 * promedio:
        titulo, consejo = f"{nombre} suele ser muy lluvioso", "atención a encharcamiento y enfermedades"
    else:
        titulo, consejo = f"{nombre} suele tener lluvia normal", "sin cambios fuertes frente al resto del año"
    items.append({"tipo": "temporada", "titulo": titulo,
                  "detalle": f"{lluvia_mes:.0f} mm en promedio (el mes típico tiene {promedio:.0f} mm): {consejo}",
                  "fecha": fecha, "fuente": clima["fuente"]})

    dias_helada = clima["dias_helada_mensual"][mes - 1]
    if dias_helada >= 1:
        items.append({"tipo": "helada", "titulo": f"Riesgo de helada en {MESES[mes - 1]}",
                      "detalle": f"{dias_helada:.0f} días de helada en promedio: protege o evita cultivos sensibles",
                      "fecha": fecha, "fuente": clima["fuente"]})
    return items


def armar_actividad(usuario, lat, lon, hoy=None):
    items = _historial(usuario)
    try:
        items += _clima_reciente(lat, lon)
        items += _temporada(lat, lon, hoy or date.today())
    except RuntimeError:
        pass  # Si NASA POWER falla se devuelve al menos el historial.
    return {"version": "1.0", "actividad": items}
