"""Resumen climático de un punto a partir de NASA POWER (usa extraer_historial.NasaPower)."""
from collections import defaultdict
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

    return {
        "lluvia_anual_mm": round(lluvia_anual),
        "lluvia_mensual_mm": lluvia_mensual,
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
