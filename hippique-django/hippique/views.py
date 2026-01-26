"""
Views for Hippique TurfFilter application
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.decorators import login_required
import json
from datetime import datetime

from .models import Scenario
from .formules import (
    generer_toutes_combinaisons,
    filtrer_combinaisons,
    formater_combinaison,
    calculer_frequence_chevaux,
    calculer_taux_filtrage,
)


def turf_filter(request):
    """
    Vue principale du filtre de combinaisons hippiques
    """
    # Récupérer les scénarios sauvegardés
    scenarios = Scenario.objects.all().order_by('-is_favorite', '-updated_at')[:10]

    context = {
        'scenarios': scenarios,
        'total_combinaisons': 8008,  # C(16,6) = 8008
    }
    return render(request, 'hippique/turf_filter.html', context)


@csrf_exempt
def api_filtrer(request):
    """
    API pour filtrer les combinaisons
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)

        # Générer toutes les combinaisons
        n = int(data.get('n_partants', 16))
        k = int(data.get('k_taille', 6))
        toutes_combinaisons = generer_toutes_combinaisons(n, k)

        # Récupérer les paramètres des filtres
        filtres = {
            'ou': data.get('filtres_ou', {}),
            'et': data.get('filtres_et', {}),
            'pairs_impairs': data.get('filtres_pairs_impairs', {}),
            'petits_suites': data.get('filtres_petits_suites', {}),
            'limitation': data.get('filtre_limitation', {}),
            'poids': data.get('filtre_poids', {}),
            'alternance': data.get('filtre_alternance', {}),
        }

        # Appliquer les filtres
        combinaisons_filtrees = filtrer_combinaisons(toutes_combinaisons, filtres)

        # Formater les combinaisons pour l'affichage
        combinaisons_formatees = [
            formater_combinaison(comb) for comb in combinaisons_filtrees
        ]

        # Calculer les fréquences
        frequence = calculer_frequence_chevaux(combinaisons_filtrees)

        # Calculer le taux de filtrage
        taux = calculer_taux_filtrage(len(toutes_combinaisons), len(combinaisons_filtrees))

        return JsonResponse({
            'combinaisons': combinaisons_formatees,
            'total': len(toutes_combinaisons),
            'conservees': len(combinaisons_filtrees),
            'taux_filtrage': taux,
            'frequence': frequence,
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def api_sauvegarder_scenario(request):
    """
    API pour sauvegarder un scénario
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)

        # Créer le scénario
        scenario = Scenario(
            nom=data.get('nom', 'Scénario sans nom'),
            description=data.get('description', ''),
            date_course=datetime.strptime(data.get('date_course', timezone.now().strftime('%Y-%m-%d')), '%Y-%m-%d').date(),
            nom_course=data.get('nom_course', ''),
            arrivee=data.get('arrivee', ''),
            filtres_ou=data.get('filtres_ou', {}),
            filtres_et=data.get('filtres_et', {}),
            filtres_pairs_impairs=data.get('filtres_pairs_impairs', {}),
            filtres_petits_suites=data.get('filtres_petits_suites', {}),
            filtre_limitation=data.get('filtre_limitation', {}),
            filtre_poids=data.get('filtre_poids', {}),
            filtre_alternance=data.get('filtre_alternance', {}),
            n_partants=int(data.get('n_partants', 16)),
            k_taille=int(data.get('k_taille', 6)),
            combinaisons_total=int(data.get('total', 8008)),
            combinaisons_conservees=int(data.get('conservees', 8008)),
            taux_filtrage=float(data.get('taux_filtrage', 0.0)),
            resultat={
                'combinaisons': data.get('combinaisons', [])[:100],  # Limiter à 100 pour la DB
            },
        )
        scenario.save()

        return JsonResponse({
            'success': True,
            'scenario_id': scenario.id,
            'message': 'Scénario sauvegardé avec succès'
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_charger_scenario(request, scenario_id):
    """
    API pour charger un scénario
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        scenario = get_object_or_404(Scenario, id=scenario_id)

        return JsonResponse({
            'success': True,
            'scenario': {
                'id': scenario.id,
                'nom': scenario.nom,
                'description': scenario.description,
                'date_course': scenario.date_course.strftime('%Y-%m-%d'),
                'nom_course': scenario.nom_course,
                'arrivee': scenario.arrivee,
                'filtres_ou': scenario.filtres_ou,
                'filtres_et': scenario.filtres_et,
                'filtres_pairs_impairs': scenario.filtres_pairs_impairs,
                'filtres_petits_suites': scenario.filtres_petits_suites,
                'filtre_limitation': scenario.filtre_limitation,
                'filtre_poids': scenario.filtre_poids,
                'filtre_alternance': scenario.filtre_alternance,
                'n_partants': scenario.n_partants,
                'k_taille': scenario.k_taille,
                'combinaisons_total': scenario.combinaisons_total,
                'combinaisons_conservees': scenario.combinaisons_conservees,
                'taux_filtrage': scenario.taux_filtrage,
                'resultat': scenario.resultat,
            }
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_liste_scenarios(request):
    """
    API pour lister tous les scénarios
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        scenarios = Scenario.objects.all().order_by('-is_favorite', '-updated_at')

        scenarios_data = []
        for scenario in scenarios:
            scenarios_data.append({
                'id': scenario.id,
                'nom': scenario.nom,
                'date_course': scenario.date_course.strftime('%Y-%m-%d'),
                'combinaisons_conservees': scenario.combinaisons_conservees,
                'taux_filtrage': scenario.taux_filtrage,
                'is_favorite': scenario.is_favorite,
            })

        return JsonResponse({
            'success': True,
            'scenarios': scenarios_data,
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_supprimer_scenario(request, scenario_id):
    """
    API pour supprimer un scénario
    """
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        scenario = get_object_or_404(Scenario, id=scenario_id)
        scenario.delete()

        return JsonResponse({
            'success': True,
            'message': 'Scénario supprimé avec succès'
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_toggle_favorite(request, scenario_id):
    """
    API pour basculer le favori d'un scénario
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        scenario = get_object_or_404(Scenario, id=scenario_id)
        scenario.is_favorite = not scenario.is_favorite
        scenario.save()

        return JsonResponse({
            'success': True,
            'is_favorite': scenario.is_favorite,
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
