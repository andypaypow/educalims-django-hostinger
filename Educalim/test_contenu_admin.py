#!/usr/bin/env python
import os
import sys
import django

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'site_educatif.settings')
django.setup()

from educalims.models import Discipline, Cycle, Niveau, Contenu
from django.contrib.auth.models import User

def test_contenu_creation():
    """Test la création d'un contenu pour vérifier que la récursion est résolue"""
    print("Test de création d'un contenu...")
    
    try:
        # Récupérer ou créer des données de test
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
        
        # Créer un utilisateur admin si nécessaire
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={'is_staff': True, 'is_superuser': True}
        )
        
        # Créer un contenu de test
        contenu = Contenu(
            titre="Test de contenu",
            description="Description de test",
            discipline=discipline,
            niveau=niveau,
            type_contenu="fiche"
        )
        
        # Sauvegarder le contenu
        contenu.save()
        print(f"Contenu créé avec succès: {contenu}")
        print(f"Str representation: {str(contenu)}")
        
        # Tester les propriétés
        print(f"Propriété is_college: {contenu.is_college}")
        print(f"Propriété is_lycee: {contenu.is_lycee}")
        print(f"Propriété unite_apprentissage_display: {contenu.unite_apprentissage_display}")
        
        print("Test reussi - Pas de recursion detectee!")
        return True
        
    except Exception as e:
        print(f"Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_contenu_creation()
    sys.exit(0 if success else 1)