from django.db import models
from django.utils import timezone

# --- 1. Discipline (ex: Mathématiques)
class Discipline(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, help_text="Description de la discipline")
    
    def __str__(self):
        return self.nom
    
    class Meta:
        ordering = ['nom']


# --- 2. Cycle (ex: Collège)
class Cycle(models.Model):
    nom = models.CharField(max_length=50, unique=True)
    discipline = models.ForeignKey(Discipline, on_delete=models.CASCADE, related_name='cycles')
    description = models.TextField(blank=True, help_text="Description du cycle")
    
    def __str__(self):
        return f"{self.nom} ({self.discipline.nom})"
    
    class Meta:
        ordering = ['discipline', 'nom']
        unique_together = ['nom', 'discipline']


# --- 2.1. TypeEnseignement (ex: Enseignement général, Enseignement technique)
class TypeEnseignement(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, help_text="Description du type d'enseignement")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nom

    class Meta:
        ordering = ['nom']


# --- 3. Niveau (ex: 6ème) - Lié à la fois à une Discipline et à un Cycle
class Niveau(models.Model):
    nom = models.CharField(max_length=50)
    discipline = models.ForeignKey(Discipline, on_delete=models.CASCADE, related_name='niveaux')
    cycle = models.ForeignKey(Cycle, on_delete=models.CASCADE, related_name='niveaux')
    ordre = models.PositiveIntegerField(default=1, help_text="Ordre du niveau dans le cycle (ex: 6ème=1, 5ème=2, etc.)")
    description = models.TextField(blank=True, help_text="Description du niveau")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='enfants', help_text="Niveau parent (ex: Première pour Première A, B, etc.)")
    type_enseignement = models.ForeignKey(TypeEnseignement, on_delete=models.SET_NULL, null=True, blank=True, related_name='niveaux', help_text="Type d'enseignement (ex: Enseignement général, Enseignement technique)")

    def __str__(self):
        return f"{self.nom} - {self.discipline.nom} ({self.cycle.nom})"

    class Meta:
        ordering = ['ordre']
        unique_together = ['nom', 'discipline', 'cycle']


# --- 4. Palier (pour organisation séquentielle, comme par semestre)
class Palier(models.Model):
    titre = models.CharField(max_length=200)
    niveau = models.ForeignKey(Niveau, on_delete=models.CASCADE, related_name='paliers')
    numero = models.PositiveIntegerField(help_text="Numéro d'ordre du palier dans le niveau")
    description = models.TextField(blank=True, help_text="Description du palier")
    
    def __str__(self):
        return f"Palier {self.numero}: {self.titre} ({self.niveau.nom})"
    
    class Meta:
        ordering = ['niveau', 'numero']
        unique_together = ['niveau', 'numero']


# --- 5. Partie (pour organisation thématique, comme Algèbre ou Géométrie)
class Partie(models.Model):
    titre = models.CharField(max_length=200)
    niveau = models.ForeignKey(Niveau, on_delete=models.CASCADE, related_name='parties')
    description = models.TextField(blank=True, help_text="Description de la partie")
    
    def __str__(self):
        return f"{self.titre} ({self.niveau.nom})"
    
    class Meta:
        ordering = ['niveau', 'titre']


# --- 6. Chapitre - Lié soit à un Palier, soit à une Partie (ou aux deux)
class Chapitre(models.Model):
    titre = models.CharField(max_length=200)
    palier = models.ForeignKey(Palier, on_delete=models.CASCADE, related_name='chapitres',
                              blank=True, null=True, help_text="Palier associé (optionnel)")
    partie = models.ForeignKey(Partie, on_delete=models.CASCADE, related_name='chapitres',
                              blank=True, null=True, help_text="Partie associée (optionnel)")
    numero = models.PositiveIntegerField(help_text="Numéro d'ordre du chapitre")
    description = models.TextField(blank=True, help_text="Description du chapitre")
    
    def __str__(self):
        parent = self.get_parent()
        parent_info = f" ({parent})" if parent else ""
        return f"Chapitre {self.numero}: {self.titre}{parent_info}"
    
    def get_parent(self):
        """Retourne le parent (Palier ou Partie) du chapitre"""
        if self.palier:
            return self.palier
        elif self.partie:
            return self.partie
        return None
    
    def get_niveau(self):
        """Retourne le niveau associé via le palier ou la partie"""
        if self.palier:
            return self.palier.niveau
        elif self.partie:
            return self.partie.niveau
        return None
    
    class Meta:
        ordering = ['numero', 'titre']
        unique_together = ['numero', 'titre', 'palier', 'partie']


# --- 7. Leçon (l'unité d'apprentissage réelle)
class Lecon(models.Model):
    titre = models.CharField(max_length=200)
    chapitre = models.ForeignKey(Chapitre, on_delete=models.CASCADE, related_name='lecons')
    numero = models.PositiveIntegerField(help_text="Numéro d'ordre de la leçon dans le chapitre")
    description = models.TextField(blank=True, help_text="Description courte de la leçon")
    objectifs = models.TextField(blank=True, help_text="Objectifs d'apprentissage")
    
    def __str__(self):
        return f"Leçon {self.numero}: {self.titre} ({self.chapitre.titre})"
    
    def get_niveau(self):
        """Retourne le niveau via le chapitre"""
        return self.chapitre.get_niveau()
    
    class Meta:
        ordering = ['chapitre', 'numero']
        unique_together = ['chapitre', 'numero']


# --- 8. Contenu (ressources pédagogiques)
class Contenu(models.Model):
    """Modèle pour les ressources pédagogiques (fiches, sujets, cahiers types)"""

    titre = models.CharField(max_length=200, help_text="Titre du contenu")
    chapitre = models.ForeignKey(Chapitre, on_delete=models.CASCADE,
                                related_name='contenus',
                                help_text="Chapitre associé au contenu")
    fichier = models.FileField(upload_to='contenus/',
                              help_text="Fichier pédagogique (PDF, DOC, HTML, etc.)")
    description = models.TextField(blank=True, help_text="Description du contenu")

    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.titre} - {self.chapitre.titre}"

    class Meta:
        ordering = ['chapitre', 'titre']
        verbose_name = "Contenu"
        verbose_name_plural = "Contenus"


