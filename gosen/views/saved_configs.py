"""
Views pour la gestion des configurations sauvegardées
Système indépendant du backtest
"""
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
from datetime import datetime


@csrf_exempt
@require_http_methods(["POST"])
def save_saved_config(request):
    """Sauvegarde la configuration actuelle"""
    try:
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Utilisateur non connecté'}, status=401)

        data = json.loads(request.body)

        from gosen.models import SavedResultConfig

        config = SavedResultConfig.objects.create(
            user=request.user,
            nom=data.get('nom', 'Sans nom'),
            num_partants=int(data.get('num_partants', 16)),
            taille_combinaison=int(data.get('taille_combinaison', 6)),
            pronostics_text=data.get('pronostics_text', ''),
            criteres_filtres=data.get('criteres_filtres', {}),
            reunion=data.get('reunion', ''),
            date_course=datetime.strptime(data.get('date_course'), '%Y-%m-%d').date() if data.get('date_course') else None,
            arrivee=data.get('arrivee', None)
        )

        return JsonResponse({
            'success': True,
            'id': config.id,
            'message': 'Configuration sauvegardée avec succès'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def list_saved_configs(request):
    """Liste toutes les configurations sauvegardées de l'utilisateur"""
    try:
        from gosen.models import SavedResultConfig

        configs = SavedResultConfig.objects.filter(
            user=request.user
        ).order_by('-created_at')[:50]

        configs_data = []
        for config in configs:
            configs_data.append({
                'id': config.id,
                'nom': config.nom,
                'created_at': config.created_at.isoformat(),
                'num_partants': config.num_partants,
                'taille_combinaison': config.taille_combinaison,
                'reunion': config.reunion or '',
                'date_course': config.date_course.isoformat() if config.date_course else '',
                'has_arrivee': config.arrivee is not None
            })

        return JsonResponse({'success': True, 'configs': configs_data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def load_saved_config(request, config_id):
    """Charge une configuration spécifique"""
    try:
        from gosen.models import SavedResultConfig

        config = SavedResultConfig.objects.get(id=config_id, user=request.user)

        return JsonResponse({
            'success': True,
            'config': {
                'id': config.id,
                'nom': config.nom,
                'num_partants': config.num_partants,
                'taille_combinaison': config.taille_combinaison,
                'pronostics_text': config.pronostics_text,
                'criteres_filtres': config.criteres_filtres,
                'reunion': config.reunion or '',
                'date_course': config.date_course.isoformat() if config.date_course else '',
                'arrivee': config.arrivee or []
            }
        })
    except SavedResultConfig.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Configuration non trouvée'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["PATCH"])
@login_required
def update_saved_config(request, config_id):
    """Met à jour les métadonnées d'une configuration (réunion, date, arrivée)"""
    try:
        from gosen.models import SavedResultConfig

        config = SavedResultConfig.objects.get(id=config_id, user=request.user)
        data = json.loads(request.body)

        # Seuls ces champs peuvent être modifiés
        if 'nom' in data:
            config.nom = data['nom']
        if 'reunion' in data:
            config.reunion = data['reunion']
        if 'date_course' in data:
            if data['date_course']:
                config.date_course = datetime.strptime(data['date_course'], '%Y-%m-%d').date()
            else:
                config.date_course = None
        if 'arrivee' in data:
            config.arrivee = data['arrivee'] if data['arrivee'] else None

        config.save()

        return JsonResponse({
            'success': True,
            'message': 'Configuration mise à jour avec succès'
        })
    except SavedResultConfig.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Configuration non trouvée'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
@login_required
def delete_saved_config(request, config_id):
    """Supprime une configuration sauvegardée"""
    try:
        from gosen.models import SavedResultConfig

        config = SavedResultConfig.objects.get(id=config_id, user=request.user)
        config.delete()

        return JsonResponse({
            'success': True,
            'message': 'Configuration supprimée avec succès'
        })
    except SavedResultConfig.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Configuration non trouvée'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
