import os
import django

# Configuration de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'site_educatif.settings')
django.setup()

from educalims.models import Discipline, Cycle, Niveau, Partie, Chapitre

# Vérifier la discipline SVT
svt = Discipline.objects.filter(nom='SVT').first()
print(f'Discipline SVT: {svt}')

# Vérifier le cycle Lycée
lycee = Cycle.objects.filter(nom='Lycée', discipline=svt).first()
print(f'Cycle Lycée: {lycee}')

# Vérifier le niveau Seconde STMG
seconde_stmg = Niveau.objects.filter(nom='Seconde STMG').first()
print(f'Niveau Seconde STMG: {seconde_stmg}')

# Vérifier les parties
parties = Partie.objects.filter(niveau=seconde_stmg)
print(f'Nombre de parties: {parties.count()}')
for partie in parties:
    print(f'  - {partie.titre}')

# Vérifier les chapitres
chapitres = Chapitre.objects.filter(partie__in=parties)
print(f'Nombre total de chapitres: {chapitres.count()}')
for chapitre in chapitres:
    print(f'  - Chapitre {chapitre.numero}: {chapitre.titre} (Partie: {chapitre.partie.titre})')