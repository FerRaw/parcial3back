from django.urls import path
from parcial3App import views

urlpatterns = [
    # PRODUCTOS
    path('logged', views.oauth),
    path('eventos/', views.eventos_list),
    path('eventos/create/', views.eventos_list),
    path('eventos/update/<str:id>/', views.eventos_detail),
    path('eventos/delete/<str:id>/', views.eventos_delete),
    path('eventos/<str:id>/', views.eventos_detail),
    path('form/<str:cadena>/', views.form),
    path('image/upload', views.upload_image),
]