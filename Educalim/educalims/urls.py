from django.urls import path
from . import views
from . import views_lecons
from . import views_paliers_parties

app_name = 'educalims'

urlpatterns = [
    # Pages principales
    path('', views.home, name='home'),
    path('disciplines/', views.disciplines_list, name='disciplines_list'),
    path('discipline/<int:discipline_id>/', views.discipline_detail, name='discipline_detail'),
    path('discipline/<slug:slug>/', views.discipline_by_slug, name='discipline'),
    path('discipline/<slug:slug>/<slug:cycle_type>/', views.discipline_cycle_detail, name='discipline_cycle'),
    path('niveau/<int:niveau_id>/', views.niveau_detail, name='niveau_detail'),
    path('niveau/<int:niveau_id>/hierarchie/', views.niveau_hierarchie, name='niveau_hierarchie'),

    # Recherche
    path('search/', views.search, name='search'),

    # Page À propos
    path('about/', views.about, name='about'),

    # API AJAX pour les formulaires dépendants
    path('get-cycles-by-discipline/', views.get_cycles_by_discipline, name='get_cycles_by_discipline'),
    path('get-niveaux-by-cycle-and-discipline/', views.get_niveaux_by_cycle_and_discipline, name='get_niveaux_by_cycle_and_discipline'),
    path('get-lecons-by-niveau/', views.get_lecons_by_niveau, name='get_lecons_by_niveau'),
    
    # Pages pour les leçons et chapitres
    path('lecon/<int:lecon_id>/', views_lecons.lecon_detail, name='lecon_detail'),
    path('chapitre/<int:chapitre_id>/', views.chapitre_detail, name='chapitre_detail'),
    
    # Pages pour les paliers et parties
    path('palier/<int:palier_id>/', views_paliers_parties.palier_detail, name='palier_detail'),
    path('partie/<int:partie_id>/', views_paliers_parties.partie_detail, name='partie_detail'),
    
    # API AJAX pour les leçons et chapitres
    path('get-lecons-by-chapitre/', views_lecons.get_lecons_by_chapitre, name='get_lecons_by_chapitre'),

    # API AJAX pour les contenus
    path('get-niveaux-by-discipline/', views.get_niveaux_by_discipline, name='get_niveaux_by_discipline'),
    path('get-unites-apprentissage-by-niveau/', views.get_unites_apprentissage_by_niveau, name='get_unites_apprentissage_by_niveau'),
    path('contenu/<int:contenu_id>/', views.contenu_detail, name='contenu_detail'),
    
    # API AJAX pour les paliers et parties
    path('get-paliers-by-niveau/', views_paliers_parties.get_paliers_by_niveau, name='get_paliers_by_niveau'),
    path('get-parties-by-niveau/', views_paliers_parties.get_parties_by_niveau, name='get_parties_by_niveau'),
]