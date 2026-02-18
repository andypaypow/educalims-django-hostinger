"""
Views pour les analyses de backtest
"""
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json


def test_arrivee(request):
    """Teste une arrivée contre les combinaisons filtrées"""
    import json
    
    data = json.loads(request.body)
    arrivee = data.get('arrivee', [])
    combinations = data.get('combinations', [])
    
    arrivee_set = set(arrivee)
    
    # Trouver les combinaisons qui contiennent l'arrivée
    matching = []
    for combi in combinations:
        combi_set = set(combi)
        if arrivee_set.issubset(combi_set):
            matching.append(combi)
    
    return JsonResponse({
        'arrivee': arrivee,
        'found': len(matching) > 0,
        'matching_count': len(matching),
        'matching_combinations': matching
    })


@csrf_exempt
@require_http_methods(["POST"])
def save_backtest_analysis(request):
    """Sauvegarde une analyse de backtest dans la base de données"""
    try:
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Utilisateur non connecté'}, status=401)
        
        data = json.loads(request.body)
        
        # Créer l'analyse
        from gosen.models import BacktestAnalysis
        
        analysis = BacktestAnalysis.objects.create(
            user=request.user,
            num_partants=data.get('num_partants'),
            taille_combinaison=data.get('taille_combinaison'),
            pronostics=data.get('pronostics', []),
            criteres_filtres=data.get('criteres_filtres', {}),
            arrivee=data.get('arrivee', []),
            combinaisons_filtrees=data.get('combinaisons_filtrees', []),
            combinaisons_trouvees=data.get('combinaisons_trouvees', []),
            nombre_trouvees=data.get('nombre_trouvees', 0),
            rapport=data.get('rapport', ''),
            nom=data.get('nom', '')
        )
        
        return JsonResponse({
            'success': True,
            'analysis_id': analysis.id,
            'message': 'Analyse sauvegardée avec succès'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def get_backtest_analyses(request):
    """Récupère la liste des analyses de backtest de l'utilisateur"""
    try:
        from gosen.models import BacktestAnalysis
        
        analyses = BacktestAnalysis.objects.filter(
            user=request.user
        ).order_by('-date_creation')[:50]  # Limiter à 50 analyses
        
        analyses_data = []
        for analysis in analyses:
            arrivee_str = ', '.join(map(str, analysis.arrivee)) if analysis.arrivee else 'N/A'
            analyses_data.append({
                'id': analysis.id,
                'nom': analysis.nom or f'Backtest du {analysis.date_creation.strftime("%d/%m/%Y %H:%M")}',
                'arrivee': arrivee_str,
                'nombre_trouvees': analysis.nombre_trouvees,
                'date_creation': analysis.date_creation.isoformat(),
                'num_partants': analysis.num_partants,
                'taille_combinaison': analysis.taille_combinaison
            })
        
        return JsonResponse({
            'success': True,
            'analyses': analyses_data
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def get_backtest_analysis(request, analysis_id):
    """Récupère une analyse spécifique avec toutes les données"""
    try:
        from gosen.models import BacktestAnalysis
        
        analysis = BacktestAnalysis.objects.get(id=analysis_id, user=request.user)
        
        return JsonResponse({
            'success': True,
            'analysis': {
                'id': analysis.id,
                'nom': analysis.nom,
                'num_partants': analysis.num_partants,
                'taille_combinaison': analysis.taille_combinaison,
                'pronostics': analysis.pronostics,
                'criteres_filtres': analysis.criteres_filtres,
                'arrivee': analysis.arrivee,
                'combinaisons_filtrees': analysis.combinaisons_filtrees,
                'combinaisons_trouvees': analysis.combinaisons_trouvees,
                'nombre_trouvees': analysis.nombre_trouvees,
                'rapport': analysis.rapport,
                'date_creation': analysis.date_creation.isoformat()
            }
        })
    except BacktestAnalysis.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Analyse non trouvée'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
@login_required
def delete_backtest_analysis(request, analysis_id):
    """Supprime une analyse de backtest"""
    try:
        from gosen.models import BacktestAnalysis
        
        analysis = BacktestAnalysis.objects.get(id=analysis_id, user=request.user)
        analysis.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Analyse supprimée avec succès'
        })
    except BacktestAnalysis.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Analyse non trouvée'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
