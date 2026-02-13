'''
URL configuration for hippique app
'''
from django.urls import path
from . import views

app_name = 'hippique'

urlpatterns = [
    path('', views.turf_filter, name='turf_filter'),
    path('api/filtrer/', views.api_filtrer, name='api_filtrer'),
]
