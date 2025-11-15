from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import Discipline, Cycle, Niveau, Palier, Partie, Chapitre, Lecon, Contenu


def home(request):
    """
    Vue pour la page d'accueil
    """
    try:
        # Récupérer toutes les disciplines avec leurs niveaux
        disciplines = Discipline.objects.all().prefetch_related('niveaux')

        # Statistiques générales
        stats = {
            'disciplines_count': Discipline.objects.count(),
        }

        context = {
            'stats': stats,
            'disciplines': disciplines,
        }
    except Exception as e:
        print(f"Erreur dans la vue home: {e}")
        context = {
            'stats': {
                'disciplines_count': 0,
            },
            'disciplines': Discipline.objects.all(),
        }

    return render(request, 'educalims/home_simple.html', context)


def disciplines_list(request):
    """
    Vue pour lister toutes les disciplines disponibles
    """
    disciplines = Discipline.objects.all().prefetch_related('niveaux')

    context = {
        'disciplines': disciplines,
    }
    return render(request, 'educalims/disciplines_list_simple.html', context)


def discipline_detail(request, discipline_id):
    """
    Vue pour afficher le détail d'une discipline avec ses cycles et niveaux
    """
    discipline = get_object_or_404(Discipline, id=discipline_id)
    cycles = discipline.cycles.all().prefetch_related('niveaux')

    # Récupérer tous les niveaux avec relations hiérarchiques
    niveaux = discipline.niveaux.all().prefetch_related(
        'enfants',
        'parent',
        'type_enseignement'
    ).select_related('parent', 'type_enseignement')

    # Organiser les niveaux par hiérarchie
    niveaux_parents = niveaux.filter(parent__isnull=True).order_by('ordre')

    # Créer une liste de tuples (parent, enfants) pour faciliter l'affichage dans le template
    niveaux_hierarchie = []
    for parent in niveaux_parents:
        enfants = niveaux.filter(parent=parent).order_by('ordre')
        niveaux_hierarchie.append({
            'parent': parent,
            'enfants': enfants
        })

    context = {
        'discipline': discipline,
        'cycles': cycles,
        'niveaux': niveaux,
        'niveaux_parents': niveaux_parents,
        'niveaux_hierarchie': niveaux_hierarchie,
    }
    return render(request, 'educalims/discipline_detail_simple.html', context)


def niveau_detail(request, niveau_id):
    """
    Vue pour afficher les détails d'un niveau spécifique avec navigation hiérarchique
    """
    niveau = get_object_or_404(Niveau.objects.prefetch_related(
        'parent',
        'type_enseignement',
        'discipline',
        'cycle',
        'enfants'
    ).select_related(
        'parent', 'type_enseignement', 'discipline', 'cycle'
    ), id=niveau_id)

    # Récupérer aussi les leçons disponibles pour ce niveau
    lecons_disponibles = Lecon.objects.filter(
        Q(chapitre__palier__niveau=niveau) | Q(chapitre__partie__niveau=niveau)
    ).select_related('chapitre', 'chapitre__palier', 'chapitre__partie').order_by(
        'chapitre__palier__numero',
        'chapitre__partie__titre',
        'chapitre__numero',
        'numero'
    )

    # Récupérer les niveaux frères et enfants pour la navigation
    niveaux_freres = Niveau.objects.filter(
        discipline=niveau.discipline,
        cycle=niveau.cycle,
        parent=niveau.parent
    ).exclude(id=niveau.id).order_by('ordre')

    niveaux_enfants = niveau.enfants.all().order_by('ordre')

    context = {
        'niveau': niveau,
        'lecons_disponibles': lecons_disponibles,
        'niveaux_freres': niveaux_freres,
        'niveaux_enfants': niveaux_enfants,
    }
    return render(request, 'educalims/niveau_detail_simple.html', context)


def palier_detail(request, palier_id):
    """
    Vue pour afficher les détails d'un palier avec ses chapitres et leçons
    """
    palier = get_object_or_404(Palier.objects.prefetch_related(
        'chapitres__lecons'
    ), id=palier_id)

    # Récupérer tous les chapitres du palier avec leurs leçons
    chapitres = palier.chapitres.all().prefetch_related('lecons')

    context = {
        'palier': palier,
        'chapitres': chapitres,
    }
    return render(request, 'educalims/palier_detail.html', context)


def partie_detail(request, partie_id):
    """
    Vue pour afficher les détails d'une partie avec ses chapitres et leçons
    """
    partie = get_object_or_404(Partie.objects.prefetch_related(
        'chapitres__lecons'
    ), id=partie_id)

    # Récupérer tous les chapitres de la partie avec leurs leçons
    chapitres = partie.chapitres.all().prefetch_related('lecons')

    context = {
        'partie': partie,
        'chapitres': chapitres,
    }
    return render(request, 'educalims/partie_detail.html', context)


def chapitre_detail(request, chapitre_id):
    """
    Vue pour afficher les détails d'un chapitre avec ses leçons et contenus
    """
    chapitre = get_object_or_404(Chapitre.objects.prefetch_related(
        'lecons', 'contenus'
    ), id=chapitre_id)

    # Récupérer toutes les leçons du chapitre
    lecons = chapitre.lecons.all()

    # Récupérer les contenus du chapitre
    contenus = chapitre.contenus.all()

    context = {
        'chapitre': chapitre,
        'lecons': lecons,
        'contenus': contenus,
    }
    return render(request, 'educalims/chapitre_detail_simple.html', context)


def lecon_detail(request, lecon_id):
    """
    Vue pour afficher les détails d'une leçon
    """
    lecon = get_object_or_404(Lecon, id=lecon_id)

    # Récupérer le parent (palier ou partie) pour la navigation
    parent = lecon.chapitre.get_parent()
    niveau = lecon.chapitre.get_niveau()

    context = {
        'lecon': lecon,
        'parent': parent,
        'niveau': niveau,
    }
    return render(request, 'educalims/lecon_detail.html', context)


def search(request):
    """
    Vue pour la recherche globale
    """
    query = request.GET.get('q', '').strip()
    is_ajax = request.GET.get('ajax') == '1'

    results = {
        'disciplines': [],
    }

    if query:
        # Recherche dans les disciplines
        results['disciplines'] = Discipline.objects.filter(
            Q(nom__icontains=query) |
            Q(description__icontains=query)
        ).prefetch_related('niveaux__cycle').distinct()

    if is_ajax:
        # Formater les résultats pour AJAX
        ajax_results = []

        # Ajouter les disciplines avec leurs combinaisons
        for discipline in results['disciplines'][:5]:  # Limiter à 5 résultats par type
            cycles = set()
            for niveau in discipline.niveaux.all():
                cycles.add(niveau.cycle.nom)

            ajax_results.append({
                'type': 'discipline',
                'title': discipline.nom,
                'url': f"/discipline/{discipline.id}/",
                'combinations': list(cycles) if cycles else ['Tous cycles'],
                'description': discipline.description[:100] + '...' if discipline.description and len(discipline.description) > 100 else discipline.description
            })

        return JsonResponse({
            'results': ajax_results,
            'total_count': len(results['disciplines'])
        })
    else:
        # Recherche normale (non-AJAX)
        context = {
            'query': query,
            'results': results,
            'total_results': len(results['disciplines']),
        }
        return render(request, 'educalims/search.html', context)


def discipline_by_slug(request, slug):
    """
    Vue pour afficher une discipline par son slug (URL simplifiée)
    """
    # Mapping des slugs vers les noms de disciplines
    discipline_mapping = {
        'svt': 'Sciences de la Vie et de la Terre',
        'physique': 'Physique-Chimie',
        'maths': 'Mathématiques',
        'philosophie': 'Philosophie',
        'histoire': 'Histoire-Géographie',
    }

    discipline_name = discipline_mapping.get(slug.lower())
    if not discipline_name:
        return HttpResponse("Discipline non trouvée", status=404)

    discipline = get_object_or_404(Discipline, nom=discipline_name)
    return discipline_detail(request, discipline.id)


def discipline_cycle_detail(request, slug, cycle_type):
    """
    Vue pour afficher uniquement les niveaux d'un cycle spécifique (collège ou lycée) pour une discipline
    """
    # Mapping des slugs vers les noms de disciplines
    discipline_mapping = {
        'svt': 'Sciences de la Vie et de la Terre',
        'physique': 'Physique-Chimie',
        'maths': 'Mathématiques',
        'philosophie': 'Philosophie',
        'histoire': 'Histoire-Géographie',
    }

    # Mapping des types de cycle vers les noms de cycles
    cycle_mapping = {
        'college': 'Collège',
        'lycee': 'Lycée',
    }

    discipline_name = discipline_mapping.get(slug.lower())
    cycle_name = cycle_mapping.get(cycle_type.lower())

    if not discipline_name or not cycle_name:
        return HttpResponse("Discipline ou cycle non trouvé", status=404)

    discipline = get_object_or_404(Discipline, nom=discipline_name)

    # Filtrer les cycles pour n'afficher que celui demandé
    cycles = discipline.cycles.filter(nom=cycle_name).prefetch_related('niveaux')

    # Filtrer les niveaux pour n'afficher que ceux du cycle demandé
    niveaux = discipline.niveaux.filter(
        cycle__nom=cycle_name
    ).select_related('parent', 'type_enseignement')

    # Organiser les niveaux par hiérarchie
    niveaux_parents = niveaux.filter(parent__isnull=True).order_by('ordre')

    # Créer une liste de tuples (parent, enfants) pour faciliter l'affichage dans le template
    niveaux_hierarchie = []
    for parent in niveaux_parents:
        enfants = discipline.niveaux.filter(
            cycle__nom=cycle_name,
            parent=parent
        ).order_by('nom')
        niveaux_hierarchie.append({
            'parent': parent,
            'enfants': enfants
        })

    context = {
        'discipline': discipline,
        'cycles': cycles,
        'niveaux': niveaux,
        'niveaux_parents': niveaux_parents,
        'niveaux_hierarchie': niveaux_hierarchie,
        'cycle_type': cycle_type,
        'cycle_name': cycle_name,
    }
    return render(request, 'educalims/discipline_cycle_detail.html', context)


def about(request):
    """
    Vue pour la page À propos
    """
    return render(request, 'educalims/about.html')


@csrf_exempt
@require_http_methods(["GET"])
def get_cycles_by_discipline(request):
    """
    Vue AJAX pour récupérer les cycles disponibles (tous les cycles sont maintenant indépendants)
    """
    try:
        cycles = Cycle.objects.all().values('id', 'nom')
        return JsonResponse({'cycles': list(cycles)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_niveaux_by_cycle_and_discipline(request):
    """
    Vue AJAX pour récupérer les niveaux associés à un cycle et une discipline
    """
    cycle_id = request.GET.get('cycle_id')
    discipline_id = request.GET.get('discipline_id')

    if not cycle_id or not discipline_id:
        return JsonResponse({'error': 'cycle_id et discipline_id requis'}, status=400)

    try:
        niveaux = Niveau.objects.filter(
            cycle_id=cycle_id,
            discipline_id=discipline_id
        ).values('id', 'nom')
        return JsonResponse({'niveaux': list(niveaux)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_lecons_by_niveau(request):
    """
    Vue AJAX pour récupérer les leçons disponibles par niveau
    """
    niveau_id = request.GET.get('niveau_id')
    if not niveau_id:
        return JsonResponse({'error': 'niveau_id requis'}, status=400)

    try:
        # Récupérer le niveau
        niveau = Niveau.objects.get(id=niveau_id)

        # Récupérer toutes les leçons disponibles pour ce niveau (via paliers ou parties)
        lecons = Lecon.objects.filter(
            Q(chapitre__palier__niveau=niveau) | Q(chapitre__partie__niveau=niveau)
        ).select_related('chapitre', 'chapitre__palier', 'chapitre__partie').order_by(
            'chapitre__palier__numero',
            'chapitre__partie__titre',
            'chapitre__numero',
            'numero'
        )

        # Formatter les données pour le JSON
        lecons_data = []
        for lecon in lecons:
            parent_info = ""
            if lecon.chapitre.palier:
                parent_info = f"Palier: {lecon.chapitre.palier.titre}"
            elif lecon.chapitre.partie:
                parent_info = f"Partie: {lecon.chapitre.partie.titre}"

            lecons_data.append({
                'id': lecon.id,
                'titre': lecon.titre,
                'numero': lecon.numero,
                'parent': parent_info,
                'chapitre': lecon.chapitre.titre,
                'description': lecon.description
            })

        return JsonResponse({'lecons': lecons_data})
    except Niveau.DoesNotExist:
        return JsonResponse({'error': 'niveau introuvable'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def niveau_hierarchie(request, niveau_id):
    """
    Vue pour afficher la navigation hiérarchique complète d'un niveau
    """
    niveau = get_object_or_404(Niveau.objects.prefetch_related(
        'parties__chapitres__contenus',
        'paliers__chapitres__contenus',
        'paliers__chapitres__lecons'
    ).select_related(
        'discipline', 'cycle'
    ), id=niveau_id)

    context = {
        'niveau': niveau,
        'parties': niveau.parties.all() if niveau.cycle.nom == 'Lycée' else [],
        'paliers': niveau.paliers.all() if niveau.cycle.nom == 'Collège' else [],
    }
    return render(request, 'educalims/niveau_hierarchie_simple.html', context)


@csrf_exempt
@require_http_methods(["GET"])
def get_niveaux_by_discipline(request):
    """
    Vue AJAX pour récupérer les niveaux associés à une discipline
    """
    discipline_id = request.GET.get('discipline_id')
    if not discipline_id:
        return JsonResponse({'error': 'discipline_id requis'}, status=400)

    try:
        niveaux = Niveau.objects.filter(discipline_id=discipline_id).select_related('cycle').order_by('cycle', 'ordre')

        niveaux_data = []
        for niveau in niveaux:
            niveaux_data.append({
                'id': niveau.id,
                'nom': niveau.nom,
                'cycle': niveau.cycle.nom,
                'ordre': niveau.ordre
            })

        return JsonResponse({'niveaux': niveaux_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_unites_apprentissage_by_niveau(request):
    """
    Vue AJAX pour récupérer les unités d'apprentissage selon le niveau
    - Collège: retourne les leçons
    - Lycée: retourne les chapitres
    """
    niveau_id = request.GET.get('niveau_id')
    if not niveau_id:
        return JsonResponse({'error': 'niveau_id requis'}, status=400)

    try:
        niveau = Niveau.objects.select_related('cycle').get(id=niveau_id)

        if niveau.cycle.nom.lower() == 'collège':
            # Pour le collège: retourner les leçons
            lecons = Lecon.objects.filter(
                Q(chapitre__palier__niveau=niveau) | Q(chapitre__partie__niveau=niveau)
            ).select_related('chapitre').order_by('chapitre__numero', 'numero')

            unites_data = []
            for lecon in lecons:
                parent_info = ""
                if lecon.chapitre.palier:
                    parent_info = f"Palier: {lecon.chapitre.palier.titre}"
                elif lecon.chapitre.partie:
                    parent_info = f"Partie: {lecon.chapitre.partie.titre}"

                unites_data.append({
                    'id': lecon.id,
                    'titre': lecon.titre,
                    'type': 'lecon',
                    'numero': lecon.numero,
                    'parent_info': parent_info,
                    'chapitre_titre': lecon.chapitre.titre
                })

            return JsonResponse({'unites': unites_data, 'cycle': 'collège'})

        elif niveau.cycle.nom.lower() == 'lycée':
            # Pour le lycée: retourner les chapitres
            chapitres = Chapitre.objects.filter(
                Q(palier__niveau=niveau) | Q(partie__niveau=niveau)
            ).order_by('numero', 'titre')

            unites_data = []
            for chapitre in chapitres:
                parent_info = ""
                if chapitre.palier:
                    parent_info = f"Palier: {chapitre.palier.titre}"
                elif chapitre.partie:
                    parent_info = f"Partie: {chapitre.partie.titre}"

                unites_data.append({
                    'id': chapitre.id,
                    'titre': chapitre.titre,
                    'type': 'chapitre',
                    'numero': chapitre.numero,
                    'parent_info': parent_info
                })

            return JsonResponse({'unites': unites_data, 'cycle': 'lycée'})

        else:
            return JsonResponse({'error': 'Cycle non reconnu'}, status=400)

    except Niveau.DoesNotExist:
        return JsonResponse({'error': 'niveau introuvable'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def contenu_detail(request, contenu_id):
    """
    Vue pour afficher le détail d'un contenu
    """
    contenu = get_object_or_404(Contenu.objects.select_related(
        'discipline', 'niveau', 'niveau__cycle'
    ).prefetch_related(
        'lecons', 'chapitres'
    ), id=contenu_id)

    context = {
        'contenu': contenu,
    }
    return render(request, 'educalims/contenu_detail_simple.html', context)