from rest_framework import serializers

class TokenSerializer(serializers.Serializer):
    idtoken = serializers.CharField()

class EventoSerializer(serializers.Serializer):
    _id = serializers.CharField(max_length = 24, required=False)
    nombre = serializers.CharField(max_length=200)
    timestamp = serializers.DateTimeField(required=False)
    lugar = serializers.CharField(max_length=200)
    lat = serializers.FloatField(required=False)
    lon = serializers.FloatField(required=False)
    organizador = serializers.CharField()
    imagen = serializers.ListField(child=serializers.CharField(allow_blank=False), required=False)
