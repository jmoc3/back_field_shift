import re
from rest_framework import serializers
from data.ecocrop import cargar_cultivos
from rotaciones.models import Rotacion
from .models import Usuario


def _formatear_rotacion(valor):
    catalogo = {c["id"]: c["nombre"] for c in cargar_cultivos()}
    if isinstance(valor, list):
        partes = [str(p).strip() for p in valor if str(p).strip()]
    else:
        partes = [p.strip() for p in re.split(r"[,→>-]+", str(valor)) if p.strip()]

    nombres = [catalogo.get(p.lower(), p) for p in partes]
    return " → ".join(nombres)


class RegistroSerializer(serializers.ModelSerializer):
    rotacion = serializers.JSONField(write_only=True)

    class Meta:
        model = Usuario
        fields = ["id", "nombre", "correo", "ubicacion", "hectareas", "rotacion"]

    def validate_rotacion(self, value):
        formateada = _formatear_rotacion(value)
        if not formateada:
            raise serializers.ValidationError("Debes indicar al menos un cultivo en la rotación.")
        return formateada

    def create(self, validated_data):
        rotacion_inicial = validated_data.pop("rotacion")
        usuario = Usuario.objects.create(**validated_data)

        Rotacion.objects.create(
            usuario=usuario,
            rotacion=rotacion_inicial,
            activa=True,
            data={
                "id": "actual",
                "actual": True,
                "nombre": rotacion_inicial,
            },
        )
        return usuario


class LoginSerializer(serializers.Serializer):
    correo = serializers.EmailField()