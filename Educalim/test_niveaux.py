#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'site_educatif.settings')
django.setup()

from educalims.models import Niveau, TypeEnseignement

print("Test: Vérification des niveaux existants")
print("Niveaux parents:")
parents = Niveau.objects.filter(parent__isnull=True, nom__in=['Première', 'Terminale'])
for parent in parents:
    print(f"  - {parent.nom} ({parent.type_enseignement.nom if parent.type_enseignement else 'Non défini'})")

print("\nTypes d'enseignement:")
for type_ens in TypeEnseignement.objects.all():
    print(f"  - {type_ens.nom}: {type_ens.description}")

print("\nTest: Création d'un niveau enfant")
premiere = Niveau.objects.filter(nom='Première').first()
if premiere:
    print(f"Parent trouvé: {premiere.nom}")
    print("Tentative de création de Première A...")

    # Vérifier si Première A existe déjà
    existing_premiere_a = Niveau.objects.filter(nom='Première A').first()
    if existing_premiere_a:
        print("Première A existe déjà!")
    else:
        premiere_a = Niveau.objects.create(
            nom='Première A',
            discipline=premiere.discipline,
            cycle=premiere.cycle,
            ordre=1,
            parent=premiere,
            type_enseignement=premiere.type_enseignement,
            description="Classe de Première A"
        )
        print(f"Créé: {premiere_a.nom} (parent: {premiere_a.parent.nom})")

    # Vérification des enfants
    print(f"\nEnfants de {premiere.nom}:")
    enfants = Niveau.objects.filter(parent=premiere)
    for enfant in enfants:
        print(f"  - {enfant.nom}")
else:
    print("Parent Première non trouvé")

print("\nTest terminé!")