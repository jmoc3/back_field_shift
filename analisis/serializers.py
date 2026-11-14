from rest_framework import serializers

class AnalisisPeticionSerializer(serializers.Serializer):
    lat = serializers.FloatField(min_value=-90, max_value=90)
    lon = serializers.FloatField(min_value=-180, max_value=180)
    rotacion = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=False
    )
    prioridades = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=True
    )
    # Opcional por si el front envía el id_usuario para guardar las rotaciones después
    id_usuario = serializers.IntegerField(required=False)

    def validate(self, data):
        # Asegurar que lat y lon no lleguen como strings o booleanos
        raw_lat = self.initial_data.get("lat")
        raw_lon = self.initial_data.get("lon")
        if isinstance(raw_lat, bool) or not isinstance(raw_lat, (int, float)):
            raise serializers.ValidationError({"lat": "Debe ser un valor numérico."})
        if isinstance(raw_lon, bool) or not isinstance(raw_lon, (int, float)):
            raise serializers.ValidationError({"lon": "Debe ser un valor numérico."})
        return data