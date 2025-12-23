# -*- coding: utf-8 -*-
from educalims_app.models import Cycle, Discipline, Niveau, Unite

import sys
import io

# Forcer UTF-8 pour la sortie
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Supprimer tout
Unite.objects.all().delete()
Niveau.objects.all().delete()
Discipline.objects.all().delete()
Cycle.objects.all().delete()

# Reset sequences
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute("DELETE FROM sqlite_sequence WHERE name LIKE 'educalims_app%'")

# Créer avec des chaînes brutes UTF-8
cycle = Cycle(id=1, nom="Lycée", description="Enseignement secondaire du lycée", ordre=3)
cycle.save()

discipline = Discipline(id=1, nom="Sciences de la Vie et de la Terre", cycle=cycle, description="SVT", ordre=1)
discipline.save()

terminale = Niveau(id=1, nom="Terminale", discipline=discipline, description="Classe de Terminale", ordre=3)
terminale.save()

term_c = Niveau(id=2, nom="Terminale C", discipline=discipline, parent=terminale, ordre=1)
term_c.save()

term_d = Niveau(id=3, nom="Terminale D", discipline=discipline, parent=terminale, ordre=2)
term_d.save()

# Créer les parties et chapitres pour Terminale C
parties_c = [
    ("PARTIE 1. UNICITÉ GÉNÉTIQUE ET POLYMORPHISME DES ESPÈCES", 1,
     ["Chapitre 1. Les mutations et le fonctionnement cellulaire",
      "Chapitre 2. Les mécanismes fondamentaux de la reproduction sexuée",
      "Chapitre 3. La reproduction sexuée et les brassages génétiques",
      "Chapitre 4. La diversité génétique des populations",
      "Chapitre 5. Les prévisions en génétique humaine"]),
    ("PARTIE 2. RÉPONSE IMMUNOLOGIQUE ET MAINTIEN DE L'INTÉGRITÉ DE L'ORGANISME", 2,
     ["Chapitre 6. L'organisme distingue le soi du non-soi",
      "Chapitre 7. Le déroulement de la réponse immunitaire",
      "Chapitre 8. Les dérèglements, déficiences et les aides au système immunitaire"]),
    ("PARTIE 3. TRANSMISSION DE L'INFORMATION DANS L'ORGANISME", 3,
     ["Chapitre 9. La communication nerveuse",
      "Chapitre 10. La communication hormonale : La régulation de la glycémie",
      "Chapitre 11. La régulation de la pression artérielle",
      "Chapitre 12. La régulation des taux des hormones sexuelles",
      "Chapitre 13. La maîtrise de la reproduction sexuée"])
]

for titre, ordre, chapitres in parties_c:
    partie = Unite(titre=titre, niveau=term_c, parent=None, ordre=ordre)
    partie.save()
    for i, chap in enumerate(chapitres, 1):
        u = Unite(titre=chap, niveau=term_c, parent=partie, ordre=i)
        u.save()

# Créer les parties et chapitres pour Terminale D
parties_d = [
    ("PARTIE 1. HISTOIRE ET ÉVOLUTION DE LA TERRE ET DES ÊTRES VIVANTS", 1,
     ["Chapitre 1. La formation de la planète terre et les premières étapes de la vie",
      "Chapitre 2. Les mécanismes de l'évolution",
      "Chapitre 3. La lignée humaine"]),
    ("PARTIE 2. UNICITÉ GÉNÉTIQUE ET POLYMORPHISME DES ESPÈCES", 2,
     ["Chapitre 4. Les mutations et le fonctionnement cellulaire",
      "Chapitre 5. Les mécanismes fondamentaux de la reproduction sexuée",
      "Chapitre 6. La reproduction sexuée et les brassages génétiques",
      "Chapitre 7. La diversité génétique des populations",
      "Chapitre 8. Les prévisions en génétique humaine"]),
    ("PARTIE 3. RÉPONSE IMMUNOLOGIQUE ET MAINTIEN DE L'INTÉGRITÉ DE L'ORGANISME", 3,
     ["Chapitre 9. L'organisme distingue le soi du non-soi"])
]

for titre, ordre, chapitres in parties_d:
    partie = Unite(titre=titre, niveau=term_d, parent=None, ordre=ordre)
    partie.save()
    for i, chap in enumerate(chapitres, 1):
        u = Unite(titre=chap, niveau=term_d, parent=partie, ordre=i)
        u.save()

print("Données recréées!")
print(f"Cycle: {cycle.nom}")
print(f"Unites: {Unite.objects.count()}")
