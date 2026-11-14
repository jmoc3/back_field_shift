from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import AnalisisPeticionSerializer
from .rotacion import analizar

class AnalisisView(APIView):
    def post(self, request):
        serializer = AnalisisPeticionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        datos = serializer.validated_data
        try:
            respuesta = analizar(datos["lat"], datos["lon"], datos["rotacion"], datos["prioridades"])
        except ValueError as error:  # cultivo que no está en el catálogo
            return Response({"rotacion": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        except RuntimeError as error:  # NASA POWER no respondió
            return Response({"detalle": str(error)}, status=status.HTTP_502_BAD_GATEWAY)

        return Response(respuesta, status=status.HTTP_200_OK)
