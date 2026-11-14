from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import AnalisisPeticionSerializer

class AnalisisView(APIView):
    def post(self, request):
        serializer = AnalisisPeticionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Respuesta mock exacta a respuesta.json para que el frontend trabaje
        respuesta_mock = {
            "version": "1.0",
            "clima": {
                "lluvia_anual_mm": 980,
                "temp_media_c": 14.2,
                "dias_calor": 3,
                "riesgo_helada": "medio",
                "humedad_suelo": 0.62,
                "fuente": "NASA POWER"
            },
            "opciones": [
                {
                    "id": "actual",
                    "actual": True,
                    "nombre": "Maíz → Maíz → Papa",
                    "cultivos": ["maiz", "maiz", "papa"],
                    "puntaje": 0.48,
                    "porque": "Es la rotación que usas hoy; sirve de punto de comparación.",
                    "evidencia": [],
                    "beneficios": ["Ya conoces el manejo"],
                    "riesgos": ["Dos ciclos de maíz seguidos favorecen plagas"],
                    "vacios": ["No conocemos el análisis de suelo de tu finca"]
                },
                {
                    "id": "opcion_1",
                    "actual": False,
                    "nombre": "Maíz → Frijol → Papa",
                    "cultivos": ["maiz", "frijol", "papa"],
                    "puntaje": 0.82,
                    "porque": "Rompe el maíz repetido e incluye una leguminosa que aporta nitrógeno.",
                    "evidencia": [
                        {
                            "dato": "Lluvia media",
                            "valor": 2.7,
                            "unidad": "mm/día",
                            "fuente": "NASA POWER",
                            "nota": "Cubre la demanda del frijol sin riego extra."
                        }
                    ],
                    "beneficios": ["Menos fertilizante", "Menos plagas del maíz"],
                    "riesgos": ["El frijol es sensible a heladas"],
                    "vacios": ["Precio local del frijol no incluido"]
                },
                {
                    "id": "opcion_2",
                    "actual": False,
                    "nombre": "Maíz → Arveja → Papa",
                    "cultivos": ["maiz", "arveja", "papa"],
                    "puntaje": 0.79,
                    "porque": "Alternativa leguminosa tolerante a temperaturas frescas.",
                    "evidencia": [
                        {
                            "dato": "Temperatura media",
                            "valor": 14.2,
                            "unidad": "°C",
                            "fuente": "NASA POWER",
                            "nota": "Rango térmico óptimo para arveja en clima frío."
                        }
                    ],
                    "beneficios": ["Fijación de nitrógeno", "Menor riesgo de helada que el frijol"],
                    "riesgos": ["Requiere tutorado en variedades volubles"],
                    "vacios": ["Disponibilidad de semilla certificada no verificada"]
                }
            ],
            "aviso": "Herramienta de apoyo: revisa estas opciones con un agrónomo local."
        }

        return Response(respuesta_mock, status=status.HTTP_200_OK)