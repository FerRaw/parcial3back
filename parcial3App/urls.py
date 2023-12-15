from django.urls import path
from parcial3App import views

urlpatterns = [
    # PRODUCTOS
    path('logged', views.oauth),
    path('lineas/', views.lineas),
    path('lineas/<str:codLinea>/<str:sentido>/', views.latlon),
    path('paradas/<str:parada>/', views.form2),
    path('image/upload', views.upload_image),
    path('articulo/<str:id>/', views.articulos_detail),
    path('articulos/', views.articulos_list),
    path('articulos/create/', views.articulos_list),
    path('articulos/<str:descripcion>/', views.articulos_list_descripcion),
    path('pujas/producto/<str:id>/', views.pujas_list),
    path('pujas/create/', views.pujas_create),
    path('pujas/last/<str:id>/', views.pujas_last),
]