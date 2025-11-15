#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'site_educatif.settings')
django.setup()

from educalims.models import Discipline, Niveau, Cycle, TypeEnseignement

print("=== Test de la hiérarchie pour SVT Lycée ===")

# Récupérer la discipline SVT (Sciences de la Vie et de la Terre)
svt_discipline = Discipline.objects.filter(nom="Sciences de la Vie et de la Terre").first()
print(f"Discipline: {svt_discipline}")

if svt_discipline:
    # Récupérer le cycle Lycée pour SVT
    lycee_cycle = Cycle.objects.filter(discipline=svt_discipline, nom="Lycée").first()
    print(f"Cycle Lycée: {lycee_cycle}")

    if lycee_cycle:
        # Filtrer les niveaux pour le cycle Lycée SVT
        niveaux_lycee = svt_discipline.niveaux.filter(
            cycle__nom="Lycée"
        ).select_related('parent', 'type_enseignement').order_by('ordre')

        print(f"\nNiveaux trouvés pour SVT Lycée: {niveaux_lycee.count()}")

        # Organiser les niveaux par hiérarchie comme dans la vue
        niveaux_parents = niveaux_lycee.filter(parent__isnull=True).order_by('ordre')
        niveaux_hierarchie = []

        for parent in niveaux_parents:
            enfants = niveaux_lycee.filter(parent=parent).order_by('ordre')
            niveaux_hierarchie.append({
                'parent': parent,
                'enfants': enfants
            })

        print(f"\nStructure hiérarchique:")
        for hierarchie in niveaux_hierarchie:
            parent = hierarchie['parent']
            enfants = hierarchie['enfants']
            type_info = parent.type_enseignement.nom if parent.type_enseignement else "Non défini"
            print(f"\n  [PARENT] {parent.nom} ({type_info})")

            # Compter les paliers/parties
            paliers_count = parent.paliers.count()
            parties_count = parent.parties.count()
            if paliers_count > 0:
                print(f"      - {paliers_count} palier(s)")
            if parties_count > 0:
                print(f"      - {parties_count} partie(s)")

            for enfant in enfants:
                enfant_type = enfant.type_enseignement.nom if enfant.type_enseignement else "Non défini"
                print(f"      [ENFANT] {enfant.nom} ({enfant_type})")

                # Compter les paliers/parties pour l'enfant
                enfant_paliers = enfant.paliers.count()
                enfant_parties = enfant.parties.count()
                if enfant_paliers > 0:
                    print(f"         - {enfant_paliers} palier(s)")
                if enfant_parties > 0:
                    print(f"         - {enfant_parties} partie(s)")

print("\n=== Test terminé ===")