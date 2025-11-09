from django.db import models

# --- 1. Discipline (ex: SVT, Philosophie)
class Discipline(models.Model):
    nom = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nom


# --- 2. Cycle (Collège / Lycée)
class Cycle(models.Model):
    nom = models.CharField(max_length=50, unique=True)
    discipline = models.ForeignKey(Discipline, on_delete=models.CASCADE, related_name='cycles')

    def __str__(self):
        return f"{self.nom} ({self.discipline.nom})"


# --- 3. Niveau (6e, 5e, Seconde, etc.)
class Niveau(models.Model):
    nom = models.CharField(max_length=50)
    cycle = models.ForeignKey(Cycle, on_delete=models.CASCADE, related_name='niveaux')

    def __str__(self):
        return f"{self.nom} - {self.cycle.nom}"


# --- 4. Unité d’enseignement (Leçon ou Chapitre)
class UniteEnseignement(models.Model):
    TYPE_CHOIX = [
        ('Leçon', 'Leçon'),
        ('Chapitre', 'Chapitre'),
    ]
    titre = models.CharField(max_length=200)
    type_unite = models.CharField(max_length=10, choices=TYPE_CHOIX)
    niveau = models.ForeignKey(Niveau, on_delete=models.CASCADE, related_name='unites')

    def __str__(self):
        return f"{self.titre} ({self.niveau.nom})"


# --- 5. Contenu (fichier téléversé)
class Contenu(models.Model):
    TYPE_CHOIX = [
        ('Fiche', 'Fiche'),
        ('Sujet', 'Sujet'),
        ('CahierType', 'Cahier Type'),
    ]
    nom = models.CharField(max_length=200)
    type_contenu = models.CharField(max_length=20, choices=TYPE_CHOIX)
    fichier = models.FileField(upload_to='contenus/')
    
    # relation multiple : un contenu peut être lié à plusieurs unités
    unites = models.ManyToManyField(UniteEnseignement, related_name='contenus')

    def __str__(self):
        return f"{self.nom} ({self.type_contenu})"
