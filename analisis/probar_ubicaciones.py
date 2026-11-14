"""Prueba manual con 3 ubicaciones contrastantes.

Uso (desde la raíz del proyecto):  python -m analisis.probar_ubicaciones
"""
import json

from analisis.rotacion import analizar
from data.nasa_power import obtener_clima

UBICACIONES = [
    ("Seca - Ica, Perú", -14.07, -75.73, ["maiz", "maiz", "algodon"], ["agua", "suelo", "economia", "equipos"]),
    ("Lluviosa - Quibdó, Chocó", 5.69, -76.66, ["arroz", "arroz", "maiz"], ["suelo", "agua", "economia", "equipos"]),
    ("Fría - Puno, Perú", -15.84, -70.02, ["papa", "papa", "cebada"], ["suelo", "economia", "agua", "equipos"]),
]

if __name__ == "__main__":
    for nombre, lat, lon, rotacion, prioridades in UBICACIONES:
        clima = obtener_clima(lat, lon)
        resultado = analizar(lat, lon, rotacion, prioridades, clima=clima)
        print(f"\n===== {nombre} =====")
        print({k: clima[k] for k in ("lluvia_anual_mm", "temp_media_c", "temp_min_abs_c", "temp_max_abs_c",
                                     "dias_calor", "riesgo_helada", "humedad_suelo")})
        for op in resultado["opciones"]:
            print(f"- [{op['id']}] {op['nombre']}  puntaje={op['puntaje']}")
            print(f"    porqué: {op['porque']}")
            for r in op["riesgos"]:
                print(f"    riesgo: {r}")
    print("\nRespuesta completa de la última ubicación:")
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
