# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404
from .models import Cycle, Discipline, Niveau, Unite, Fichier


def home(request):
    """
    Page d'accueil - Liste tous les cycles
    """
    cycles = Cycle.objects.all()
    context = {
        'cycles': cycles,
        'title': 'EDUCALIMS - Accueil',
    }
    return render(request, 'home.html', context)


def cycle_detail(request, pk):
    """
    Détail d'un cycle avec toutes ses disciplines
    """
    cycle = get_object_or_404(Cycle, pk=pk)
    disciplines = cycle.disciplines.all()
    
    context = {
        'cycle': cycle,
        'disciplines': disciplines,
        'title': f'{cycle.nom} - EDUCALIMS',
    }
    return render(request, 'educalims_app/cycle_detail.html', context)


def discipline_detail(request, pk):
    """
    Détail d'une discipline avec tous ses niveaux
    """
    discipline = get_object_or_404(Discipline, pk=pk)
    niveaux = discipline.niveaux.filter(parent__isnull=True)  # Uniquement les niveaux parents
    
    context = {
        'discipline': discipline,
        'niveaux': niveaux,
        'title': f'{discipline.nom} - EDUCALIMS',
    }
    return render(request, 'educalims_app/discipline_detail.html', context)


def niveau_detail(request, pk):
    """
    Détail d'un niveau avec toutes ses unités
    """
    niveau = get_object_or_404(Niveau, pk=pk)
    unites = niveau.unites.filter(parent__isnull=True)  # Uniquement les unités parentes
    enfants = niveau.enfants.all()  # Niveaux enfants (hiérarchie profonde)
    
    context = {
        'niveau': niveau,
        'unites': unites,
        'enfants': enfants,
        'title': f'{niveau.nom} - EDUCALIMS',
    }
    return render(request, 'educalims_app/niveau_detail.html', context)


def unite_detail(request, pk):
    """
    Détail d'une unité avec tous ses fichiers
    """
    unite = get_object_or_404(Unite, pk=pk)
    fichiers = unite.fichiers.all()
    enfants = unite.enfants.all()  # Unités enfants (hiérarchie profonde)
    
    context = {
        'unite': unite,
        'fichiers': fichiers,
        'enfants': enfants,
        'title': f'{unite.titre} - EDUCALIMS',
    }
    return render(request, 'educalims_app/unite_detail.html', context)


def fichier_detail(request, pk):
    """
    Détail d'un fichier
    """
    fichier = get_object_or_404(Fichier, pk=pk)
    
    context = {
        'fichier': fichier,
        'title': f'{fichier.titre} - EDUCALIMS',
    }
    return render(request, 'educalims_app/fichier_detail.html', context)
