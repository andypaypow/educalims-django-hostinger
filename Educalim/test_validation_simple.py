#!/usr/bin/env python
"""
Script simple pour tester la validation du formulaire ContenuAdminForm
"""
import os
import sys
import django

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'site_educatif.settings')
django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import Q
from educalims.models import Discipline, Cycle, Niveau, TypeEnseignement, Palier, Partie, Chapitre, Lecon, Contenu
from educalims.admin import ContenuAdminForm


def tester_validation_formulaire():
    """Tester la validation du formulaire ContenuAdminForm"""
    print("Test de validation du formulaire ContenuAdminForm...")
    
    # Récupérer ou créer des données existantes
    try:
        # D'abord, trouver une leçon existante
        lecon = Lecon.objects.first()
        
        if not lecon:
            print("Aucune leçon trouvée dans la base de données")
            return False
        
        # Ensuite, déterminer le niveau et la discipline à partir de la leçon
        niveau = lecon.chapitre.get_niveau()
        if not niveau:
            print("La leçon n'est associée à aucun niveau")
            return False
        
        discipline = niveau.discipline
        if not discipline:
            print("Le niveau n'est associé à aucune discipline")
            return False
        
        print(f"Utilisation de: discipline={discipline}, niveau={niveau}, leçon={lecon}")
        
        # Créer un fichier factice
        fichier_test = SimpleUploadedFile(
            "test.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        
        # Cas 1: Formulaire valide pour le collège (avec leçon)
        print("\nCas 1: Formulaire valide pour le collège")
        form_data = {
            'titre': 'Test de contenu mathématiques',
            'description': 'Description de test',
            'type_contenu': 'fiche',
            'discipline': discipline.id,
            'niveau': niveau.id,
            'lecons': [lecon.id],
            'chapitres': [],
        }
        
        file_data = {'fichier': fichier_test}
        form = ContenuAdminForm(data=form_data, files=file_data)
        
        if form.is_valid():
            print("OK: Formulaire valide")
            print(f"  Nettoyé: {form.cleaned_data}")
        else:
            print("ERREUR: Formulaire invalide")
            print(f"  Erreurs: {form.errors}")
            for field, errors in form.errors.items():
                print(f"    {field}: {errors}")
        
        # Cas 2: Formulaire invalide pour le collège (sans leçon)
        print("\nCas 2: Formulaire invalide pour le collège (sans leçon)")
        form_data_invalid = {
            'titre': 'Test de contenu mathématiques',
            'description': 'Description de test',
            'type_contenu': 'fiche',
            'discipline': discipline.id,
            'niveau': niveau.id,
            'lecons': [],
            'chapitres': [],
        }
        
        form_invalid = ContenuAdminForm(data=form_data_invalid, files=file_data)
        
        if form_invalid.is_valid():
            print("ERREUR: Formulaire devrait être invalide mais est valide")
        else:
            print("OK: Formulaire correctement invalide")
            print(f"  Erreurs attendues: {form_invalid.errors}")
            for field, errors in form_invalid.errors.items():
                print(f"    {field}: {errors}")
        
        # Cas 3: Test avec un niveau de lycée
        niveau_lycee = Niveau.objects.filter(cycle__nom='Lycée').first()
        if niveau_lycee:
            chapitre = Chapitre.objects.filter(
                Q(palier__niveau=niveau_lycee) | Q(partie__niveau=niveau_lycee)
            ).first()
            
            if chapitre:
                print("\nCas 3: Formulaire valide pour le lycée (avec chapitre)")
                form_data_lycee = {
                    'titre': 'Test de contenu lycée',
                    'description': 'Description de test',
                    'type_contenu': 'fiche',
                    'discipline': chapitre.get_niveau().discipline.id,
                    'niveau': chapitre.get_niveau().id,
                    'lecons': [],
                    'chapitres': [chapitre.id],
                }
                
                form_lycee = ContenuAdminForm(data=form_data_lycee, files=file_data)
                
                if form_lycee.is_valid():
                    print("OK: Formulaire valide pour le lycée")
                else:
                    print("ERREUR: Formulaire invalide pour le lycée")
                    print(f"  Erreurs: {form_lycee.errors}")
                    for field, errors in form_lycee.errors.items():
                        print(f"    {field}: {errors}")
            else:
                print("\nAucun chapitre trouvé pour le niveau de lycée")
        else:
            print("\nAucun niveau de lycée trouvé")
        
        return True
        
    except Exception as e:
        print(f"Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False


def verifier_donnees_existantes():
    """Vérifier les données existantes dans la base"""
    print("\nVérification des données existantes...")
    
    print(f"Disciplines: {Discipline.objects.count()}")
    for d in Discipline.objects.all()[:3]:
        print(f"  - {d.nom}")
    
    print(f"\nNiveaux: {Niveau.objects.count()}")
    for n in Niveau.objects.all()[:5]:
        print(f"  - {n.nom} ({n.discipline.nom}, {n.cycle.nom})")
    
    print(f"\nLeçons: {Lecon.objects.count()}")
    for l in Lecon.objects.all()[:3]:
        print(f"  - {l.titre} ({l.chapitre.titre})")
    
    print(f"\nChapitres: {Chapitre.objects.count()}")
    for c in Chapitre.objects.all()[:3]:
        parent = c.get_parent()
        parent_info = f" ({parent})" if parent else ""
        print(f"  - {c.titre}{parent_info}")


if __name__ == '__main__':
    print("=" * 60)
    print("TEST DE VALIDATION DU FORMULAIRE CONTENU")
    print("=" * 60)
    
    # Vérifier les données existantes
    verifier_donnees_existantes()
    
    # Tester la validation du formulaire
    validation_ok = tester_validation_formulaire()
    
    print("\n" + "=" * 60)
    print("RÉSUMÉ")
    print("=" * 60)
    print(f"Test de validation: {'Réussi' if validation_ok else 'Échoué'}")