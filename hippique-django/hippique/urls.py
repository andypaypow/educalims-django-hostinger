"""
URL configuration for hippique app
"""
from django.urls import path
from . import views

app_name = 'hippique'

urlpatterns = [
    path('', views.turf_filter, name='turf_filter'),
    path('api/filtrer/', views.api_filtrer, name='api_filtrer'),
    path('api/sauvegarder/', views.api_sauvegarder_scenario, name='api_sauvegarder'),
    path('api/charger/<int:scenario_id>/', views.api_charger_scenario, name='api_charger'),
    path('api/scenarios/', views.api_liste_scenarios, name='api_liste_scenarios'),
    path('api/supprimer/<int:scenario_id>/', views.api_supprimer_scenario, name='api_supprimer'),
    path('api/favori/<int:scenario_id>/', views.api_toggle_favorite, name='api_toggle_favorite'),
]
