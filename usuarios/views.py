from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Usuario
from .serializers import RegistroSerializer, LoginSerializer

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
            .values("id", "rotacion", "activa")
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
