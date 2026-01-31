from django.urls import path
from . import views
from .views import auth, base, filters

urlpatterns = [
    # Page principale
    path('', base.index, name='index'),
    
    # Authentification admin
    path('admin/login/', auth.login_page, name='admin_login'),
    path('admin/logout/', auth.logout, name='admin_logout'),
    
    # API Authentification
    path('api/auth/login/', auth.login_api, name='api_login'),
    path('api/auth/check/', auth.check_auth, name='api_check_auth'),
    
    # API Filtrage (côté serveur)
    path('api/filter/', filters.api_filter_combinations, name='api_filter'),
    path('api/filter/check-access/', filters.api_check_filter_access, name='api_check_filter_access'),
    
    # API existantes
    path('api/combinations-count/', base.api_combinations_count, name='api_combinations_count'),
    path('api/parse-pronostics/', base.parse_pronostics, name='api_parse_pronostics'),
]
