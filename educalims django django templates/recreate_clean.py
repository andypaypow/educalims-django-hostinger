# -*- coding: utf-8 -*-
from educalims_app.models import Cycle, Discipline, Niveau, Unite
from django.db import connection

# Supprimer tout
Unite.objects.all().delete()
Niveau.objects.all().delete()
Discipline.objects.all().delete()
Cycle.objects.all().delete()

# Reset sequences
with connection.cursor() as cursor:
    cursor.execute("DELETE FROM sqlite_sequence WHERE name LIKE 'educalims_app%'%")

# Creer les donnees
cycle = Cycle.objects.create(nom="Lycée", description="Enseignement secondaire du lycée", ordre=3)
discipline = Discipline.objects.create(nom="Sciences de la Vie et de la Terre", cycle=cycle, description="SVT", ordre=1)
terminale = Niveau.objects.create(nom="Terminale", discipline=discipline, description="Classe de Terminale", ordre=3)
term_c = Niveau.objects.create(nom="Terminale C", discipline=discipline, parent=terminale, ordre=1)
term_d = Niveau.objects.create(nom="Terminale D", discipline=discipline, parent=terminale, ordre=2)

# Terminale C - Partie 1
p1 = Unite.objects.create(titre="PARTIE 1. UNICITE GENETIQUE ET POLYMORPHISME DES ESPECES", niveau=term_c, ordre=1)
Unite.objects.create(titre="Chapitre 1. Les mutations et le fonctionnement cellulaire", niveau=term_c, parent=p1, ordre=1)
Unite.objects.create(titre="Chapitre 2. Les mecanismes fondamentaux de la reproduction sexuee", niveau=term_c, parent=p1, ordre=2)
Unite.objects.create(titre="Chapitre 3. La reproduction sexuee et les brassages genetiques", niveau=term_c, parent=p1, ordre=3)
Unite.objects.create(titre="Chapitre 4. La diversite genetique des populations", niveau=term_c, parent=p1, ordre=4)
Unite.objects.create(titre="Chapitre 5. Les previsions en genetique humaine", niveau=term_c, parent=p1, ordre=5)

# Terminale C - Partie 2
p2 = Unite.objects.create(titre="PARTIE 2. REPONSE IMMUNOLOGIQUE ET MAINTIEN DE L'INTEGRITE DE L'ORGANISME", niveau=term_c, ordre=2)
Unite.objects.create(titre="Chapitre 6. L'organisme distingue le soi du non-soi", niveau=term_c, parent=p2, ordre=6)
Unite.objects.create(titre="Chapitre 7. Le deroulement de la reponse immunitaire", niveau=term_c, parent=p2, ordre=7)
Unite.objects.create(titre="Chapitre 8. Les dereglements, deficiencies et les aides au systeme immunitaire", niveau=term_c, parent=p2, ordre=8)

# Terminale C - Partie 3
p3 = Unite.objects.create(titre="PARTIE 3. TRANSMISSION DE L'INFORMATION DANS L'ORGANISME", niveau=term_c, ordre=3)
Unite.objects.create(titre="Chapitre 9. La communication nerveuse", niveau=term_c, parent=p3, ordre=9)
Unite.objects.create(titre="Chapitre 10. La communication hormonale", niveau=term_c, parent=p3, ordre=10)
Unite.objects.create(titre="Chapitre 11. La regulation de la pression arterielle", niveau=term_c, parent=p3, ordre=11)
Unite.objects.create(titre="Chapitre 12. La regulation des taux des hormones sexuelles", niveau=term_c, parent=p3, ordre=12)
Unite.objects.create(titre="Chapitre 13. La maitrise de la reproduction sexuee", niveau=term_c, parent=p3, ordre=13)

# Terminale D - Partie 1
p1d = Unite.objects.create(titre="PARTIE 1. HISTOIRE ET EVOLUTION DE LA TERRE ET DES ETRES VIVANTS", niveau=term_d, ordre=1)
Unite.objects.create(titre="Chapitre 1. La formation de la planete terre et les premieres etapes de la vie", niveau=term_d, parent=p1d, ordre=1)
Unite.objects.create(titre="Chapitre 2. Les mecanismes de l'evolution", niveau=term_d, parent=p1d, ordre=2)
Unite.objects.create(titre="Chapitre 3. La lignee humaine", niveau=term_d, parent=p1d, ordre=3)

# Terminale D - Partie 2
p2d = Unite.objects.create(titre="PARTIE 2. UNICITE GENETIQUE ET POLYMORPHISME DES ESPECES", niveau=term_d, ordre=2)
Unite.objects.create(titre="Chapitre 4. Les mutations et le fonctionnement cellulaire", niveau=term_d, parent=p2d, ordre=4)
Unite.objects.create(titre="Chapitre 5. Les mecanismes fondamentaux de la reproduction sexuee", niveau=term_d, parent=p2d, ordre=5)
Unite.objects.create(titre="Chapitre 6. La reproduction sexuee et les brassages genetiques", niveau=term_d, parent=p2d, ordre=6)
Unite.objects.create(titre="Chapitre 7. La diversite genetique des populations", niveau=term_d, parent=p2d, ordre=7)
Unite.objects.create(titre="Chapitre 8. Les previsions en genetique humaine", niveau=term_d, parent=p2d, ordre=8)

# Terminale D - Partie 3
p3d = Unite.objects.create(titre="PARTIE 3. REPONSE IMMUNOLOGIQUE ET MAINTIEN DE L'INTEGRITE DE L'ORGANISME", niveau=term_d, ordre=3)
Unite.objects.create(titre="Chapitre 9. L'organisme distingue le soi du non-soi", niveau=term_d, parent=p3d, ordre=9)

print("Donnees creees sans accents!")
print(f"Cycle: {cycle.nom} - {cycle.description}")
