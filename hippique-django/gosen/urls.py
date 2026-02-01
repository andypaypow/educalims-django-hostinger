from django.urls import path
from . import views
from .views import base
from gosen.views.auth import login_page, logout_view, login_api, check_auth
from gosen.views.filters import api_filter_combinations, api_check_filter_access

urlpatterns = [
    # Page principale
    path('', base.index, name='index'),
    
    # Authentification admin
    path('admin/login/', login_page, name='admin_login'),
    path('admin/logout/', logout_view, name='admin_logout'),
    
    # API Authentification
    path('api/auth/login/', login_api, name='api_login'),
    path('api/auth/check/', check_auth, name='api_check_auth'),
    
    # API Filtrage (côté serveur)
    path('api/filter/', api_filter_combinations, name='api_filter'),
    path('api/filter/check-access/', api_check_filter_access, name='api_check_filter_access'),
    
    # API existantes
    path('api/combinations-count/', base.api_combinations_count, name='api_combinations_count'),
    path('api/parse-pronostics/', base.parse_pronostics, name='api_parse_pronostics'),
]
