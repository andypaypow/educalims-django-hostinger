#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'site_educatif.settings')
django.setup()

from educalims.models import Discipline, Niveau, Cycle

print("=== Correction de la hiérarchie des niveaux Seconde ===")

# Récupérer la discipline SVT
svt_discipline = Discipline.objects.get(nom="Sciences de la Vie et de la Terre")

# Récupérer le cycle Lycée pour SVT
lycee_cycle = Cycle.objects.get(discipline=svt_discipline, nom="Lycée")

# Récupérer les niveaux concernés
seconde_parent = Niveau.objects.get(nom="Seconde (Parent)", discipline=svt_discipline, cycle=lycee_cycle)
seconde_sle = Niveau.objects.get(nom="Seconde S/LE", discipline=svt_discipline, cycle=lycee_cycle)
seconde_stmg = Niveau.objects.get(nom="Seconde STMG", discipline=svt_discipline, cycle=lycee_cycle)

# Corriger les relations parent/enfant
print("Corrections des relations:")

# Corriger Seconde S/LE
if seconde_sle.parent != seconde_parent:
    print(f"Avant: Seconde S/LE -> parent: {seconde_sle.parent}")
    seconde_sle.parent = seconde_parent
    seconde_sle.save()
    print(f"Après: Seconde S/LE -> parent: {seconde_sle.parent}")
else:
    print("Seconde S/LE déjà correctement rattachée")

# Corriger Seconde STMG
if seconde_stmg.parent != seconde_parent:
    print(f"Avant: Seconde STMG -> parent: {seconde_stmg.parent}")
    seconde_stmg.parent = seconde_parent
    seconde_stmg.save()
    print(f"Après: Seconde STMG -> parent: {seconde_stmg.parent}")
else:
    print("Seconde STMG déjà correctement rattachée")

# Supprimer ou corriger le niveau "Seconde" problématique
try:
    seconde_problematique = Niveau.objects.get(nom="Seconde", discipline=svt_discipline, cycle=lycee_cycle)
    print(f"Niveau 'Seconde' problématique trouvé: {seconde_problematique}")
    print("Suppression de ce niveau pour éviter la confusion...")
    seconde_problematique.delete()
    print("Niveau 'Seconde' problématique supprimé")
except Niveau.DoesNotExist:
    print("Aucun niveau 'Seconde' problématique trouvé")

# Renommer "Seconde (Parent)" en "Seconde" si c'est possible
try:
    # Vérifier si "Seconde" existe maintenant
    Niveau.objects.get(nom="Seconde", discipline=svt_discipline, cycle=lycee_cycle)
    print("Le nom 'Seconde' est déjà utilisé")
except Niveau.DoesNotExist:
    print("Renommage de 'Seconde (Parent)' en 'Seconde'")
    seconde_parent.nom = "Seconde"
    seconde_parent.save()
    print(f"Renommé en: {seconde_parent.nom}")

print("\n=== Vérification finale ===")

# Vérifier la structure finale
niveaux_lycee = Niveau.objects.filter(
    discipline=svt_discipline,
    cycle=lycee_cycle
).select_related('parent', 'type_enseignement').order_by('ordre')

niveaux_parents = niveaux_lycee.filter(parent__isnull=True).order_by('ordre')

print("Structure hiérarchique finale:")
for parent in niveaux_parents:
    enfants = niveaux_lycee.filter(parent=parent).order_by('ordre')
    type_info = parent.type_enseignement.nom if parent.type_enseignement else "Non défini"

    print(f"\n[PARENT] {parent.nom} ({type_info})")

    if enfants.exists():
        print(f"   Enfants ({enfants.count()}):")
        for enfant in enfants:
            enfant_type = enfant.type_enseignement.nom if enfant.type_enseignement else "Non défini"
            print(f"      - {enfant.nom} ({enfant_type})")
    else:
        print("   (Pas d'enfants)")

print("\n=== Opération terminée ===")