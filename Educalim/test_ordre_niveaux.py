#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'site_educatif.settings')
django.setup()

from educalims.models import Niveau, Discipline, Cycle

print("=== Vérification de l'ordre des niveaux ===")

try:
    # Récupérer la discipline SVT
    svt_discipline = Discipline.objects.get(nom="Sciences de la Vie et de la Terre")
    print(f"Discipline : {svt_discipline.nom}")

    # Récupérer tous les niveaux SVT avec leur ordre
    niveaux_svt = Niveau.objects.filter(discipline=svt_discipline).select_related('cycle', 'parent').order_by('ordre')

    print(f"\nNiveaux trouvés : {niveaux_svt.count()}")
    print("\nOrdre actuel des niveaux :")

    for i, niveau in enumerate(niveaux_svt, 1):
        print(f"{i:2d}. {niveau.nom:15s} (ordre: {niveau.ordre:2d}) - {niveau.cycle.nom} - Parent: {niveau.parent.nom if niveau.parent else 'Aucun'}")

    # Vérifier l'ordre souhaité
    print("\nOrdre souhaité :")
    ordre_souhaite = [
        "6ème", "5ème", "4ème", "3ème",  # Collège
        "Seconde", "Première", "Terminale"  # Lycée
    ]

    for i, nom_souhaite in enumerate(ordre_souhaite, 1):
        try:
            niveau = Niveau.objects.get(discipline=svt_discipline, nom=nom_souhaite)
            print(f"{i:2d}. {niveau.nom:15s} (ordre actuel: {niveau.ordre:2d}) - Devrait être ordre: {i}")
        except Niveau.DoesNotExist:
            print(f"{i:2d}. {nom_souhaite:15s} (NIVEAU MANQUANT)")

    # Proposition de correction
    print(f"\n{'='*50}")
    print("CORRECTION SUGGÉRÉE :")
    print("Pour corriger l'ordre, exécutez ce code dans la console Django :")
    print("\n# Mettre à jour les ordres")

    corrections = {}
    for i, nom_souhaite in enumerate(ordre_souhaite, 1):
        try:
            niveau = Niveau.objects.get(discipline=svt_discipline, nom=nom_souhaite)
            if niveau.ordre != i:
                corrections[niveau.nom] = i
                print(f"Niveau.objects.filter(discipline=svt_discipline, nom='{niveau.nom}').update(ordre={i})")
        except Niveau.DoesNotExist:
            pass

    if not corrections:
        print("✓ L'ordre des niveaux est déjà correct!")

except Discipline.DoesNotExist:
    print("Discipline SVT non trouvée")
except Exception as e:
    print(f"Erreur : {e}")

print("\n=== Test terminé ===")