#!/usr/bin/env python
"""
Script de test pour vérifier la nouvelle structure de la base de données Django
"""

import os
import sys
import django
from django.db import models

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'site_educatif.settings')
django.setup()

from educalims.models import Discipline, Cycle, Niveau, Palier, Partie, Chapitre, Lecon, Contenu


def test_new_structure():
    """
    Test la nouvelle structure de la base de données
    """
    print("=== Test de la nouvelle structure de la base de données ===\n")
    
    # 1. Test de création de Discipline
    print("1. Création d'une Discipline...")
    discipline, created = Discipline.objects.get_or_create(
        nom="Mathématiques",
        defaults={'description': 'Apprentissage des mathématiques'}
    )
    print(f"   Discipline créée: {created} - {discipline}")
    
    # 2. Test de création de Cycle
    print("\n2. Création d'un Cycle...")
    # D'abord vérifier si un cycle existe déjà pour cette discipline
    existing_cycle = Cycle.objects.filter(discipline=discipline).first()
    if existing_cycle:
        cycle = existing_cycle
        created = False
        print(f"   Cycle existant utilisé: {cycle}")
    else:
        cycle = Cycle.objects.create(
            nom="Lycée",
            discipline=discipline,
            description='Cycle d\'enseignement supérieur'
        )
        created = True
        print(f"   Cycle créé: {created} - {cycle}")
    
    # 3. Test de création de Niveau (lié à Discipline et Cycle)
    print("\n3. Création d'un Niveau...")
    niveau, created = Niveau.objects.get_or_create(
        nom="6ème",
        discipline=discipline,
        cycle=cycle,
        defaults={'description': 'Classe de 6ème'}
    )
    print(f"   Niveau créé: {created} - {niveau}")
    
    # 4. Test de création d'un Palier
    print("\n4. Création d'un Palier...")
    palier, created = Palier.objects.get_or_create(
        titre="Semestre 1",
        niveau=niveau,
        numero=1,
        defaults={'description': 'Premier semestre de 6ème'}
    )
    print(f"   Palier créé: {created} - {palier}")
    
    # 5. Test de création d'une Partie
    print("\n5. Création d'une Partie...")
    partie, created = Partie.objects.get_or_create(
        titre="Algèbre",
        niveau=niveau,
        defaults={'description': 'Introduction à l\'algèbre'}
    )
    print(f"   Partie créée: {created} - {partie}")
    
    # 6. Test de création d'un Chapitre (lié à un Palier)
    print("\n6. Création d'un Chapitre (lié au Palier)...")
    chapitre_palier, created = Chapitre.objects.get_or_create(
        titre="Nombres et calculs",
        palier=palier,
        numero=1,
        defaults={'description': 'Apprentissage des nombres et des calculs'}
    )
    print(f"   Chapitre (Palier) créé: {created} - {chapitre_palier}")
    print(f"   Parent du chapitre: {chapitre_palier.get_parent()}")
    print(f"   Niveau du chapitre: {chapitre_palier.get_niveau()}")
    
    # 7. Test de création d'un Chapitre (lié à une Partie)
    print("\n7. Création d'un Chapitre (lié à la Partie)...")
    chapitre_partie, created = Chapitre.objects.get_or_create(
        titre="Équations simples",
        partie=partie,
        numero=1,
        defaults={'description': 'Introduction aux équations'}
    )
    print(f"   Chapitre (Partie) créé: {created} - {chapitre_partie}")
    print(f"   Parent du chapitre: {chapitre_partie.get_parent()}")
    print(f"   Niveau du chapitre: {chapitre_partie.get_niveau()}")
    
    # 8. Test de création d'une Leçon
    print("\n8. Création d'une Leçon...")
    lecon, created = Lecon.objects.get_or_create(
        titre="Addition et soustraction",
        chapitre=chapitre_palier,
        numero=1,
        defaults={
            'description': 'Apprendre à additionner et soustraire',
            'objectifs': 'Maîtriser les opérations de base'
        }
    )
    print(f"   Leçon créée: {created} - {lecon}")
    print(f"   Niveau de la leçon: {lecon.get_niveau()}")
    
    # 9. Test de création d'un Contenu (lié à une Leçon)
    print("\n9. Création d'un Contenu (lié à une Leçon)...")
    contenu_lecon, created = Contenu.objects.get_or_create(
        titre="Exercices d'addition",
        lecon=lecon,
        defaults={
            'type_contenu': 'pdf',
            'description': 'Série d\'exercices sur l\'addition',
            'fichier': 'exercices/addition_6eme.pdf'
        }
    )
    print(f"   Contenu (Leçon) créé: {created} - {contenu_lecon}")
    print(f"   Contenu a un fichier: {contenu_lecon.has_file}")
    print(f"   Extension du fichier: {contenu_lecon.file_extension}")
    print(f"   Niveau du contenu: {contenu_lecon.get_niveau()}")
    print(f"   Parent du contenu: {contenu_lecon.get_parent()}")
    
    # 9b. Test de création d'un Contenu (lié à un Chapitre)
    print("\n9b. Création d'un Contenu (lié à un Chapitre)...")
    contenu_chapitre, created = Contenu.objects.get_or_create(
        titre="Résumé du chapitre",
        chapitre=chapitre_partie,
        defaults={
            'type_contenu': 'pdf',
            'description': 'Résumé des notions du chapitre',
            'fichier': 'resume/chapitre_equations.pdf'
        }
    )
    print(f"   Contenu (Chapitre) créé: {created} - {contenu_chapitre}")
    print(f"   Contenu a un fichier: {contenu_chapitre.has_file}")
    print(f"   Extension du fichier: {contenu_chapitre.file_extension}")
    print(f"   Niveau du contenu: {contenu_chapitre.get_niveau()}")
    print(f"   Parent du contenu: {contenu_chapitre.get_parent()}")
    
    # 10. Test des relations
    print("\n10. Vérification des relations...")
    print(f"   Disciplines: {Discipline.objects.count()}")
    print(f"   Cycles: {Cycle.objects.count()}")
    print(f"   Niveaux: {Niveau.objects.count()}")
    print(f"   Paliers: {Palier.objects.count()}")
    print(f"   Parties: {Partie.objects.count()}")
    print(f"   Chapitres: {Chapitre.objects.count()}")
    print(f"   Leçons: {Lecon.objects.count()}")
    print(f"   Contenus: {Contenu.objects.count()}")
    
    # 11. Test des requêtes complexes
    print("\n11. Test des requêtes complexes...")
    
    # Récupérer tous les contenus d'un niveau (via leçons)
    contenus_niveau_lecons = Contenu.objects.filter(
        lecon__chapitre__palier__niveau=niveau
    )
    print(f"   Contenus du niveau {niveau.nom} (via leçons-paliers): {contenus_niveau_lecons.count()}")
    
    contenus_niveau_lecons_partie = Contenu.objects.filter(
        lecon__chapitre__partie__niveau=niveau
    )
    print(f"   Contenus du niveau {niveau.nom} (via leçons-parties): {contenus_niveau_lecons_partie.count()}")
    
    # Récupérer tous les contenus d'un niveau (via chapitres)
    contenus_niveau_chapitres = Contenu.objects.filter(
        chapitre__palier__niveau=niveau
    )
    print(f"   Contenus du niveau {niveau.nom} (via chapitres-paliers): {contenus_niveau_chapitres.count()}")
    
    contenus_niveau_chapitres_partie = Contenu.objects.filter(
        chapitre__partie__niveau=niveau
    )
    print(f"   Contenus du niveau {niveau.nom} (via chapitres-parties): {contenus_niveau_chapitres_partie.count()}")
    
    # Récupérer toutes les leçons d'un niveau
    lecons_niveau = Lecon.objects.filter(
        models.Q(chapitre__palier__niveau=niveau) |
        models.Q(chapitre__partie__niveau=niveau)
    )
    print(f"   Leçons du niveau {niveau.nom}: {lecons_niveau.count()}")
    
    # Vérifier les cycles avec leurs disciplines
    cycles = Cycle.objects.all()
    print(f"   Cycles et leurs disciplines:")
    for cycle in cycles:
        print(f"     - {cycle.nom} -> {cycle.discipline.nom}")
    
    print("\n=== Test terminé avec succès ! ===")
    return True


if __name__ == "__main__":
    try:
        test_new_structure()
    except Exception as e:
        print(f"\nErreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)