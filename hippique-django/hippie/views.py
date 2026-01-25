"""
Django Views for Hippique Filtering Application
Based on turboquinteplus architecture
"""
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .formules import (
    combinations_count,
    combination_generator,
    citation_synthesis,
    position_synthesis,
    expert_synthesis,
    filter_by_group_min_max,
    expert1_filter,
    expert2_filter,
    count_even_odd,
    count_small_large,
    get_longest_consecutive,
    calculate_combination_weight,
    build_weight_map,
    calculate_weight_bounds,
    calculate_alternances,
    max_alternances,
    results_synthesis,
    calculate_filtration_rate,
    find_matching_combinations,
    apply_all_filters,
)


# =============================================================================
# PAGE VIEWS
# =============================================================================

def home(request):
    """Page d'accueil avec l'interface de filtrage."""
    return render(request, 'hippie/home.html')


def turf_filter(request):
    """Page principale de l'application TurfFilter."""
    return render(request, 'hippie/turf_filter.html')


# =============================================================================
# API VIEWS
# =============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def api_combinations_count(request):
    """
    API: Calcule C(n, k) - nombre de combinaisons possibles.

    POST body:
        {
            "n": 16,  # nombre de partants
            "k": 6    # taille de la combinaison
        }
    """
    try:
        data = json.loads(request.body)
        n = int(data.get('n', 16))
        k = int(data.get('k', 6))

        if n < 8 or n > 20:
            return JsonResponse({'error': 'n must be between 8 and 20'}, status=400)
        if k < 2 or k > 7:
            return JsonResponse({'error': 'k must be between 2 and 7'}, status=400)
        if k > n:
            return JsonResponse({'error': 'k cannot be greater than n'}, status=400)

        count = combinations_count(n, k)
        return JsonResponse({
            'n': n,
            'k': k,
            'count': count,
            'count_formatted': f"{count:,}".replace(',', ' ')
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def api_parse_pronostics(request):
    """
    API: Parse le texte des pronostics et retourne les groupes.

    POST body:
        {
            "text": "Favoris: 1, 2, 3\nOutsiders: 4, 5, 6"
        }
    """
    try:
        data = json.loads(request.body)
        text = data.get('text', '')

        groups = []
        lines = text.strip().split('\n')

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            parts = line.split(':')
            if len(parts) > 1:
                name = parts[0].strip()
                horses_str = parts[1]
            else:
                name = f"Groupe {line_num}"
                horses_str = line

            horses = []
            if horses_str:
                found = horses_str.replace(',', ' ').replace('-', ' ').split()
                horses = sorted(set(int(h) for h in found if h.isdigit() and 1 <= int(h) <= 20))

            if horses:
                groups.append({
                    'name': name,
                    'horses': horses,
                    'min': 0,
                    'max': len(horses)
                })

        return JsonResponse({'groups': groups})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def api_synthesis(request):
    """
    API: Calcule les synthèses (citation, position).

    POST body:
        {
            "groups": [
                {"name": "G1", "horses": [1, 2, 3]},
                {"name": "G2", "horses": [2, 4, 6]}
            ]
        }
    """
    try:
        data = json.loads(request.body)
        groups = data.get('groups', [])

        citation = citation_synthesis(groups)
        position = position_synthesis(groups)

        return JsonResponse({
            'citation': [{'horse': h, 'count': c} for h, c in citation],
            'position': [{'horse': h, 'score': s} for h, s in position]
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def api_filter_combinations(request):
    """
    API: Applique tous les filtres et retourne les combinaisons filtrées.

    POST body:
        {
            "n": 16,
            "k": 6,
            "groups": [
                {"name": "G1", "horses": [1, 2, 3], "min": 1, "max": 2}
            ],
            "filters": {
                "expert1": [{"chevaux_min": 1, "groupes_min": 1}],
                "expert2": [{"chevaux_min": 1, "groupes_min": 1}],
                "even_odd": [{"min": 0, "max": 6}],
                "small_large": [{"limit": 10, "min": 0, "max": 6}],
                "consecutive": [{"min": 0, "max": 7}],
                "weight": [{"min": 21, "max": 81, "source": "default", "map": {...}}],
                "alternance": [{"min": 0, "max": 5, "source": "default"}]
            }
        }
    """
    try:
        data = json.loads(request.body)
        n = int(data.get('n', 16))
        k = int(data.get('k', 6))
        groups = data.get('groups', [])
        filters = data.get('filters', {})

        # Prepare weight filters - use map sent by frontend directly
        weight_filters = []
        for wf in filters.get('weight', []):
            # Frontend builds the weight map directly, use it
            weight_map = wf.get('map', {})
            # Convert string keys to int for proper handling
            if weight_map:
                weight_map = {int(k): v for k, v in weight_map.items()}
            weight_filters.append({
                'min': wf.get('min', 21),
                'max': wf.get('max', 81),
                'map': weight_map
            })

        # Prepare alternance filters - use sourceArray sent by frontend directly
        alternance_filters = []
        for af in filters.get('alternance', []):
            # Frontend builds the source array directly, use it
            source_array = af.get('sourceArray', af.get('source', []))
            # Convert to string array for alternance calculation
            if source_array and isinstance(source_array[0], int):
                source_array = [str(x) for x in source_array]
            alternance_filters.append({
                'min': af.get('min', 0),
                'max': af.get('max', max_alternances(k)),
                'source': source_array
            })

        # Apply all filters
        filtered = apply_all_filters(
            n=n,
            k=k,
            groups=groups,
            or_filters=filters.get('expert1', []),
            and_filters=filters.get('expert2', []),
            even_odd_filters=filters.get('even_odd', []),
            small_large_filters=filters.get('small_large', []),
            consecutive_filters=filters.get('consecutive', []),
            weight_filters=weight_filters,
            alternance_filters=alternance_filters
        )

        total = combinations_count(n, k)
        rate = calculate_filtration_rate(total, len(filtered))

        # Calculate results synthesis
        results = results_synthesis(filtered)

        # Calculate expert synthesis from groups and results
        expert = []
        if results and groups:
            citation_data = citation_synthesis(groups)
            position_data = position_synthesis(groups)
            results_data = [(r[0], r[1]) for r in results]
            expert = expert_synthesis(citation_data, position_data, results_data)

        return JsonResponse({
            'total': total,
            'filtered': len(filtered),
            'rate': round(rate, 2),
            'combinations': filtered[:1000],  # Limit to 1000 for response
            'has_more': len(filtered) > 1000,
            'results_synthesis': [{'horse': h, 'count': c} for h, c in results],
            'expert_synthesis': [{'horse': h, 'score': round(s, 1)} for h, s in expert]
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def api_backtest(request):
    """
    API: Teste une arrivée contre les combinaisons filtrées.

    POST body:
        {
            "arrivee": "1, 2, 3, 4, 5",
            "combinations": [[1, 2, 3, 4, 5, 6], [1, 2, 3, 4, 5, 7], ...],
            "groups": [...],
            "filters": {...}
        }
    """
    try:
        data = json.loads(request.body)
        arrivee_str = data.get('arrivee', '')
        combinations = data.get('combinations', [])
        groups = data.get('groups', [])
        filters = data.get('filters', {})

        # Parse arrivee
        arrivee = sorted(set(int(x.strip()) for x in arrivee_str.replace(',', ' ').split() if x.strip().isdigit()))

        if not arrivee:
            return JsonResponse({'error': 'Invalid arrivee'}, status=400)

        # Find matching combinations
        matching = find_matching_combinations(arrivee, combinations)

        # Analyze groups
        group_analysis = []
        for group in groups:
            intersection = [h for h in group['horses'] if h in arrivee]
            if intersection:
                group_analysis.append({
                    'name': group['name'],
                    'horses_in_arrivee': intersection,
                    'count': len(intersection)
                })

        # Analyze matching combinations
        matching_details = []
        for combi in matching:
            detail = {
                'combination': combi,
                'even_count': sum(1 for n in combi if n % 2 == 0),
                'odd_count': sum(1 for n in combi if n % 2 == 1),
            }

            # Weight analysis
            for wf in filters.get('weight', []):
                if 'map' in wf:
                    weight = calculate_combination_weight(combi, wf['map'])
                    detail['weight'] = weight

            # Alternance analysis
            for af in filters.get('alternance', []):
                if 'source' in af:
                    alt = calculate_alternances(combi, af['source'])
                    detail['alternance'] = alt

            matching_details.append(detail)

        return JsonResponse({
            'arrivee': arrivee,
            'found_count': len(matching),
            'total_tested': len(combinations),
            'group_analysis': group_analysis,
            'matching_combinations': matching_details
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def api_weight_bounds(request):
    """
    API: Calcule les bornes min/max de poids pour une source.

    POST body:
        {
            "source": "default",
            "n": 16,
            "k": 6,
            "manual_list": [1, 2, 3]
        }
    """
    try:
        data = json.loads(request.body)
        source = data.get('source', 'default')
        n = int(data.get('n', 16))
        k = int(data.get('k', 6))
        manual_list = data.get('manual_list', [])

        weight_map, sorted_weights = build_weight_map(source, n, None, manual_list)

        if len(sorted_weights) < k:
            return JsonResponse({
                'error': f'Pas assez de chevaux ({len(sorted_weights)}) pour une combinaison de taille {k}'
            }, status=400)

        min_weight, max_weight = calculate_weight_bounds(sorted_weights, k)

        return JsonResponse({
            'source': source,
            'min_weight': min_weight,
            'max_weight': max_weight,
            'available_horses': len(sorted_weights)
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def api_alternance_max(request):
    """
    API: Retourne le maximum théorique d'alternances.

    POST body:
        {
            "k": 6
        }
    """
    try:
        data = json.loads(request.body)
        k = int(data.get('k', 6))

        return JsonResponse({
            'k': k,
            'max_alternances': max_alternances(k)
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# =============================================================================
# SCENARIO MANAGEMENT API
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def api_scenarios_list(request):
    """
    API: Liste tous les scénarios sauvegardés.

    GET response:
        [
            {
                "id": 1,
                "name": "Mon favori Quinté+",
                "description": "Pour les courses à 16+ partants",
                "n_partants": 16,
                "k_taille": 6,
                "is_favorite": true,
                "usage_count": 15,
                "date_course": "2026-01-23",  // Optionnel
                "course_name": "Prix d'Amérique",  // Optionnel
                "nb_combinaisons_restantes": 1234,  // Optionnel
                "created_at": "2026-01-23T10:30:00Z"
            }
        ]
    """
    from .models import Scenario

    scenarios = Scenario.objects.all()
    scenarios_data = [{
        'id': s.id,
        'name': s.name,
        'description': s.description,
        'n_partants': s.n_partants,
        'k_taille': s.k_taille,
        'is_favorite': s.is_favorite,
        'usage_count': s.usage_count,
        'date_course': s.date_course.isoformat() if s.date_course else None,
        'course_name': s.nom_course,
        'nb_combinaisons_restantes': s.nb_combinaisons_restantes,
        'created_at': s.created_at.isoformat(),
        'updated_at': s.updated_at.isoformat(),
    } for s in scenarios]

    return JsonResponse({'scenarios': scenarios_data})


@csrf_exempt
@require_http_methods(["POST"])
def api_scenario_save(request):
    """
    API: Sauvegarde un nouveau scénario ou met à jour un existant.

    POST body:
        {
            "id": null,  // null pour nouveau, ID pour mise à jour
            "name": "Mon scénario",
            "description": "Description optionnelle",
            "n_partants": 16,
            "k_taille": 6,
            "groups": [...],
            "filters": {...},
            "course_date": "2026-01-23",  // Optionnel
            "course_name": "Prix d'Amérique",  // Optionnel
            "arrivee": [1, 2, 3, 4, 5],  // Optionnel
            "pronostics_text": "Favoris: 1, 2, 3...",  // Optionnel
            "nb_combinaisons_restantes": 1234,  // Optionnel
            "is_favorite": false
        }
    """
    from .models import Scenario
    from datetime import datetime

    try:
        data = json.loads(request.body)
        scenario_id = data.get('id')

        # Parse date if provided
        course_date = data.get('course_date')
        if course_date:
            try:
                course_date = datetime.strptime(course_date, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                course_date = None

        if scenario_id:
            # Mise à jour
            scenario = Scenario.objects.get(id=scenario_id)
            scenario.name = data.get('name', scenario.name)
            scenario.description = data.get('description', '')
            scenario.n_partants = data.get('n_partants', scenario.n_partants)
            scenario.k_taille = data.get('k_taille', scenario.k_taille)
            scenario.groups = data.get('groups', [])
            scenario.filters = data.get('filters', {})
            scenario.date_course = course_date
            scenario.nom_course = data.get('course_name', '')
            scenario.arrivee = data.get('arrivee')
            scenario.pronostics_text = data.get('pronostics_text', '')
            scenario.nb_combinaisons_restantes = data.get('nb_combinaisons_restantes')
            scenario.is_favorite = data.get('is_favorite', False)
            scenario.save()
        else:
            # Création
            scenario = Scenario.objects.create(
                name=data.get('name', 'Nouveau scénario'),
                description=data.get('description', ''),
                n_partants=data.get('n_partants', 16),
                k_taille=data.get('k_taille', 6),
                groups=data.get('groups', []),
                filters=data.get('filters', {}),
                date_course=course_date,
                nom_course=data.get('course_name', ''),
                arrivee=data.get('arrivee'),
                pronostics_text=data.get('pronostics_text', ''),
                nb_combinaisons_restantes=data.get('nb_combinaisons_restantes'),
                is_favorite=data.get('is_favorite', False)
            )

        return JsonResponse({
            'success': True,
            'scenario': {
                'id': scenario.id,
                'name': scenario.name,
                'description': scenario.description,
                'n_partants': scenario.n_partants,
                'k_taille': scenario.k_taille,
                'groups': scenario.groups,
                'filters': scenario.filters,
                'course_date': scenario.date_course.isoformat() if scenario.date_course else None,
                'course_name': scenario.nom_course,
                'arrivee': scenario.arrivee,
                'pronostics_text': scenario.pronostics_text,
                'nb_combinaisons_restantes': scenario.nb_combinaisons_restantes,
                'is_favorite': scenario.is_favorite,
            }
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def api_scenario_load(request):
    """
    API: Charge un scénario et incrémente son compteur d'utilisation.

    POST body:
        {
            "id": 1
        }
    """
    from .models import Scenario

    try:
        data = json.loads(request.body)
        scenario = Scenario.objects.get(id=data.get('id'))
        scenario.increment_usage()

        return JsonResponse({
            'success': True,
            'scenario': {
                'id': scenario.id,
                'name': scenario.name,
                'description': scenario.description,
                'n_partants': scenario.n_partants,
                'k_taille': scenario.k_taille,
                'groups': scenario.groups,
                'filters': scenario.filters,
                'course_date': scenario.date_course.isoformat() if scenario.date_course else None,
                'course_name': scenario.nom_course,
                'arrivee': scenario.arrivee,
                'pronostics_text': scenario.pronostics_text,
                'nb_combinaisons_restantes': scenario.nb_combinaisons_restantes,
                'is_favorite': scenario.is_favorite,
            }
        })
    except Scenario.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Scénario non trouvé'}, status=404)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["DELETE"])
def api_scenario_delete(request):
    """
    API: Supprime un scénario.

    DELETE body:
        {
            "id": 1
        }
    """
    from .models import Scenario

    try:
        data = json.loads(request.body)
        scenario = Scenario.objects.get(id=data.get('id'))
        scenario.delete()

        return JsonResponse({'success': True})
    except Scenario.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Scénario non trouvé'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
