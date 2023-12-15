from django.shortcuts import render
from parcial3App.serializers import  LineaSerializer , ArticuloSerializer , PujaSerializer

import pymongo
import requests
import json

from datetime import datetime
from dateutil import parser

import cloudinary
import cloudinary.uploader

from django.http import HttpResponse

from bson import ObjectId
from rest_framework.response import Response

from django.http.response import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework import status

from google.oauth2 import id_token
from google.auth.transport import requests

from pymongo import ReturnDocument

from django.shortcuts import render, get_object_or_404

from parcial3App.serializers import TokenSerializer

# Conexión a la base de datos MongoDB
my_client = pymongo.MongoClient("mongodb+srv://usuario:usuario@cluster0.inp8hlj.mongodb.net/?retryWrites=true&w=majority")

# Nombre de la base de datos
dbname = my_client['PruebaExamen']

# Colecciones
collection_buses = dbname['Buses']
collection_articulos = dbname['Articulos']
collection_pujas = dbname['Pujas']

CLIENT_ID = '739979864172-bbrds0insroblueqf3grvncjuj4m3dca.apps.googleusercontent.com'
# ----------------------------------------  VISTAS DE LA APLICACIÓN ------------------------------

@api_view(['POST'])
def oauth(request):
    if request.method == 'POST':
        serializer = TokenSerializer(data=request.data)
        if serializer.is_valid():
            tokenData = serializer.validated_data
            try:
                token = tokenData['idtoken']
                # Specify the CLIENT_ID of the app that accesses the backend:
                idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)

                # Or, if multiple clients access the backend server:
                # idinfo = id_token.verify_oauth2_token(token, requests.Request())
                # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
                #     raise ValueError('Could not verify audience.')

                # If auth request is from a G Suite domain:
                # if idinfo['hd'] != GSUITE_DOMAIN_NAME:
                #     raise ValueError('Wrong hosted domain.')

                # ID token is valid. Get the user's Google Account ID from the decoded token.
                userid = idinfo['sub']
                if userid:
                    return Response({"userid": userid,},
                                    status=status.HTTP_200_OK)
            except ValueError:
                # Invalid token
                return Response({"error": "Token no valido",},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

#Devuelve solamente el numero de lineas
@api_view(['GET'])
def lineas(request):
    if request.method == 'GET':
        buses = list(collection_buses.find())
        lineas = []
        for bus in buses:
            if bus['codLinea'] not in lineas:
                lineas.append(bus['codLinea'])
        if lineas:
            print(lineas)
            return JsonResponse(lineas, status=status.HTTP_200_OK, safe=False)
        else :
            return JsonResponse({'message': 'No hay lineas'}, status=status.HTTP_404_NOT_FOUND)
        
#Devuelve el cojunto de latitudes y longitudes de una linea y sentido concreto
@api_view(['GET'])
def latlon(request, codLinea, sentido):
    if request.method == 'GET':
        print(codLinea,sentido)
        buses = list(collection_buses.find({"codLinea": int(codLinea), "sentido": int(sentido)}))
        print(buses)
        latlon = []
        for bus in buses:
            latlon.append([bus['lat'], bus['lon']])
        if latlon:
            return JsonResponse(latlon, status=status.HTTP_200_OK, safe=False)
        else :
            return JsonResponse({'message': 'No hay latitudes y longitudes'}, status=status.HTTP_404_NOT_FOUND)

#Devuelve el cojunto de latitudes y longitudes de una parada que contenga el string que se le pasa
@api_view(['GET'])
def form2(request, parada):
    if request.method == 'GET':
        print(parada)
        buses = list(collection_buses.find({"nombreParada": {"$regex": parada, "$options": "i"}}))
        paradas = []
        for bus in buses:
            paradas.append([bus['lat'], bus['lon']])
        if paradas:
            return JsonResponse(paradas, status=status.HTTP_200_OK, safe=False)
        else :
            return JsonResponse({'message': 'No hay paradas'}, status=status.HTTP_404_NOT_FOUND)
        
@api_view(['POST'])
def upload_image(request):
    if request.method == 'POST' and request.FILES.getlist('images'):
        uploaded_files = request.FILES.getlist('images')
        uploaded_urls = []

        # Upload each image to Cloudinary
        cloudinary.config(
                cloud_name="dxlqj1ldn",
                api_key="226898995815434",
                api_secret="i6cDmXohqmK8EzNu_-OI0OUs824"
            )

        for file in uploaded_files:
            upload_result = cloudinary.uploader.upload(
                file,
                folder='examen_ingweb'
            )
            uploaded_urls.append(upload_result['secure_url'])
        return JsonResponse({'urls': uploaded_urls})
    return HttpResponse(status=400)

# Devuelve todos los productos y permite crear un producto
@api_view(['GET', 'POST'])
def articulos_list(request):
    if request.method == 'GET':
        productos = list(collection_articulos.find({}).sort('fecha', pymongo.DESCENDING))        
        productos_serializer = ArticuloSerializer(data=productos, many= True)
        if productos_serializer.is_valid():
            json_data = productos_serializer.data
            return Response(json_data, status=status.HTTP_200_OK)
        else:
            return Response(productos_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'POST':
        serializer = ArticuloSerializer(data=request.data)
        if serializer.is_valid():
            producto = serializer.validated_data
            producto['identificador'] = str(ObjectId())
            producto['precioSalida'] = float(producto['precioSalida'])
            producto['comprador'] = "" 

            result = collection_articulos.insert_one(producto)
            if result.acknowledged:
                return Response({"message": "Producto creado con éxito."}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": "Algo salió mal. Producto no creado."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
# Buscar una lista de arituclos por descripción dada una cadena de texto concreta
@api_view(['GET'])
def articulos_list_descripcion(request, descripcion):
    if request.method == 'GET':
        productos = list(collection_articulos.find({"descripcion": {"$regex": descripcion, "$options": "i"}}).sort('fecha', pymongo.DESCENDING))
        productos_serializer = ArticuloSerializer(data=productos, many= True)
        if productos_serializer.is_valid():
            json_data = productos_serializer.data
            return Response(json_data, status=status.HTTP_200_OK)
        else:
            return Response(productos_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
# Devuelve un producto dada su identificador
@api_view(['GET'])
def articulos_detail(request, id):
    if request.method == 'GET':
        producto = collection_articulos.find_one({"identificador": id})
        producto_serializer = ArticuloSerializer(data=producto)
        if producto_serializer.is_valid():
            json_data = producto_serializer.data
            return Response(json_data, status=status.HTTP_200_OK)
        else:
            return Response(producto_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Devuelve todas las pujas dado un identificador de producto
@api_view(['GET'])
def pujas_list(request, id):
    if request.method == 'GET':
        pujas = list(collection_pujas.find({"identificador": id}).sort('cantidadOfrecida', pymongo.ASCENDING))
        pujas_serializer = PujaSerializer(data=pujas, many= True)
        if pujas_serializer.is_valid():
            json_data = pujas_serializer.data
            return Response(json_data, status=status.HTTP_200_OK)
        else:
            return Response(pujas_serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
        

# Devuelve la ultima puja dado un identificador de producto
@api_view(['GET'])
def pujas_last(request, id):
    if request.method == 'GET':
        pujas = list(collection_pujas.find({"identificador": id}).sort('cantidadOfrecida', pymongo.DESCENDING))
        pujas_serializer = PujaSerializer(data=pujas, many= True)
        if pujas_serializer.is_valid():
            json_data = pujas_serializer.data
            return Response(json_data[0], status=status.HTTP_200_OK)
        else:
            return Response(pujas_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

# Crea una puja
@api_view(['POST'])
def pujas_create(request):
    if request.method == 'POST':
        serializer = PujaSerializer(data=request.data)
        if serializer.is_valid():
            puja = serializer.validated_data
            puja['fecha'] = datetime.now()
            puja['cantidadOfrecida'] = float(puja['cantidadOfrecida']) 

            result = collection_pujas.insert_one(puja)
            if result.acknowledged:
                return Response({"message": "Puja creada con éxito."}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": "Algo salió mal. Puja no creada."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)