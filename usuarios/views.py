from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from rotaciones.models import Rotacion
from .models import Usuario
from .serializers import LoginSerializer, RegistroSerializer, UsuarioUpdateSerializer


class RegistroView(APIView):
    def post(self, request):
        serializer = RegistroSerializer(data=request.data)
        if serializer.is_valid():
            usuario = serializer.save()
            return Response(
                {
                    "mensaje": "Usuario registrado correctamente",
                    "usuario": {
                        "id": usuario.id,
                        "nombre": usuario.nombre,
                        "correo": usuario.correo,
                        "ubicacion": usuario.ubicacion,
                        "hectareas": usuario.hectareas,
                    },
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        correo = serializer.validated_data["correo"]
        try:
            usuario = Usuario.objects.get(correo=correo)
            return Response(
                {
                    "mensaje": "Ingreso exitoso",
                    "usuario": {
                        "id": usuario.id,
                        "nombre": usuario.nombre,
                        "correo": usuario.correo,
                        "ubicacion": usuario.ubicacion,
                        "hectareas": usuario.hectareas,
                    },
                },
                status=status.HTTP_200_OK,
            )
        except Usuario.DoesNotExist:
            return Response(
                {"error": "El correo no está registrado"},
                status=status.HTTP_404_NOT_FOUND,
            )


class UsuarioView(APIView):
    def get(self, request):
        id_usuario = request.query_params.get("id_usuario")

        if not id_usuario:
            return Response(
                {"error": "Debes enviar el parámetro id_usuario."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            usuario = Usuario.objects.get(pk=id_usuario)
        except (Usuario.DoesNotExist, ValueError):
            return Response(
                {"error": "Usuario no encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        rotaciones_activas = list(
            usuario.rotaciones
            .filter(activa=True)
            .values("id", "rotacion", "activa", "data")
        )

        return Response(
            {
                "id": usuario.id,
                "nombre": usuario.nombre,
                "correo": usuario.correo,
                "ubicacion": usuario.ubicacion,
                "hectareas": usuario.hectareas,
                "rotaciones": rotaciones_activas,
            }
        )

    def patch(self, request):
        serializer = UsuarioUpdateSerializer(data=request.data)
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

        with transaction.atomic():
            campos_actualizados = []
            if "ubicacion" in datos:
                usuario.ubicacion = datos["ubicacion"]
                campos_actualizados.append("ubicacion")
            if "hectareas" in datos:
                usuario.hectareas = datos["hectareas"]
                campos_actualizados.append("hectareas")

            if campos_actualizados:
                usuario.save(update_fields=campos_actualizados)

            if "rotacion" in datos:
                nueva_rotacion = datos["rotacion"]
                Rotacion.objects.filter(usuario=usuario, activa=True).update(activa=False)

                rotacion_obj, creada = Rotacion.objects.get_or_create(
                    usuario=usuario,
                    rotacion=nueva_rotacion,
                    defaults={
                        "activa": True,
                        "data": {
                            "id": "actual",
                            "actual": True,
                            "nombre": nueva_rotacion,
                        },
                    },
                )
                if not creada:
                    data_existente = rotacion_obj.data if isinstance(rotacion_obj.data, dict) else {}
                    data_existente.update({
                        "id": "actual",
                        "actual": True,
                        "nombre": nueva_rotacion,
                    })
                    rotacion_obj.activa = True
                    rotacion_obj.data = data_existente
                    rotacion_obj.save(update_fields=["activa", "data"])

        rotacion_activa = (
            Rotacion.objects.filter(usuario=usuario, activa=True)
            .order_by("-id")
            .first()
        )

        return Response(
            {
                "mensaje": "Datos de la finca actualizados correctamente",
                "usuario": {
                    "id": usuario.id,
                    "nombre": usuario.nombre,
                    "correo": usuario.correo,
                    "ubicacion": usuario.ubicacion,
                    "hectareas": usuario.hectareas,
                    "rotacion_actual": rotacion_activa.rotacion if rotacion_activa else None,
                },
            },
            status=status.HTTP_200_OK,
        )