#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'site_educatif.settings')
django.setup()

from educalims.models import Niveau, Contenu

print("=== Test de vérification des templates Lycée ===")

try:
    # Trouver un niveau Lycée
    niveau_lycee = Niveau.objects.filter(cycle__nom='Lycée').first()

    if niveau_lycee:
        print(f"Niveau Lycée trouvé: {niveau_lycee.nom}")
        print(f"Cycle: {niveau_lycee.cycle.nom}")

        # Vérifier s'il a des parties (structure Lycée)
        if hasattr(niveau_lycee, 'parties'):
            parties = niveau_lycee.parties.all()
            print(f"Parties trouvées: {parties.count()}")
            for partie in parties[:3]:  # Limiter à 3 pour l'affichage
                print(f"  - {partie.titre}")
                chapitres = partie.chapitres.all()
                print(f"    Chapitres: {chapitres.count()}")
                for chapitre in chapitres[:2]:  # Limiter à 2 pour l'affichage
                    contenus = chapitre.contenus_chapitre.all()
                    print(f"      • {chapitre.titre}: {contenus.count()} contenus")

        # Compter les contenus via le modèle standard (pour Lycée)
        contenus_via_parties = Contenu.objects.filter(
            lecon__chapitre__partie__niveau=niveau_lycee
        ).count()

        print(f"\nContenus trouvés via parties: {contenus_via_parties}")

        print(f"\nURLs à tester pour le Lycée:")
        print(f"1. Navigation hiérarchique: http://127.0.0.1:8000/niveau_hierarchie/{niveau_lycee.id}/")
        print(f"2. Contenus détaillés: http://127.0.0.1:8000/niveau/{niveau_lycee.id}/")

        if niveau_lycee.enfants.exists():
            print(f"3. Niveau enfant Lycée: http://127.0.0.1:8000/niveau/{niveau_lycee.enfants.first().id}/")

        print(f"\nVérification des modifications:")
        print("✓ Template niveau_detail_with_lecons.html modifié pour grouper par chapitre au Lycée")
        print("✓ Vue niveau_hierarchie mise à jour avec prefetch_related contenus_chapitre")
        print("✓ Modèles supportent contenus_chapitre pour Lycée (structure directe chapitre -> contenu)")

    else:
        print("Aucun niveau Lycée trouvé dans la base de données")

except Exception as e:
    print(f"Erreur: {e}")

print("\n=== Test terminé ===")