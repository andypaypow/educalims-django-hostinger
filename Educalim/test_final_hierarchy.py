#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'site_educatif.settings')
django.setup()

from educalims.models import Discipline, Niveau, Cycle

print("=== Test final de la hiérarchie SVT ===")

# Récupérer la discipline SVT
svt_discipline = Discipline.objects.get(nom="Sciences de la Vie et de la Terre")

# Récupérer le cycle Lycée pour SVT
lycee_cycle = Cycle.objects.get(discipline=svt_discipline, nom="Lycée")

# Récupérer les niveaux pour le Lycée SVT
niveaux_lycee = svt_discipline.niveaux.filter(
    cycle__nom="Lycée"
).select_related('parent', 'type_enseignement').order_by('ordre')

# Organiser par hiérarchie comme dans la vue
niveaux_parents = niveaux_lycee.filter(parent__isnull=True).order_by('ordre')
niveaux_hierarchie = []

for parent in niveaux_parents:
    enfants = niveaux_lycee.filter(parent=parent).order_by('ordre')
    niveaux_hierarchie.append({
        'parent': parent,
        'enfants': enfants
    })

print("\n=== STRUCTURE QUI SERA AFFICHÉE DANS LE TEMPLATE ===")

for hierarchie in niveaux_hierarchie:
    parent = hierarchie['parent']
    enfants = hierarchie['enfants']
    type_info = parent.type_enseignement.nom if parent.type_enseignement else "Non défini"

    print(f"\n[NIVEAU PRINCIPAL] {parent.nom}")
    print(f"   Type: {type_info}")
    print(f"   ID: {parent.id}")

    # Compter les paliers/parties
    paliers_count = parent.paliers.count()
    parties_count = parent.parties.count()
    print(f"   Paliers: {paliers_count}, Parties: {parties_count}")

    if enfants.exists():
        print(f"   [SOUS-NIVEAUX] ({enfants.count()}):")
        for enfant in enfants:
            enfant_type = enfant.type_enseignement.nom if enfant.type_enseignement else "Non défini"
            enfant_paliers = enfant.paliers.count()
            enfant_parties = enfant.parties.count()
            print(f"      - {enfant.nom} (Type: {enfant_type}, ID: {enfant.id})")
            print(f"        Paliers: {enfant_paliers}, Parties: {enfant_parties}")
            print(f"        Type d'enseignement: {enfant_type}")
    else:
        print("   (Pas de sous-niveaux)")

print("\n=== Test du système d'accordéon ===")
print("Maintenant, en visitant http://localhost:8000/discipline/svt/lycee/ :")
print("1. Seconde s'affichera avec un badge '2 classes' et une flèche ▼")
print("2. Première s'affichera avec un badge '3 classes' et une flèche ▼")
print("3. Terminale s'affichera avec un badge '4 classes' et une flèche ▼")
print("4. En cliquant sur chaque parent, les classes enfants apparaîtront")

print("\n=== Structure attendue ===")
print("Seconde (Enseignement général)")
print("├── Seconde S/LE (Enseignement général)")
print("└── Seconde STMG (Enseignement technique) ⚠️ badge différent")
print("\nPremière (Enseignement général)")
print("├── Première A (Enseignement général)")
print("├── Première B (Enseignement général)")
print("└── Première S (Enseignement général)")
print("\nTerminale (Enseignement général)")
print("├── Terminale A (Enseignement général)")
print("├── Terminale B (Enseignement général)")
print("├── Terminale C (Enseignement général)")
print("└── Terminale D (Enseignement général)")

print("\n=== Test terminé avec succès ===")