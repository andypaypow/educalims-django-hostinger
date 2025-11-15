#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'site_educatif.settings')
django.setup()

from educalims.models import Niveau, Contenu, Discipline

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

        # Compter les contenus (éviter union + distinct qui cause l'erreur)
        contenus_paliers = Contenu.objects.filter(
            lecon__chapitre__palier__niveau=niveau
        )
        contenus_parties = Contenu.objects.filter(
            lecon__chapitre__partie__niveau=niveau
        )

        # Combiner manuellement pour éviter l'erreur
        contenus_ids = set()
        contenus_list = []

        for contenu in contenus_paliers:
            if contenu.id not in contenus_ids:
                contenus_ids.add(contenu.id)
                contenus_list.append(contenu)

        for contenu in contenus_parties:
            if contenu.id not in contenus_ids:
                contenus_ids.add(contenu.id)
                contenus_list.append(contenu)

        # Convertir en une liste simple pour le test
        contenus = contenus_list

        print(f"\nContenus trouvés: {len(contenus)}")

        if contenus:
            print("Types de contenus:")
            types_counts = {}
            for contenu in contenus:
                type_key = contenu.get_type_contenu_display()
                if type_key not in types_counts:
                    types_counts[type_key] = 0
                types_counts[type_key] += 1

            for type_name, count in types_counts.items():
                print(f"  - {type_name}: {count}")

        # Vérifier les niveaux enfants
        enfants = niveau.enfants.all()
        if enfants.exists():
            print(f"\nNiveaux enfants ({enfants.count()}):")
            for enfant in enfants:
                enfant_type = enfant.type_enseignement.nom if enfant.type_enseignement else "Non défini"
                print(f"  - {enfant.nom} ({enfant_type})")

        print(f"\nURL à tester: http://127.0.0.1:8000/niveau/{niveau.id}/")
        print("Cette page montrera les contenus détaillés avec navigation hiérarchique.")

    else:
        print("Aucun niveau trouvé dans la base de données")

except Exception as e:
    print(f"Erreur: {e}")

print("\n=== Test terminé ===")