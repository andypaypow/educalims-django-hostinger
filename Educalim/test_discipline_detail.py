#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'site_educatif.settings')
django.setup()

from educalims.models import Discipline, Niveau, Cycle

print("=== Test de la vue discipline_detail (tous les niveaux) ===")

# Tester avec SVT (ID probablement 1)
try:
    svt_discipline = Discipline.objects.get(nom="Sciences de la Vie et de la Terre")
    print(f"Discipline trouvée: {svt_discipline.nom} (ID: {svt_discipline.id})")

    # Récupérer tous les niveaux SVT
    niveaux_svt = svt_discipline.niveaux.all().select_related('parent', 'type_enseignement', 'cycle').order_by('cycle__nom', 'ordre')
    print(f"\nTotal des niveaux SVT: {niveaux_svt.count()}")

    # Organiser par hiérarchie
    niveaux_parents = niveaux_svt.filter(parent__isnull=True).order_by('cycle__nom', 'ordre')

    print(f"\nNiveaux parents ({niveaux_parents.count()}):")
    for parent in niveaux_parents:
        enfants = niveaux_svt.filter(parent=parent).order_by('ordre')
        type_info = parent.type_enseignement.nom if parent.type_enseignement else "Non défini"
        print(f"  - {parent.nom} ({parent.cycle.nom}) - {type_info}")
        if enfants.exists():
            print(f"    Enfants ({enfants.count()}):")
            for enfant in enfants:
                enfant_type = enfant.type_enseignement.nom if enfant.type_enseignement else "Non défini"
                print(f"      • {enfant.nom} ({enfant.cycle.nom}) - {enfant_type}")

    print("\n=== Structure attendue dans le template ===")
    print("1. Section Collège:")
    college_parents = niveaux_parents.filter(cycle__nom="Collège")
    for parent in college_parents:
        enfants = niveaux_svt.filter(parent=parent)
        print(f"   - {parent.nom} (badge: {enfants.count()} classes)")
        for enfant in enfants:
            print(f"     → {enfant.nom}")

    print("\n2. Section Lycée:")
    lycee_parents = niveaux_parents.filter(cycle__nom="Lycée")
    for parent in lycee_parents:
        enfants = niveaux_svt.filter(parent=parent)
        print(f"   - {parent.nom} (badge: {enfants.count()} classes)")
        for enfant in enfants:
            print(f"     → {enfant.nom}")

    print(f"\n=== Test terminé ===")
    print(f"URL à tester: http://127.0.0.1:8000/discipline/{svt_discipline.id}/")

except Discipline.DoesNotExist:
    print("Discipline SVT non trouvée")
except Exception as e:
    print(f"Erreur: {e}")