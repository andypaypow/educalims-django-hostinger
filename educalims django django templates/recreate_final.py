# -*- coding: utf-8 -*-
from educalims_app.models import Cycle, Discipline, Niveau, Unite
from django.db import connection

# Supprimer tout
Unite.objects.all().delete()
Niveau.objects.all().delete()
Discipline.objects.all().delete()
Cycle.objects.all().delete()

# Reset
with connection.cursor() as cursor:
    for table in ['educalims_app_cycle', 'educalims_app_discipline', 'educalims_app_niveau', 'educalims_app_unite']:
        cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'")

# Creer avec les donnees exactes
cycle = Cycle.objects.create(nom="Lyce", description="Enseignement secondaire du lyce", ordre=3)
discipline = Discipline.objects.create(nom="Sciences de la Vie et de la Terre", cycle=cycle, description="SVT", ordre=1)
terminale = Niveau.objects.create(nom="Terminale", discipline=discipline, parent=None, description="Classe de Terminale", ordre=3)
term_c = Niveau.objects.create(nom="Terminale C", discipline=discipline, parent=terminale, ordre=1)
term_d = Niveau.objects.create(nom="Terminale D", discipline=discipline, parent=terminale, ordre=2)

# Terminale C - Partie 1
p1_c = Unite.objects.create(titre="PARTIE 1. UNICITE GENETIQUE ET POLYMORPHISME DES ESPECES", niveau=term_c, ordre=1)
Unite.objects.create(titre="Chapitre 1. Les mutations et le fonctionnement cellulaire", niveau=term_c, parent=p1_c, ordre=1)
Unite.objects.create(titre="Chapitre 2. Les mecanismes fondamentaux de la reproduction sexuee", niveau=term_c, parent=p1_c, ordre=2)
Unite.objects.create(titre="Chapitre 3. La reproduction sexuee et les brassages genetiques", niveau=term_c, parent=p1_c, ordre=3)
Unite.objects.create(titre="Chapitre 4. La diversite genetique des populations", niveau=term_c, parent=p1_c, ordre=4)
Unite.objects.create(titre="Chapitre 5. Les previsions en genetique humaine", niveau=term_c, parent=p1_c, ordre=5)

# Terminale C - Partie 2
p2_c = Unite.objects.create(titre="PARTIE 2. REPONSE IMMUNOLOGIQUE ET MAINTIEN DE L'INTEGRITE DE L'ORGANISME", niveau=term_c, ordre=2)
Unite.objects.create(titre="Chapitre 6. L'organisme distingue le soi du non-soi", niveau=term_c, parent=p2_c, ordre=6)
Unite.objects.create(titre="Chapitre 7. Le deroulement de la reponse immunitaire", niveau=term_c, parent=p2_c, ordre=7)
Unite.objects.create(titre="Chapitre 8. Les dereglements, deficiencies et les aides au systeme immunitaire", niveau=term_c, parent=p2_c, ordre=8)

# Terminale C - Partie 3
p3_c = Unite.objects.create(titre="PARTIE 3. TRANSMISSION DE L'INFORMATION DANS L'ORGANISME", niveau=term_c, ordre=3)
Unite.objects.create(titre="Chapitre 9. La communication nerveuse", niveau=term_c, parent=p3_c, ordre=9)
Unite.objects.create(titre="Chapitre 10. La communication hormonale", niveau=term_c, parent=p3_c, ordre=10)
Unite.objects.create(titre="Chapitre 11. La regulation de la pression arterielle", niveau=term_c, parent=p3_c, ordre=11)
Unite.objects.create(titre="Chapitre 12. La regulation des taux des hormones sexuelles", niveau=term_c, parent=p3_c, ordre=12)
Unite.objects.create(titre="Chapitre 13. La maitrise de la reproduction sexuee", niveau=term_c, parent=p3_c, ordre=13)

# Terminale D - Partie 1
p1_d = Unite.objects.create(titre="PARTIE 1. HISTOIRE ET EVOLUTION DE LA TERRE ET DES ETRES VIVANTS", niveau=term_d, ordre=1)
Unite.objects.create(titre="Chapitre 1. La formation de la planete terre et les premieres etapes de la vie", niveau=term_d, parent=p1_d, ordre=1)
Unite.objects.create(titre="Chapitre 2. Les mecanismes de l'evolution", niveau=term_d, parent=p1_d, ordre=2)
Unite.objects.create(titre="Chapitre 3. La lignee humaine", niveau=term_d, parent=p1_d, ordre=3)

# Terminale D - Partie 2
p2_d = Unite.objects.create(titre="PARTIE 2. UNICITE GENETIQUE ET POLYMORPHISME DES ESPECES", niveau=term_d, ordre=2)
Unite.objects.create(titre="Chapitre 4. Les mutations et le fonctionnement cellulaire", niveau=term_d, parent=p2_d, ordre=4)
Unite.objects.create(titre="Chapitre 5. Les mecanismes fondamentaux de la reproduction sexuee", niveau=term_d, parent=p2_d, ordre=5)
Unite.objects.create(titre="Chapitre 6. La reproduction sexuee et les brassages genetiques", niveau=term_d, parent=p2_d, ordre=6)
Unite.objects.create(titre="Chapitre 7. La diversite genetique des populations", niveau=term_d, parent=p2_d, ordre=7)
Unite.objects.create(titre="Chapitre 8. Les previsions en genetique humaine", niveau=term_d, parent=p2_d, ordre=8)

# Terminale D - Partie 3
p3_d = Unite.objects.create(titre="PARTIE 3. REPONSE IMMUNOLOGIQUE ET MAINTIEN DE L'INTEGRITE DE L'ORGANISME", niveau=term_d, ordre=3)
Unite.objects.create(titre="Chapitre 9. L'organisme distingue le soi du non-soi", niveau=term_d, parent=p3_d, ordre=9)

print("Donnees creees: " + str(Unite.objects.count()))

# Maintenant ajouter les accents
accents = {
    "Lyce": "Lyce",
    "GENETIQUE": "GENETIQUE",
    "ESPECES": "ESPECES",
    "REPONSE": "REPONSE",
    "INTEGRITE": "INTEGRITE",
    "EVOLUTION": "EVOLUTION",
    "ETRES": "ETRES",
}

# En fait, on utilise la methode de correction qui marche
# Pour chaque objet, decoder les bytes
for obj in list(Cycle.objects.all()) + list(Discipline.objects.all()) + list(Niveau.objects.all()) + list(Unite.objects.all()):
    for field in ['nom', 'description', 'titre']:
        if hasattr(obj, field):
            value = getattr(obj, field)
            if value:
                try:
                    # Convertir correctement
                    new_value = value.encode('latin-1').decode('utf-8')
                    setattr(obj, field, new_value)
                except:
                    pass
    obj.save()

print("Accident ajoutes!")
print("Cycle: " + Cycle.objects.first().nom)
