#!/usr/bin/env python
"""
Script de test pour diagnostiquer les problèmes de validation lors de l'enregistrement d'un contenu
"""
import os
import sys
import django

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'site_educatif.settings')
django.setup()

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import Q
from educalims.models import Discipline, Cycle, Niveau, TypeEnseignement, Palier, Partie, Chapitre, Lecon, Contenu


def creer_donnees_test():
    """Créer des données de test pour reproduire le problème"""
    print("Création des données de test...")
    
    # Créer une discipline
    discipline, _ = Discipline.objects.get_or_create(
        nom="Mathématiques",
        defaults={'description': 'Discipline de test'}
    )
    
    # Créer un cycle
    cycle, _ = Cycle.objects.get_or_create(
        nom="Collège",
        defaults={'discipline': discipline, 'description': 'Cycle de test'}
    )
    
    # Créer un niveau
    niveau, _ = Niveau.objects.get_or_create(
        nom="6ème",
        defaults={
            'discipline': discipline,
            'cycle': cycle,
            'ordre': 1,
            'description': 'Niveau de test'
        }
    )
    
    # Créer un palier
    palier = None
    try:
        palier, _ = Palier.objects.get_or_create(
            titre="Premier semestre",
            defaults={
                'niveau': niveau,
                'numero': 1,
                'description': 'Palier de test'
            }
        )
    except Exception as e:
        print(f"Erreur lors de la création du palier: {e}")
        # Utiliser un palier existant ou en créer un nouveau avec un numéro différent
        max_numero = Palier.objects.filter(niveau=niveau).order_by('-numero').first()
        next_numero = (max_numero.numero + 1) if max_numero else 1
        palier, _ = Palier.objects.get_or_create(
            titre=f"Semestre de test {next_numero}",
            defaults={
                'niveau': niveau,
                'numero': next_numero,
                'description': 'Palier de test'
            }
        )
    
    # Créer un chapitre
    chapitre = None
    try:
        chapitre, _ = Chapitre.objects.get_or_create(
            titre="Nombres et calculs",
            defaults={
                'palier': palier,
                'numero': 1,
                'description': 'Chapitre de test'
            }
        )
    except Exception as e:
        print(f"Erreur lors de la création du chapitre: {e}")
        # Utiliser un chapitre existant ou en créer un nouveau avec un numéro différent
        max_numero = Chapitre.objects.filter(
            Q(palier=palier) | Q(partie__niveau=niveau)
        ).order_by('-numero').first()
        next_numero = (max_numero.numero + 1) if max_numero else 1
        chapitre, _ = Chapitre.objects.get_or_create(
            titre=f"Chapitre de test {next_numero}",
            defaults={
                'palier': palier,
                'numero': next_numero,
                'description': 'Chapitre de test'
            }
        )
    
    # Créer une leçon
    lecon = None
    try:
        lecon, _ = Lecon.objects.get_or_create(
            titre="Addition et soustraction",
            defaults={
                'chapitre': chapitre,
                'numero': 1,
                'description': 'Leçon de test',
                'objectifs': 'Apprendre à additionner et soustraire'
            }
        )
    except Exception as e:
        print(f"Erreur lors de la création de la leçon: {e}")
        # Utiliser une leçon existante ou en créer une nouvelle avec un numéro différent
        max_numero = Lecon.objects.filter(chapitre=chapitre).order_by('-numero').first()
        next_numero = (max_numero.numero + 1) if max_numero else 1
        lecon, _ = Lecon.objects.get_or_create(
            titre=f"Leçon de test {next_numero}",
            defaults={
                'chapitre': chapitre,
                'numero': next_numero,
                'description': 'Leçon de test',
                'objectifs': 'Apprendre à additionner et soustraire'
            }
        )
    
    print(f"Données créées: discipline={discipline}, niveau={niveau}, leçon={lecon}")
    return discipline, niveau, lecon


def tester_creation_contenu_via_formulaire():
    """Tester la création d'un contenu via le formulaire d'administration"""
    print("\nTest de création de contenu via le formulaire d'administration...")
    
    # Créer un utilisateur administrateur
    admin_user, _ = User.objects.get_or_create(
        username='admin',
        defaults={
            'is_superuser': True,
            'is_staff': True,
            'email': 'admin@example.com'
        }
    )
    admin_user.set_password('admin123')
    admin_user.save()
    
    # Créer les données de test
    discipline, niveau, lecon = creer_donnees_test()
    
    # Créer un client de test
    client = Client()
    
    # Se connecter en tant qu'admin
    client.login(username='admin', password='admin123')
    
    # Créer un fichier factice
    fichier_test = SimpleUploadedFile(
        "test.pdf",
        b"file_content",
        content_type="application/pdf"
    )
    
    # Préparer les données du formulaire
    form_data = {
        'titre': 'Test de contenu mathématiques',
        'description': 'Description de test',
        'type_contenu': 'fiche',
        'discipline': discipline.id,
        'niveau': niveau.id,
        'lecons': [lecon.id],  # Ajouter la leçon
        'chapitres': [],  # Pas de chapitre pour le collège
        'fichier': fichier_test,
    }
    
    # Soumettre le formulaire
    response = client.post('/admin/educalims/contenu/add/', data=form_data)
    
    print(f"Statut de la réponse: {response.status_code}")
    
    if response.status_code == 302:
        print("Redirection réussie - Contenu créé avec succès")
        return True
    else:
        print("Erreur lors de la création du contenu")
        if response.context and 'form' in response.context:
            form = response.context['form']
            print("Erreurs du formulaire:")
            for field, errors in form.errors.items():
                print(f"  {field}: {errors}")
        else:
            print("Pas de formulaire dans le contexte de la réponse")
            print("Contenu de la réponse (premiers 1000 caractères):")
            print(response.content.decode('utf-8')[:1000])
        return False


def tester_validation_directe():
    """Tester la validation directe du modèle Contenu"""
    print("\nTest de validation directe du modèle Contenu...")
    
    # Créer les données de test
    discipline, niveau, lecon = creer_donnees_test()
    
    # Créer un fichier factice
    from io import BytesIO
    from django.core.files.base import ContentFile
    
    fichier_test = ContentFile(b"file_content", name="test.pdf")
    
    # Créer un contenu avec les bonnes relations
    try:
        contenu = Contenu(
            titre='Test de contenu mathématiques',
            description='Description de test',
            type_contenu='fiche',
            discipline=discipline,
            niveau=niveau,
            fichier=fichier_test
        )
        
        # Ajouter la leçon
        contenu.save()
        contenu.lecons.add(lecon)
        
        print(f"Contenu créé avec succès: {contenu}")
        print(f"Leçons associées: {list(contenu.lecons.all())}")
        return True
        
    except Exception as e:
        print(f"Erreur lors de la création du contenu: {e}")
        import traceback
        traceback.print_exc()
        return False


def tester_requetes_ajax():
    """Tester les requêtes AJAX utilisées dans le formulaire"""
    print("\nTest des requêtes AJAX...")
    
    # Créer les données de test
    discipline, niveau, lecon = creer_donnees_test()
    
    # Créer un client de test
    client = Client()
    
    # Tester la récupération des niveaux par discipline
    response = client.get(f'/get-niveaux-by-discipline/?discipline_id={discipline.id}')
    print(f"get-niveaux-by-discipline: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Niveaux trouvés: {len(data.get('niveaux', []))}")
    
    # Tester la récupération des unités d'apprentissage par niveau
    response = client.get(f'/get-unites-apprentissage-by-niveau/?niveau_id={niveau.id}')
    print(f"get-unites-apprentissage-by-niveau: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Cycle: {data.get('cycle')}")
        print(f"  Unités trouvées: {len(data.get('unites', []))}")
        for unite in data.get('unites', [])[:3]:  # Afficher les 3 premières
            print(f"    - {unite.get('titre')} ({unite.get('type')})")


if __name__ == '__main__':
    print("=" * 60)
    print("DIAGNOSTIC DES PROBLÈMES DE VALIDATION DE CONTENU")
    print("=" * 60)
    
    # Tester la validation directe
    validation_ok = tester_validation_directe()
    
    # Tester les requêtes AJAX
    tester_requetes_ajax()
    
    # Tester la création via formulaire
    formulaire_ok = tester_creation_contenu_via_formulaire()
    
    print("\n" + "=" * 60)
    print("RÉSUMÉ DES TESTS")
    print("=" * 60)
    print(f"Validation directe: {'✓' if validation_ok else '✗'}")
    print(f"Création via formulaire: {'✓' if formulaire_ok else '✗'}")
    
    if not formulaire_ok:
        print("\nLe problème semble être lié au formulaire d'administration.")
        print("Vérifiez les points suivants:")
        print("1. La validation dans ContenuAdminForm.clean()")
        print("2. Le fonctionnement des widgets personnalisés")
        print("3. La soumission des champs ManyToMany via JavaScript")