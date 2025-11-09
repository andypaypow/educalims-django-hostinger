import os
import django

# Configurer Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'site_educatif.settings')
django.setup()

from educalims.models import Discipline, Cycle, Niveau, UniteEnseignement, Contenu

def create_test_data():
    print("Création des données de test...")

    # Créer les disciplines
    svt, created = Discipline.objects.get_or_create(nom="Sciences de la Vie et de la Terre")
    physique, created = Discipline.objects.get_or_create(nom="Physique-Chimie")
    maths, created = Discipline.objects.get_or_create(nom="Mathématiques")
    philo, created = Discipline.objects.get_or_create(nom="Philosophie")
    histoire, created = Discipline.objects.get_or_create(nom="Histoire-Géographie")

    print(f"Disciplines créées: {Discipline.objects.count()}")

    # Créer les cycles pour SVT
    college_svt, created = Cycle.objects.get_or_create(nom="Collège", discipline=svt)
    lycee_svt, created = Cycle.objects.get_or_create(nom="Lycée", discipline=svt)

    # Créer les niveaux pour SVT
    niveaux_svt = [
        ("6ème", college_svt),
        ("5ème", college_svt),
        ("4ème", college_svt),
        ("3ème", college_svt),
        ("Seconde", lycee_svt),
        ("Première", lycee_svt),
        ("Terminale", lycee_svt),
    ]

    for nom_niveau, cycle in niveaux_svt:
        niveau, created = Niveau.objects.get_or_create(nom=nom_niveau, cycle=cycle)

    print(f"Niveaux SVT créés: {college_svt.niveaux.count() + lycee_svt.niveaux.count()}")

    # Créer quelques unités d'enseignement
    niveau_6eme = Niveau.objects.get(nom="6ème", cycle=college_svt)
    niveau_5eme = Niveau.objects.get(nom="5ème", cycle=college_svt)

    unites = [
        ("L'environnement et l'activité humaine", "Chapitre", niveau_6eme),
        ("La nutrition", "Leçon", niveau_6eme),
        ("Les êtres vivants dans leur environnement", "Chapitre", niveau_5eme),
        ("La respiration", "Leçon", niveau_5eme),
    ]

    for titre, type_unite, niveau in unites:
        unite, created = UniteEnseignement.objects.get_or_create(
            titre=titre,
            type_unite=type_unite,
            niveau=niveau
        )

    print(f"Unités d'enseignement créées: {UniteEnseignement.objects.count()}")

    # Créer quelques contenus (simulés)
    unite_nutrition = UniteEnseignement.objects.get(titre="La nutrition")
    unite_respiration = UniteEnseignement.objects.get(titre="La respiration")

    # Note: Les fichiers seront créés comme des objets vides car nous n'avons pas de vrais fichiers
    # En production, vous devriez avoir de vrais fichiers à uploader
    contenus = [
        ("Fiche - Les nutriments", "Fiche", unite_nutrition),
        ("Sujet d'exercice - Nutrition", "Sujet", unite_nutrition),
        ("Cahier de TP - Nutrition", "CahierType", unite_nutrition),
        ("Fiche - L'appareil respiratoire", "Fiche", unite_respiration),
        ("Exercices - Respiration", "Sujet", unite_respiration),
    ]

    for nom, type_contenu, unite in contenus:
        contenu, created = Contenu.objects.get_or_create(
            nom=nom,
            type_contenu=type_contenu,
            defaults={'fichier': 'contenus/dummy.pdf'}  # Fichier fictif
        )
        contenu.unites.add(unite)

    print(f"Contenus créés: {Contenu.objects.count()}")

    print("\n✅ Données de test créées avec succès!")
    print(f"Total: {Discipline.objects.count()} disciplines, {UniteEnseignement.objects.count()} leçons, {Contenu.objects.count()} contenus")

if __name__ == "__main__":
    create_test_data()