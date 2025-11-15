#!/usr/bin/env python
import os
import sys
import django

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'site_educatif.settings')
django.setup()

from educalims.models import Discipline, Cycle, Niveau, Contenu, Lecon, Chapitre
from educalims.admin import ContenuAdminForm
from django.contrib.auth.models import User
from django.test import RequestFactory

def test_simple_admin():
    """Test simple de création de contenu via l'admin"""
    print("Test simple de création de contenu...")
    
    try:
        # Créer les objets de base
        discipline, created = Discipline.objects.get_or_create(
            nom="Mathematiques",
            defaults={'description': 'Test discipline'}
        )
        
        cycle, created = Cycle.objects.get_or_create(
            nom="College",
            defaults={'discipline': discipline, 'description': 'Test cycle'}
        )
        
        niveau, created = Niveau.objects.get_or_create(
            nom="6eme",
            defaults={
                'discipline': discipline,
                'cycle': cycle,
                'ordre': 1,
                'description': 'Test niveau'
            }
        )
        
        # Créer le formulaire avec les données
        # Créer une leçon de test
        lecon_test = Lecon.objects.create(
            titre="Leçon test",
            chapitre=Chapitre.objects.create(
                titre="Chapitre test",
                numero=1
            ),
            numero=1,
            description="Leçon de test"
        )
        
        form_data = {
            'titre': 'Test de contenu admin',
            'description': 'Description de test admin',
            'discipline': str(discipline.id),
            'niveau': str(niveau.id),
            'type_contenu': 'fiche',
            'lecons': [lecon_test.id],
            'chapitres': []
        }
        
        # Créer une instance de contenu
        contenu = Contenu()
        form = ContenuAdminForm(data=form_data, instance=contenu)
        
        # Tester la validation
        if form.is_valid():
            print("Formulaire valide")
            contenu = form.save()
            print("Contenu sauvegarde:", contenu.titre)
            print("Test reussi!")
            return True
        else:
            print("Formulaire invalide")
            return False
        
    except Exception as e:
        print("Erreur lors du test:", str(e))
        return False

if __name__ == "__main__":
    success = test_simple_admin()
    sys.exit(0 if success else 1)