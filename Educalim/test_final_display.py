#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'site_educatif.settings')
django.setup()

from educalims.models import Discipline, Niveau, Cycle, TypeEnseignement

print("=== Vérification finale de la hiérarchie SVT ===")

# Récupérer la discipline SVT
svt_discipline = Discipline.objects.filter(nom="Sciences de la Vie et de la Terre").first()
print(f"Discipline: {svt_discipline}")

if svt_discipline:
    # Vérifier les niveaux pour le Lycée
    niveaux_lycee = svt_discipline.niveaux.filter(
        cycle__nom="Lycée"
    ).select_related('parent', 'type_enseignement').order_by('ordre')

    print(f"\nNiveaux SVT Lycée: {niveaux_lycee.count()} niveaux")

    # Organiser par hiérarchie comme dans la vue
    niveaux_parents = niveaux_lycee.filter(parent__isnull=True).order_by('ordre')

    print("\n=== STRUCTURE QUI SERA AFFICHÉE DANS LE TEMPLATE ===")

    for parent in niveaux_parents:
        enfants = niveaux_lycee.filter(parent=parent).order_by('ordre')
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
        else:
            print("   (Pas de sous-niveaux)")

print("\n=== Test des URLs ===")
print("URLs à tester dans le navigateur:")
print("• Page d'accueil: http://localhost:8000/")
print("• SVT Collège: http://localhost:8000/discipline/svt/college/")
print("• SVT Lycée: http://localhost:8000/discipline/svt/lycee/")
print("\nLes niveaux devraient maintenant s'afficher avec leur structure hiérarchique!")
print("Les parents Première et Terminale montreront leurs classes enfants (A, B, S, etc.)")