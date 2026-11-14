from rest_framework import serializers
from .models import Usuario
from rotaciones.models import Rotacion

class RegistroSerializer(serializers.ModelSerializer):
    rotacion = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = ["id", "nombre", "correo", "ubicacion", "hectareas", "rotacion"]

    def create(self, validated_data):
        rotacion_inicial = validated_data.pop("rotacion")
        usuario = Usuario.objects.create(**validated_data)
        # Guardamos su rotación inicial como activa
        Rotacion.objects.create(
            usuario=usuario,
            rotacion=rotacion_inicial,
            activa=True
        )
        return usuario


class LoginSerializer(serializers.Serializer):
    correo = serializers.EmailField()