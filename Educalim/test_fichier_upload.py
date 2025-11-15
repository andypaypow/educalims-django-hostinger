#!/usr/bin/env python
import os
import sys
import django
from io import BytesIO

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'site_educatif.settings')
django.setup()

from educalims.models import Discipline, Cycle, Niveau, Contenu
from django.core.files.uploadedfile import SimpleUploadedFile

def test_fichier_upload():
    """Test le téléversement de fichiers pour le modèle Contenu"""
    print("Test de téléversement de fichier...")
    
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
        
        # Créer un fichier de test
        test_file_content = b"Contenu de test pour le fichier"
        test_file = SimpleUploadedFile(
            "test_fichier.txt",
            test_file_content,
            content_type="text/plain"
        )
        
        # Créer un contenu avec fichier
        contenu = Contenu(
            titre="Test de contenu avec fichier",
            description="Description de test avec fichier",
            discipline=discipline,
            niveau=niveau,
            type_contenu="fiche",
            fichier=test_file
        )
        
        # Sauvegarder le contenu
        contenu.save()
        print(f"Contenu créé avec succès: {contenu}")
        print(f"Fichier: {contenu.fichier}")
        print(f"Fichier URL: {contenu.fichier.url if contenu.fichier else 'None'}")
        print(f"Fichier size: {contenu.fichier.size if contenu.fichier else 'None'}")
        
        # Vérifier que le fichier existe
        if contenu.fichier and os.path.exists(contenu.fichier.path):
            print(f"✅ Fichier sauvegardé à: {contenu.fichier.path}")
        else:
            print("❌ Fichier non trouvé sur le disque")
        
        print("✅ Test de téléversement réussi!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_fichier_upload()
    sys.exit(0 if success else 1)