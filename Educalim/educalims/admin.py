from django.contrib import admin
from .models import Discipline, Cycle, Niveau, UniteEnseignement, Contenu

# Enregistre tous les modèles dans l'interface d'administration
admin.site.register(Discipline)
admin.site.register(Cycle)
admin.site.register(Niveau)
admin.site.register(UniteEnseignement)
admin.site.register(Contenu)
