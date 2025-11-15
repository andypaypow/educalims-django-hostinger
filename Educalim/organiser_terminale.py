#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'site_educatif.settings')
django.setup()

from educalims.models import Niveau, Discipline

print("=== Organisation des classes de Terminale ===")

try:
    # Récupérer la discipline SVT (ID: 1)
    svt_discipline = Discipline.objects.get(id=1)
    print(f"Discipline : {svt_discipline.nom}")

    # Ordre souhaité pour les classes de Terminale
    ordre_terminale = {
        "Terminale A": 1,
        "Terminale B": 2,
        "Terminale C": 3,
        "Terminale D": 4
    }

    print("\nMise à jour des ordres pour les classes de Terminale :")

    # Récupérer le niveau parent Terminale
    try:
        parent_terminale = Niveau.objects.get(discipline=svt_discipline, nom="Terminale", parent__isnull=True)
        print(f"Niveau parent trouvé : {parent_terminale.nom}")

        # Mettre à jour l'ordre des enfants Terminale
        for nom_enfant, nouvel_ordre in ordre_terminale.items():
            try:
                enfant = Niveau.objects.get(discipline=svt_discipline, nom=nom_enfant, parent=parent_terminale)
                ancien_ordre = enfant.ordre
                enfant.ordre = nouvel_ordre
                enfant.save()
                print(f"OK {nom_enfant}: {ancien_ordre} -> {nouvel_ordre}")
            except Niveau.DoesNotExist:
                print(f"ERREUR Classe '{nom_enfant}' non trouvée")

        print(f"\n{'='*50}")
        print("Vérification après mise à jour :")

        # Vérifier l'ordre des classes de Terminale
        enfants_terminale = Niveau.objects.filter(
            discipline=svt_discipline,
            parent=parent_terminale
        ).order_by('ordre')

        for i, enfant in enumerate(enfants_terminale, 1):
            print(f"{i}. {enfant.nom} (ordre: {enfant.ordre})")

        print(f"\nOK Classes de Terminale organisées selon l'ordre demandé !")

    except Niveau.DoesNotExist:
        print("ERREUR Niveau parent 'Terminale' non trouvé")

except Discipline.DoesNotExist:
    print("Discipline SVT (ID: 1) non trouvée")
except Exception as e:
    print(f"Erreur : {e}")

print("\n=== Organisation terminée ===")