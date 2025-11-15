#!/usr/bin/env python
"""
Script de test simple pour vérifier la nouvelle structure de la base de données Django
"""

import os
import sys
import django
from django.db import models

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'site_educatif.settings')
django.setup()

from educalims.models import Discipline, Cycle, Niveau, Palier, Partie, Chapitre, Lecon, Contenu


def test_existing_structure():
    """
    Test la structure existante de la base de données
    """
    print("=== Test de la structure existante de la base de données ===\n")
    
    # 1. Vérification des Disciplines
    print("1. Disciplines existantes:")
    disciplines = Discipline.objects.all()
    for discipline in disciplines:
        print(f"   - {discipline.nom}: {discipline.description}")
    
    # 2. Vérification des Cycles et leurs relations avec Disciplines
    print("\n2. Cycles existants et leurs disciplines:")
    cycles = Cycle.objects.all()
    for cycle in cycles:
        print(f"   - {cycle.nom} -> {cycle.discipline.nom}")
    
    # 3. Vérification des Niveaux
    print("\n3. Niveaux existants:")
    niveaux = Niveau.objects.all()
    for niveau in niveaux:
        print(f"   - {niveau.nom} -> {niveau.discipline.nom} ({niveau.cycle.nom})")
    
    # 4. Vérification des Paliers
    print("\n4. Paliers existants:")
    paliers = Palier.objects.all()
    for palier in paliers:
        print(f"   - Palier {palier.numero}: {palier.titre} ({palier.niveau.nom})")
    
    # 5. Vérification des Parties
    print("\n5. Parties existantes:")
    parties = Partie.objects.all()
    for partie in parties:
        print(f"   - {partie.titre} ({partie.niveau.nom})")
    
    # 6. Vérification des Chapitres
    print("\n6. Chapitres existants:")
    chapitres = Chapitre.objects.all()
    for chapitre in chapitres:
        parent = chapitre.get_parent()
        print(f"   - Chapitre {chapitre.numero}: {chapitre.titre} -> {parent}")
    
    # 7. Vérification des Leçons
    print("\n7. Leçons existantes:")
    lecons = Lecon.objects.all()
    for lecon in lecons:
        print(f"   - Leçon {lecon.numero}: {lecon.titre} ({lecon.chapitre.titre})")
    
    # 8. Vérification des Contenus
    print("\n8. Contenus existants:")
    contenus = Contenu.objects.all()
    for contenu in contenus:
        parent = contenu.get_parent()
        print(f"   - {contenu.titre} -> {parent}")
        print(f"     Type: {contenu.type_contenu}, Fichier: {contenu.has_file}")
    
    # 9. Test des requêtes complexes
    print("\n9. Test des requêtes complexes:")
    
    # Récupérer tous les contenus d'un niveau (via leçons)
    if niveaux:
        niveau_test = niveaux.first()
        contenus_niveau_lecons = Contenu.objects.filter(
            lecon__chapitre__palier__niveau=niveau_test
        )
        print(f"   Contenus du niveau {niveau_test.nom} (via leçons-paliers): {contenus_niveau_lecons.count()}")
        
        contenus_niveau_lecons_partie = Contenu.objects.filter(
            lecon__chapitre__partie__niveau=niveau_test
        )
        print(f"   Contenus du niveau {niveau_test.nom} (via leçons-parties): {contenus_niveau_lecons_partie.count()}")
        
        # Récupérer tous les contenus d'un niveau (via chapitres)
        contenus_niveau_chapitres = Contenu.objects.filter(
            chapitre__palier__niveau=niveau_test
        )
        print(f"   Contenus du niveau {niveau_test.nom} (via chapitres-paliers): {contenus_niveau_chapitres.count()}")
        
        contenus_niveau_chapitres_partie = Contenu.objects.filter(
            chapitre__partie__niveau=niveau_test
        )
        print(f"   Contenus du niveau {niveau_test.nom} (via chapitres-parties): {contenus_niveau_chapitres_partie.count()}")
        
        # Récupérer toutes les leçons d'un niveau
        lecons_niveau = Lecon.objects.filter(
            models.Q(chapitre__palier__niveau=niveau_test) | 
            models.Q(chapitre__partie__niveau=niveau_test)
        )
        print(f"   Leçons du niveau {niveau_test.nom}: {lecons_niveau.count()}")
    
    # 10. Statistiques finales
    print("\n10. Statistiques finales:")
    print(f"   Disciplines: {Discipline.objects.count()}")
    print(f"   Cycles: {Cycle.objects.count()}")
    print(f"   Niveaux: {Niveau.objects.count()}")
    print(f"   Paliers: {Palier.objects.count()}")
    print(f"   Parties: {Partie.objects.count()}")
    print(f"   Chapitres: {Chapitre.objects.count()}")
    print(f"   Leçons: {Lecon.objects.count()}")
    print(f"   Contenus: {Contenu.objects.count()}")
    
    print("\n=== Test terminé avec succès ! ===")
    return True


if __name__ == "__main__":
    try:
        test_existing_structure()
    except Exception as e:
        print(f"\nErreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)