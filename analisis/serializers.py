from rest_framework import serializers


class AnalisisPeticionSerializer(serializers.Serializer):
    usuario_id = serializers.IntegerField(required=True)
    lat = serializers.FloatField()
    lon = serializers.FloatField()
    rotacion = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=False,
    )
    prioridades = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=True,
    )

    def validate(self, data):
        raw_usuario_id = self.initial_data.get("usuario_id")
        if isinstance(raw_usuario_id, bool) or not isinstance(raw_usuario_id, int):
            raise serializers.ValidationError({"usuario_id": "Debe ser un número entero."})

        raw_lat = self.initial_data.get("lat")
        raw_lon = self.initial_data.get("lon")
        if isinstance(raw_lat, bool) or not isinstance(raw_lat, (int, float)):
            raise serializers.ValidationError({"lat": "Debe ser un valor numérico."})
        if isinstance(raw_lon, bool) or not isinstance(raw_lon, (int, float)):
            raise serializers.ValidationError({"lon": "Debe ser un valor numérico."})

        return data