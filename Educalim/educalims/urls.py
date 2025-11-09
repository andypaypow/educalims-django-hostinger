from django.urls import path
from . import views

app_name = 'educalims'

urlpatterns = [
    # Pages principales
    path('', views.home, name='home'),
    path('disciplines/', views.disciplines_list, name='disciplines_list'),
    path('discipline/<int:discipline_id>/', views.discipline_detail, name='discipline_detail'),
    path('discipline/<slug:slug>/', views.discipline_by_slug, name='discipline'),
    path('niveau/<int:niveau_id>/', views.niveau_detail, name='niveau_detail'),
    path('unite/<int:unite_id>/', views.unite_detail, name='unite_detail'),

    # Recherche
    path('search/', views.search, name='search'),

    # Page À propos
    path('about/', views.about, name='about'),
]