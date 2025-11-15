#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'site_educatif.settings')
django.setup()

from educalims.models import Discipline, Niveau

print("=== Correction de l'ordre des niveaux ===")

try:
    # Récupérer la discipline SVT
    svt_discipline = Discipline.objects.get(nom="Sciences de la Vie et de la Terre")
    print(f"Discipline : {svt_discipline.nom}")

    # Ordre souhaité pour les niveaux principaux (parents)
    ordre_corrections = {
        "6ème": 1,
        "5ème": 2,
        "4ème": 3,
        "3ème": 4,
        "Seconde": 5,
        "Première": 6,
        "Terminale": 7
    }

    print("\nMise à jour des ordres :")

    for nom_niveau, nouvel_ordre in ordre_corrections.items():
        try:
            niveau = Niveau.objects.get(discipline=svt_discipline, nom=nom_niveau)
            ancien_ordre = niveau.ordre
            niveau.ordre = nouvel_ordre
            niveau.save()
            print(f"OK {nom_niveau}: {ancien_ordre} -> {nouvel_ordre}")
        except Niveau.DoesNotExist:
            print(f"ERREUR Niveau '{nom_niveau}' non trouvé")

    print(f"\n{'='*50}")
    print("Vérification après correction :")

    niveaux_corriges = Niveau.objects.filter(discipline=svt_discipline, parent__isnull=True).order_by('ordre')
    for i, niveau in enumerate(niveaux_corriges, 1):
        print(f"{i}. {niveau.nom} (ordre: {niveau.ordre}) - {niveau.cycle.nom}")

    print(f"\nOK Correction terminée ! Les niveaux sont maintenant ordonnés de la 6ème à la Terminale.")

except Discipline.DoesNotExist:
    print("Discipline SVT non trouvée")
except Exception as e:
    print(f"Erreur : {e}")

print("\n=== Correction terminée ===")