#!/usr/bin/env python
import os
import sys
import django

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'site_educatif.settings')
django.setup()

from educalims.models import Discipline, Cycle, Niveau, Contenu
from educalims.admin import ContenuAdminForm
from django.contrib.auth.models import User
from django.test import RequestFactory

def test_admin_contenu_creation():
    """Test la création d'un contenu via l'admin comme si on venait du formulaire"""
    print("Test de création de contenu via l'admin...")
    
    try:
        # Créer une requête POST simulée
        factory = RequestFactory()
        request = factory.post('/admin/educalims/contenu/add/')
        
        # Créer un utilisateur admin si nécessaire
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={'is_staff': True, 'is_superuser': True}
        )
        request.user = admin_user
        
        # Créer les données de base
        discipline, created = Discipline.objects.get_or_create(
            nom="Mathématiques",
            defaults={'description': 'Test discipline'}
        )
        
        cycle, created = Cycle.objects.get_or_create(
            nom="Collège",
            defaults={'discipline': discipline, 'description': 'Test cycle'}
        )
        
        niveau, created = Niveau.objects.get_or_create(
            nom="6ème",
            defaults={
                'discipline': discipline,
                'cycle': cycle,
                'ordre': 1,
                'description': 'Test niveau'
            }
        )
        
        # Créer le formulaire avec les données POST
        form_data = {
            'titre': 'Test de contenu admin',
            'description': 'Description de test admin',
            'discipline': str(discipline.id),
            'niveau': str(niveau.id),
            'type_contenu': 'fiche',
            'lecons': [],
            'chapitres': []
        }
        
        # Créer une instance de contenu (sans la sauvegarder)
        contenu = Contenu()
        form = ContenuAdminForm(data=form_data, instance=contenu)
        
        # Tester la validation du formulaire (sans accéder aux propriétés qui causent la récursion)
        if form.is_valid():
            print("Formulaire valide")
            
            # Sauvegarder sans fichier
            contenu = form.save()
            print(f"Contenu sauvegardé: {contenu}")
            print(f"Représentation: {str(contenu)}")
            
            return True
        else:
            print("❌ Formulaire invalide:")
            for field, errors in form.errors.items():
                print(f"  - {field}: {errors}")
            return False
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_admin_contenu_creation()
    sys.exit(0 if success else 1)