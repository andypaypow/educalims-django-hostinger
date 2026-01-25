# -*- coding: utf-8 -*-
"""
Script pour créer un ProduitAbonnement par défaut pour Filtre Expert +
Usage: python create_produit_abonnement.py
"""
import os
import sys

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Setup Django - ajuster le path si nécessaire
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hippie_project.settings')

import django
django.setup()

from hippie.models import ProduitAbonnement

def create_default_product():
    """Crée le produit d'abonnement par défaut avec les infos Cyberschool"""

    # Configuration Cyberschool (infos fournies par l'utilisateur)
    CYBERSCHOOL_PRODUCT_ID = "KzIfBGUYU6glnH3JlsbZ"
    CYBERSCHOOL_ACCOUNT_CODE = "ACC_6835C458B85FF"
    CYBERSCHOOL_BASE_URL = "https://sumb.cyberschool.ga/"
    PRIX = 100  # FCFA

    # Vérifier si le produit existe déjà
    existing = ProduitAbonnement.objects.filter(
        produit_id=CYBERSCHOOL_PRODUCT_ID
    ).first()

    if existing:
        print(f"✅ Le produit existe déjà: {existing.nom}")
        print(f"   Prix: {existing.prix} FCFA")
        print(f"   URL: {existing.url_paiement}")
        print(f"   Actif: {existing.est_actif}")
        print(f"   ID Cyberschool: {existing.produit_id}")

        # Demander si on veut le mettre à jour
        try:
            reponse = input("\nMettre à jour ce produit ? (o/n): ")
            if reponse.lower() == 'o':
                existing.nom = "Filtre Expert + - Accès Journalier"
                existing.prix = PRIX
                existing.duree_jours = 1
                existing.url_paiement = CYBERSCHOOL_BASE_URL
                existing.description = "Accès illimité à Filtre Expert + pendant 24h (jusqu'à 23h59)"
                existing.est_actif = True
                existing.save()
                print("✅ Produit mis à jour !")
        except (EOFError, KeyboardInterrupt):
            print("\n⏭️  Passage de la mise à jour (mode non-interactif)")

        return existing

    # Créer le nouveau produit
    produit = ProduitAbonnement.objects.create(
        nom="Filtre Expert + - Accès Journalier",
        produit_id=CYBERSCHOOL_PRODUCT_ID,
        prix=PRIX,  # 100 FCFA
        duree_jours=1,  # 1 jour
        url_paiement=CYBERSCHOOL_BASE_URL,
        description="Accès illimité à Filtre Expert + pendant 24h (jusqu'à 23h59)",
        est_actif=True
    )

    print(f"✅ Produit créé avec succès !")
    print(f"   Nom: {produit.nom}")
    print(f"   ID Cyberschool: {produit.produit_id}")
    print(f"   Prix: {produit.prix} FCFA")
    print(f"   Durée: {produit.duree_jours} jour(s)")
    print(f"   URL base: {produit.url_paiement}")
    print(f"   Actif: {produit.est_actif}")
    print()
    print(f"📋 Lien de paiement complet:")
    print(f"   {CYBERSCHOOL_BASE_URL}?productId={CYBERSCHOOL_PRODUCT_ID}&operationAccountCode={CYBERSCHOOL_ACCOUNT_CODE}&maison=moov&amount={PRIX}")

    return produit


if __name__ == '__main__':
    print("=" * 60)
    print("Creation du Produit d'Abonnement Filtre Expert +")
    print("=" * 60)
    print()

    try:
        produit = create_default_product()
        print("\n" + "=" * 60)
        print("✅ Operation terminee avec succes !")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
