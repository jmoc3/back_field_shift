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


class UsuarioUpdateSerializer(serializers.Serializer):
    usuario_id = serializers.IntegerField(required=True)
    ubicacion = serializers.CharField(max_length=255, required=False)
    hectareas = serializers.FloatField(required=False)
    rotacion = serializers.JSONField(required=False, write_only=True)

    def validate(self, data):
        raw_usuario_id = self.initial_data.get("usuario_id")
        if isinstance(raw_usuario_id, bool) or not isinstance(raw_usuario_id, int):
            raise serializers.ValidationError({"usuario_id": "Debe ser un número entero."})

        if "hectareas" in self.initial_data:
            raw_hectareas = self.initial_data.get("hectareas")
            if isinstance(raw_hectareas, bool) or not isinstance(raw_hectareas, (int, float)):
                raise serializers.ValidationError({"hectareas": "Debe ser un valor numérico."})

        return data

    def validate_rotacion(self, value):
        formateada = _formatear_rotacion(value)
        if not formateada:
            raise serializers.ValidationError("Debes indicar al menos un cultivo en la rotación.")
        return formateada