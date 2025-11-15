#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'site_educatif.settings')
django.setup()

from educalims.models import Niveau, Contenu

print("=== Test de la vue niveau_detail (contenus détaillés) ===")

try:
    # Tester avec un niveau qui a des contenus
    niveau = Niveau.objects.prefetch_related(
        'parent', 'type_enseignement', 'discipline', 'cycle'
    ).first()

    if niveau:
        print(f"Niveau testé: {niveau.nom}")
        print(f"Discipline: {niveau.discipline.nom}")
        print(f"Cycle: {niveau.cycle.nom}")
        print(f"Type: {niveau.type_enseignement.nom if niveau.type_enseignement else 'Non défini'}")

        if niveau.parent:
            print(f"Parent: {niveau.parent.nom}")
        else:
            print("Parent: Aucun (niveau racine)")

        # Compter les contenus via paliers
        contenus_paliers = Contenu.objects.filter(
            lecon__chapitre__palier__niveau=niveau
        ).count()

        # Compter les contenus via parties
        contenus_parties = Contenu.objects.filter(
            lecon__chapitre__partie__niveau=niveau
        ).count()

        total_contenus = max(contenus_paliers, contenus_parties)  # Approximation pour le test

        print(f"\nContenus trouvés:")
        print(f"  - Via paliers: {contenus_paliers}")
        print(f"  - Via parties: {contenus_parties}")
        print(f"  - Total estimé: {total_contenus}")

        # Vérifier les niveaux enfants
        enfants = niveau.enfants.all()
        if enfants.exists():
            print(f"\nNiveaux enfants ({enfants.count()}):")
            for enfant in enfants:
                enfant_type = enfant.type_enseignement.nom if enfant.type_enseignement else "Non défini"
                print(f"  - {enfant.nom} ({enfant_type})")

        print(f"\nURL à tester: http://127.0.0.1:8000/niveau/{niveau.id}/")
        print("Cette page montrera les contenus détaillés avec navigation hiérarchique.")

        if niveau.cycle.nom == 'Lycée':
            print("\nNiveaux Lycée avec enfants à tester:")
            niveaux_lycee_enfants = Niveau.objects.filter(
                cycle__nom="Lycée",
                parent__isnull=False
            )
            for n in niveaux_lycee_enfants[:3]:  # Limiter à 3 pour le test
                print(f"  - http://127.0.0.1:8000/niveau/{n.id}/ (niveau enfant)")

    else:
        print("Aucun niveau trouvé dans la base de données")

except Exception as e:
    print(f"Erreur: {e}")

print("\n=== Test terminé ===")