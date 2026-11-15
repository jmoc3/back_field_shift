"""Resumen climático de un punto a partir de NASA POWER (usa extraer_historial.NasaPower)."""
from collections import defaultdict
from datetime import date, timedelta
from statistics import mean

from data.extraer_historial import NasaPower

# Últimos 10 años completos.
FECHA_INICIO = "20160101"
FECHA_FIN = "20251231"

UMBRAL_CALOR_C = 35  # T2M_MAX por encima de esto = día de calor extremo
UMBRAL_HELADA_C = 0  # T2M_MIN en o por debajo de esto = día de helada

_cliente = NasaPower()


def _por_anio(serie):
    grupos = defaultdict(list)
    for fecha, valor in serie.items():
        grupos[fecha[:4]].append(valor)
    return grupos


def _riesgo_helada(dias_helada_anio, temp_min_abs):
    if dias_helada_anio >= 5:
        return "alto"
    if dias_helada_anio > 0 or temp_min_abs <= 2:
        return "medio"
    return "bajo"


def obtener_clima(lat, lon):
    datos = _cliente.obtener_datos_historicos(lat, lon, FECHA_INICIO, FECHA_FIN)
    lluvia = datos["precipitacion"]
    t_max = datos["temperatura_maxima"]
    t_min = datos["temperatura_minima"]
    if not all(datos.values()):
        raise RuntimeError("NASA POWER no tiene datos válidos para esta ubicación.")
    anios = len(_por_anio(lluvia))

    # Lluvia: total anual promedio y total promedio por mes.
    lluvia_anual = mean(sum(v) for v in _por_anio(lluvia).values())
    por_mes = defaultdict(float)
    for fecha, valor in lluvia.items():
        por_mes[int(fecha[4:6])] += valor
    lluvia_mensual = [round(por_mes[m] / anios, 1) for m in range(1, 13)]

    dias_calor = sum(1 for v in t_max.values() if v > UMBRAL_CALOR_C) / anios
    dias_helada = sum(1 for v in t_min.values() if v <= UMBRAL_HELADA_C) / anios
    temp_min_abs = min(t_min.values())

    helada_por_mes = defaultdict(int)
    for fecha, valor in t_min.items():
        if valor <= UMBRAL_HELADA_C:
            helada_por_mes[int(fecha[4:6])] += 1
    dias_helada_mensual = [round(helada_por_mes[m] / anios, 1) for m in range(1, 13)]

    return {
        "lluvia_anual_mm": round(lluvia_anual),
        "lluvia_mensual_mm": lluvia_mensual,
        "dias_helada_mensual": dias_helada_mensual,
        "lluvia_media_mm_dia": round(mean(lluvia.values()), 1),
        "temp_media_c": round(mean(datos["temperatura"].values()), 1),
        "temp_max_abs_c": round(max(t_max.values()), 1),
        "temp_min_abs_c": round(temp_min_abs, 1),
        "dias_calor": round(dias_calor),
        "dias_helada": round(dias_helada),
        "riesgo_helada": _riesgo_helada(dias_helada, temp_min_abs),
        "humedad_suelo": round(mean(datos["humedad_raiz"].values()), 2),
        "periodo": f"{FECHA_INICIO[:4]}-{FECHA_FIN[:4]}",
        "fuente": "NASA POWER",
    }


def obtener_reciente(lat, lon, dias=7):
    """Últimos `dias` con dato (NASA POWER tiene unos 3 días de retraso) comparados con lo normal
    para esas mismas fechas en 2016-2025."""
    hoy = date.today()
    inicio = (hoy - timedelta(days=dias + 10)).strftime("%Y%m%d")
    recientes = _cliente.obtener_datos_historicos(lat, lon, inicio, hoy.strftime("%Y%m%d"))
    fechas = sorted(recientes["precipitacion"])[-dias:]
    if not fechas:
        raise RuntimeError("NASA POWER no tiene datos recientes para esta ubicación.")

    historico = _cliente.obtener_datos_historicos(lat, lon, FECHA_INICIO, FECHA_FIN)
    dias_mes = {f[4:] for f in fechas}  # MMDD

    lluvia_por_anio = defaultdict(float)
    humedad_hist = []
    for fecha, valor in historico["precipitacion"].items():
        if fecha[4:] in dias_mes:
            lluvia_por_anio[fecha[:4]] += valor
    for fecha, valor in historico["humedad_raiz"].items():
        if fecha[4:] in dias_mes:
            humedad_hist.append(valor)

    def _extremo(serie, funcion, condicion):
        valores = {f: serie[f] for f in fechas if f in serie and condicion(serie[f])}
        if not valores:
            return None
        f = funcion(valores, key=valores.get)
        return {"fecha": f"{f[:4]}-{f[4:6]}-{f[6:]}", "temp_c": round(valores[f], 1)}

    humedad = [recientes["humedad_raiz"][f] for f in fechas if f in recientes["humedad_raiz"]]
    return {
        "desde": f"{fechas[0][:4]}-{fechas[0][4:6]}-{fechas[0][6:]}",
        "hasta": f"{fechas[-1][:4]}-{fechas[-1][4:6]}-{fechas[-1][6:]}",
        "dias": len(fechas),
        "lluvia_mm": round(sum(recientes["precipitacion"][f] for f in fechas), 1),
        "lluvia_normal_mm": round(mean(lluvia_por_anio.values()), 1) if lluvia_por_anio else None,
        "humedad_suelo": round(mean(humedad), 2) if humedad else None,
        "humedad_normal": round(mean(humedad_hist), 2) if humedad_hist else None,
        "helada": _extremo(recientes["temperatura_minima"], min, lambda v: v <= UMBRAL_HELADA_C),
        "calor": _extremo(recientes["temperatura_maxima"], max, lambda v: v > UMBRAL_CALOR_C),
        "fuente": "NASA POWER",
    }
