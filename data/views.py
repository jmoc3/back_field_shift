import json
from pathlib import Path

from rest_framework.response import Response
from rest_framework.views import APIView


RUTA_CULTIVOS = Path(__file__).with_name("cultivos.json")


class CultivosView(APIView):
    def get(self, request):
        with RUTA_CULTIVOS.open(encoding="utf-8") as archivo:
            cultivos = json.load(archivo)

        # Con Accept-Language: en, "nombre" viene en inglés; el id no cambia
        if request.headers.get("Accept-Language", "").strip().lower().startswith("en"):
            cultivos = [{**c, "nombre": c.get("nombre_en", c["nombre"])} for c in cultivos]

        return Response(cultivos)
