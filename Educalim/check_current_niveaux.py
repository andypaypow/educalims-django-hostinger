#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'site_educatif.settings')
django.setup()

from educalims.models import Discipline, Niveau, Cycle

print("=== État actuel des niveaux SVT ===")

# Récupérer la discipline SVT
svt_discipline = Discipline.objects.get(nom="Sciences de la Vie et de la Terre")

# Récupérer le cycle Lycée pour SVT
lycee_cycle = Cycle.objects.get(discipline=svt_discipline, nom="Lycée")

# Récupérer tous les niveaux SVT Lycée
niveaux_lycee = Niveau.objects.filter(
    discipline=svt_discipline,
    cycle=lycee_cycle
).select_related('parent', 'type_enseignement').order_by('ordre')

print(f"\nNiveaux SVT Lycée trouvés: {niveaux_lycee.count()}")

for niveau in niveaux_lycee:
    parent_info = f"parent: {niveau.parent.nom}" if niveau.parent else "parent: Aucun"
    type_info = niveau.type_enseignement.nom if niveau.type_enseignement else "Non défini"
    print(f"  - {niveau.nom} ({type_info}) - {parent_info}")

print("\n=== Structure des niveaux qui contiennent 'Seconde' ===")

seconde_levels = niveaux_lycee.filter(nom__icontains="seconde")
for niveau in seconde_levels:
    parent_info = f"parent: {niveau.parent.nom}" if niveau.parent else "parent: Aucun"
    type_info = niveau.type_enseignement.nom if niveau.type_enseignement else "Non défini"
    print(f"  - {niveau.nom} ({type_info}) - {parent_info} - ID: {niveau.id}")

print("\n=== Recherche du niveau 'Seconde' exact ===")

exact_seconde = niveaux_lycee.filter(nom="Seconde")
for niveau in exact_seconde:
    parent_info = f"parent: {niveau.parent.nom}" if niveau.parent else "parent: Aucun"
    type_info = niveau.type_enseignement.nom if niveau.type_enseignement else "Non défini"
    print(f"  - {niveau.nom} ({type_info}) - {parent_info} - ID: {niveau.id}")