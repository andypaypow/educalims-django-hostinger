#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'site_educatif.settings')
django.setup()

from educalims.models import Niveau, TypeEnseignement

print("=== Correction du type d'enseignement pour Seconde STMG ===")

# Récupérer la Seconde STMG pour la discipline SVT
seconde_stmg_svt = Niveau.objects.filter(
    nom__icontains="STMG",
    discipline__nom="Sciences de la Vie et de la Terre"
).first()

# Récupérer le type d'enseignement technique
tech_type = TypeEnseignement.objects.get(nom="Enseignement technique")

if seconde_stmg_svt:
    print(f"Avant: {seconde_stmg_svt.nom} - {seconde_stmg_svt.type_enseignement}")
    seconde_stmg_svt.type_enseignement = tech_type
    seconde_stmg_svt.save()
    print(f"Après: {seconde_stmg_svt.nom} - {seconde_stmg_svt.type_enseignement}")
else:
    print("Seconde STMG (SVT) non trouvée")

print("=== Vérification finale ===")
# Vérifier tous les niveaux STMG
seconde_stmg_all = Niveau.objects.filter(nom__icontains="STMG")
for niveau in seconde_stmg_all:
    print(f"{niveau.nom} ({niveau.discipline.nom}) - {niveau.type_enseignement.nom if niveau.type_enseignement else 'Non défini'}")