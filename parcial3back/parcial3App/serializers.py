from rest_framework import serializers

class TokenSerializer(serializers.Serializer):
    idtoken = serializers.CharField()

class LineaSerializer(serializers.Serializer):
    _id = serializers.CharField(max_length = 24, required=False)
    codLinea = serializers.CharField(max_length = 10)
    nombreLinea = serializers.CharField(max_length = 50)
    sentido = serializers.IntegerField()
    nombreParada = serializers.CharField(max_length = 50)
    lon = serializers.FloatField()
    lat = serializers.FloatField()

class ArticuloSerializer(serializers.Serializer):
    identificador = serializers.CharField(max_length = 24, required=False)
    vendedor = serializers.CharField()
    descripcion = serializers.CharField()
    precioSalida = serializers.FloatField()
    imagenes = serializers.ListField(child=serializers.CharField())
    comprador = serializers.CharField(required=False, allow_blank=True)

class PujaSerializer(serializers.Serializer):
    identificador = serializers.CharField(max_length = 24, required=False)
    comprador = serializers.CharField()
    fecha = serializers.DateTimeField(required=False)
    cantidadOfrecida = serializers.FloatField()