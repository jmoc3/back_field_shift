from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from rotaciones.models import Rotacion
from usuarios.models import Usuario
from .rotacion import analizar
from .actividad import armar_actividad
from .serializers import ActividadPeticionSerializer, AnalisisPeticionSerializer


class AnalisisView(APIView):
    def post(self, request):
        serializer = AnalisisPeticionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        datos = serializer.validated_data

        try:
            usuario = Usuario.objects.get(id=datos["usuario_id"])
        except Usuario.DoesNotExist:
            return Response(
                {"usuario_id": "No existe un usuario con ese ID."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            respuesta = analizar(
                datos["lat"],
                datos["lon"],
                datos["rotacion"],
                datos["prioridades"],
            )
        except ValueError as error:
            return Response({"rotacion": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        except RuntimeError as error:
            return Response({"detalle": str(error)}, status=status.HTTP_502_BAD_GATEWAY)

        # Desactivar todas las previas y reactivar/insertar exactamente las 3 del resultado
        with transaction.atomic():
            Rotacion.objects.filter(usuario=usuario, activa=True).update(activa=False)

            for opcion in respuesta["opciones"]:
                Rotacion.objects.update_or_create(
                    usuario=usuario,
                    rotacion=opcion["nombre"],
                    defaults={
                        "activa": True,
                        "data": opcion,
                    },
                )

        return Response(respuesta, status=status.HTTP_200_OK)

class ActividadView(APIView):
    def get(self, request):
        serializer = ActividadPeticionSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        datos = serializer.validated_data
        try:
            usuario = Usuario.objects.get(id=datos["usuario_id"])
        except Usuario.DoesNotExist:
            return Response(
                {"usuario_id": "No existe un usuario con ese ID."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(armar_actividad(usuario, datos["lat"], datos["lon"]), status=status.HTTP_200_OK)
