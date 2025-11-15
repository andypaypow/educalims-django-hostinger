#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'site_educatif.settings')
django.setup()

from educalims.models import Discipline, Niveau, TypeEnseignement, Cycle

print("=== Création du niveau parent Seconde ===")

# Récupérer les types d'enseignement
enseignement_general = TypeEnseignement.objects.get(nom="Enseignement général")
enseignement_technique = TypeEnseignement.objects.get(nom="Enseignement technique")

# Récupérer la discipline SVT
svt_discipline = Discipline.objects.get(nom="Sciences de la Vie et de la Terre")

# Récupérer le cycle Lycée pour SVT
lycee_cycle = Cycle.objects.get(discipline=svt_discipline, nom="Lycée")

# Vérifier s'il existe déjà un niveau "Seconde" pour SVT
existing_seconde = Niveau.objects.filter(
    nom="Seconde",
    discipline=svt_discipline,
    cycle=lycee_cycle
).first()

if existing_seconde:
    if existing_seconde.parent is None:
        print(f"Le niveau parent Seconde existe déjà: {existing_seconde}")
        seconde_parent = existing_seconde
    else:
        print(f"Il existe un niveau Seconde mais il a déjà un parent: {existing_seconde.parent}")
        # On va créer un nouveau parent avec un nom différent
        seconde_parent = Niveau.objects.create(
            nom="Seconde (Parent)",
            discipline=svt_discipline,
            cycle=lycee_cycle,
            ordre=1,  # Ordre 1 pour Seconde (avant Première)
            description="Niveau parent pour toutes les classes de Seconde",
            type_enseignement=enseignement_general,
            parent=None
        )
        print(f"Créé le niveau parent Seconde (Parent): {seconde_parent}")
else:
    # Créer le niveau parent Seconde
    seconde_parent = Niveau.objects.create(
        nom="Seconde",
        discipline=svt_discipline,
        cycle=lycee_cycle,
        ordre=1,  # Ordre 1 pour Seconde (avant Première)
        description="Niveau parent pour toutes les classes de Seconde",
        type_enseignement=enseignement_general,
        parent=None
    )
    print(f"Créé le niveau parent Seconde: {seconde_parent}")

print("\n=== Rattachement des niveaux Seconde existants ===")

# Récupérer les niveaux Seconde existants
seconde_sle = Niveau.objects.filter(
    nom="Seconde S/LE",
    discipline=svt_discipline,
    cycle=lycee_cycle,
    parent__isnull=True
).first()

seconde_stmg = Niveau.objects.filter(
    nom="Seconde STMG",
    discipline=svt_discipline,
    cycle=lycee_cycle,
    parent__isnull=True
).first()

# Mettre à jour Seconde S/LE
if seconde_sle:
    seconde_sle.parent = seconde_parent
    seconde_sle.save()
    print(f"[OK] Seconde S/LE rattachee au parent Seconde")
else:
    print("[ERREUR] Seconde S/LE non trouvee")

# Mettre à jour Seconde STMG
if seconde_stmg:
    seconde_stmg.parent = seconde_parent
    seconde_stmg.save()
    print(f"[OK] Seconde STMG rattachee au parent Seconde")
else:
    print("[ERREUR] Seconde STMG non trouvee")

print("\n=== Vérification finale ===")

# Vérifier la hiérarchie
print("Structure hiérarchique pour SVT Lycée:")
niveaux_lycee = svt_discipline.niveaux.filter(
    cycle__nom="Lycée"
).select_related('parent', 'type_enseignement').order_by('ordre')

niveaux_parents = niveaux_lycee.filter(parent__isnull=True).order_by('ordre')

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