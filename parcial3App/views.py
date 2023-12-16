from django.shortcuts import render
from parcial3App.serializers import  EventoSerializer

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

from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# Conexión a la base de datos MongoDB
my_client = pymongo.MongoClient("mongodb+srv://usuario:usuario@cluster0.inp8hlj.mongodb.net/?retryWrites=true&w=majority")

# Nombre de la base de datos
dbname = my_client['PruebaExamen']

# Colecciones
collection_eventos = dbname['Eventos']

CLIENT_ID = '1070292351809-53c621o3hvn65teqrbrai79uncdj9604.apps.googleusercontent.com'
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

#Lista todos los eventos y crea eventos
@api_view(['GET', 'POST'])
def eventos_list(request):
    if request.method == 'GET':
        eventos = list(collection_eventos.find({}).sort('timestamp', pymongo.DESCENDING))
        for evento in eventos:
            evento['_id'] = str(ObjectId(evento.get('_id',[])))
        eventos_serializer = EventoSerializer(data=eventos, many= True)
        if eventos_serializer.is_valid():
            json_data = eventos_serializer.data
            return Response(json_data, status=status.HTTP_200_OK)
        else:
            return Response(eventos_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'POST':
        serializer = EventoSerializer(data=request.data)
        if serializer.is_valid():
            evento = serializer.validated_data
            evento['_id'] = ObjectId()
            coordenadas = get_coordinates(evento['lugar'])
            evento['lat'] = float(coordenadas['latitud'])
            evento['lon'] = float(coordenadas['longitud'])
            print(evento)

            result = collection_eventos.insert_one(evento)
            if result.acknowledged:
                return Response({"message": "Evento creado con éxito."}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": "Algo salió mal. Evento no creado."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
# Modifica un evento dado su identificador
@api_view(['PUT'])
def eventos_detail(request, id):
    if request.method == 'PUT':
        evento = collection_eventos.find_one_and_update({"_id": ObjectId(id)}, {"$set": request.data}, return_document=ReturnDocument.AFTER)
        evento_serializer = EventoSerializer(data=evento)
        if evento_serializer.is_valid():
            json_data = evento_serializer.data
            return Response(json_data, status=status.HTTP_200_OK)
        else:
            return Response(evento_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
#Borra un evento dado su identificador
@api_view(['DELETE'])
def eventos_delete(request, id):
    if request.method == 'DELETE':
        result = collection_eventos.delete_one({"_id": ObjectId(id)})
        if result.acknowledged:
            return Response({"message": "Evento borrado con éxito."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Algo salió mal. Evento no borrado."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#Devuelve un evento dado su localización
@api_view(['GET'])
def eventos_detail(request, id):
    if request.method == 'GET':
        evento = collection_eventos.find_one({"lugar": id})
        evento['id'] = str(ObjectId(evento.get('_id',[])))
        evento_serializer = EventoSerializer(data=evento)
        if evento_serializer.is_valid():
            json_data = evento_serializer.data
            return Response(json_data, status=status.HTTP_200_OK)
        else:
            return Response(evento_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#Devuelve las coordendas dada una cadena
@api_view(['GET'])
def form(request, cadena):
        geolocator = Nominatim(user_agent="my_geocoder")
        # Obtiene las coordenadas geográficas de la dirección postal
        ubicacion = geolocator.geocode(cadena)
        coordenadas = (ubicacion.latitude, ubicacion.longitude)

        response_data = {
            'latitud': f"{coordenadas[0]}",
            'longitud': f"{coordenadas[1]}"
        }
        return JsonResponse(response_data, content_type='application/json', json_dumps_params={'ensure_ascii': False})

def get_coordinates(cadena):
    geolocator = Nominatim(user_agent="my_geocoder")
    ubicacion = geolocator.geocode(cadena)
    coordenadas = (ubicacion.latitude, ubicacion.longitude)

    return {
        'latitud': f"{coordenadas[0]}",
        'longitud': f"{coordenadas[1]}"
    }



