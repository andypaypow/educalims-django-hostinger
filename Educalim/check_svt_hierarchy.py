#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'site_educatif.settings')
django.setup()

from educalims.models import Discipline, Niveau, TypeEnseignement

print("=== Vérification des niveaux SVT et hiérarchie ===")

# Récupérer la discipline SVT
svt = Discipline.objects.filter(nom__icontains='svt').first()
print(f"Discipline SVT: {svt.nom if svt else 'Non trouvée'}")

if svt:
    niveaux_svt = Niveau.objects.filter(discipline=svt).order_by('ordre')
    print(f"\nNiveaux SVT ({niveaux_svt.count()}):")

    for n in niveaux_svt:
        parent_info = n.parent.nom if n.parent else "Aucun"
        type_info = n.type_enseignement.nom if n.type_enseignement else "Non défini"
        print(f"  - {n.nom} (parent: {parent_info}, type: {type_info})")

# Vérifier tous les niveaux pour SVT
print("\n=== Toutes les disciplines et leurs niveaux ===")
disciplines = Discipline.objects.all()
for disc in disciplines:
    niveaux = Niveau.objects.filter(discipline=disc).order_by('ordre')
    print(f"\n{disc.nom} ({niveaux.count()} niveaux):")
    for n in niveaux:
        parent_info = n.parent.nom if n.parent else "Aucun"
        type_info = n.type_enseignement.nom if n.type_enseignement else "Non défini"
        print(f"  - {n.nom} (parent: {parent_info}, type: {type_info})")

# Vérifier les niveaux parents
print("\n=== Niveaux parents ===")
parents = Niveau.objects.filter(parent__isnull=True).order_by('nom')
for parent in parents:
    enfants = Niveau.objects.filter(parent=parent)
    type_info = parent.type_enseignement.nom if parent.type_enseignement else "Non défini"
    print(f"\n{parent.nom} ({type_info}) - {enfants.count()} enfants:")
    for enfant in enfants:
        print(f"  - {enfant.nom}")