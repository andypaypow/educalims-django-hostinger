from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.http import HttpResponse
from .models import Discipline, Cycle, Niveau, UniteEnseignement, Contenu


def home(request):
    """
    Vue pour la page d'accueil
    """
    try:
        # Statistiques générales
        stats = {
            'disciplines_count': Discipline.objects.count(),
            'unites_count': UniteEnseignement.objects.count(),
            'contenus_count': Contenu.objects.count(),
        }

        # Dernières unités d'enseignement ajoutées
        recent_unites = UniteEnseignement.objects.select_related(
            'niveau__cycle__discipline'
        ).order_by('-id')[:6]

        context = {
            'stats': stats,
            'recent_unites': recent_unites,
        }
    except Exception as e:
        print(f"Erreur dans la vue home: {e}")
        context = {
            'stats': {
                'disciplines_count': 0,
                'unites_count': 0,
                'contenus_count': 0,
            },
            'recent_unites': [],
        }

    return render(request, 'educalims/home_simple.html', context)


def disciplines_list(request):
    """
    Vue pour lister toutes les disciplines disponibles
    """
    disciplines = Discipline.objects.all().prefetch_related('cycles__niveaux__unites')

    context = {
        'disciplines': disciplines,
    }
    return render(request, 'educalims/disciplines_list_simple.html', context)


def discipline_detail(request, discipline_id):
    """
    Vue pour afficher le détail d'une discipline avec ses cycles et niveaux
    """
    discipline = get_object_or_404(Discipline, id=discipline_id)
    cycles = discipline.cycles.all().prefetch_related('niveaux__unites')

    context = {
        'discipline': discipline,
        'cycles': cycles,
    }
    return render(request, 'educalims/discipline_detail_simple.html', context)


def niveau_detail(request, niveau_id):
    """
    Vue pour afficher les unités d'enseignement d'un niveau spécifique
    """
    niveau = get_object_or_404(Niveau, id=niveau_id)
    unites = niveau.unites.all().prefetch_related('contenus')

    context = {
        'niveau': niveau,
        'unites': unites,
    }
    return render(request, 'educalims/niveau_detail_simple.html', context)


def unite_detail(request, unite_id):
    """
    Vue pour afficher le détail d'une unité d'enseignement avec ses contenus
    """
    unite = get_object_or_404(UniteEnseignement, id=unite_id)
    contenus = unite.contenus.all().order_by('type_contenu', 'nom')

    context = {
        'unite': unite,
        'contenus': contenus,
    }
    return render(request, 'educalims/unite_detail_simple.html', context)


def search(request):
    """
    Vue pour la recherche globale
    """
    query = request.GET.get('q', '').strip()
    results = {
        'unites': [],
        'contenus': [],
        'disciplines': [],
    }

    if query:
        # Recherche dans les unités d'enseignement
        results['unites'] = UniteEnseignement.objects.filter(
            Q(titre__icontains=query) |
            Q(niveau__nom__icontains=query) |
            Q(niveau__cycle__nom__icontains=query) |
            Q(niveau__cycle__discipline__nom__icontains=query)
        ).select_related('niveau__cycle__discipline').distinct()

        # Recherche dans les contenus
        results['contenus'] = Contenu.objects.filter(
            Q(nom__icontains=query) |
            Q(type_contenu__icontains=query)
        ).select_related('unites').distinct()

        # Recherche dans les disciplines
        results['disciplines'] = Discipline.objects.filter(
            Q(nom__icontains=query)
        ).distinct()

    context = {
        'query': query,
        'results': results,
        'total_results': len(results['unites']) + len(results['contenus']) + len(results['disciplines']),
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


def about(request):
    """
    Vue pour la page À propos
    """
    return render(request, 'educalims/about.html')
