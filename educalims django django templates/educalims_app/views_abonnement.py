# -*- coding: utf-8 -*-
"""
Vues pour le système d'abonnement par discipline.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import timedelta
import json
import hashlib
import secrets

from .models import (
    Cycle, Discipline, TelegramUser,
    Seance, Abonnement, Transaction, TypeAbonnement, StatutAbonnement
)


# ============================================================================
# PRIX DES ABONNEMENTS (en FCFA)
# ============================================================================
PRIX_ABONNEMENTS = {
    TypeAbonnement.ESSENTIEL: 2500,
    TypeAbonnement.SEANCE_UNIQUE: 1000,
    TypeAbonnement.SEANCE_INTEGRAL: 10000,
}

# Durée des abonnements (en jours)
DUREE_ABONNEMENTS = {
    TypeAbonnement.ESSENTIEL: 365,  # 1 an
    TypeAbonnement.SEANCE_UNIQUE: 7,   # 7 jours
    TypeAbonnement.SEANCE_INTEGRAL: 365,  # 1 an
}


# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def a_acces_essentiel(utilisateur, discipline):
    """
    Vérifie si l'utilisateur a un abonnement Essentiel actif pour cette discipline.
    (Obsolète: utiliser a_acces_essentiel_niveau à la place)
    """
    if not utilisateur:
        return False

    return Abonnement.objects.filter(
        utilisateur=utilisateur,
        discipline=discipline,
        type_abonnement=TypeAbonnement.ESSENTIEL,
        statut=StatutAbonnement.ACTIF,
        date_debut__lte=timezone.now(),
        date_fin__gte=timezone.now()
    ).exists()


def a_acces_essentiel_niveau(utilisateur, niveau):
    """
    Vérifie si l'utilisateur a un abonnement Essentiel actif pour ce niveau.
    Condition requise pour accéder aux séances.
    """
    if not utilisateur:
        return False

    return Abonnement.objects.filter(
        utilisateur=utilisateur,
        niveau=niveau,
        type_abonnement=TypeAbonnement.ESSENTIEL,
        statut=StatutAbonnement.ACTIF,
        date_debut__lte=timezone.now(),
        date_fin__gte=timezone.now()
    ).exists()


def a_deja_abonnement_seance(utilisateur, discipline):
    """
    Vérifie si l'utilisateur a déjà un abonnement de séance (Unique ou Intégral)
    actif pour cette discipline.
    (Obsolète: utiliser a_deja_abonnement_seance_niveau à la place)
    """
    if not utilisateur:
        return False

    return Abonnement.objects.filter(
        utilisateur=utilisateur,
        discipline=discipline,
        type_abonnement__in=[TypeAbonnement.SEANCE_UNIQUE, TypeAbonnement.SEANCE_INTEGRAL],
        statut=StatutAbonnement.ACTIF,
        date_debut__lte=timezone.now(),
        date_fin__gte=timezone.now()
    ).exists()


def a_deja_abonnement_seance_niveau(utilisateur, niveau):
    """
    Vérifie si l'utilisateur a déjà un abonnement de séance (Unique ou Intégral)
    actif pour ce niveau.
    """
    if not utilisateur:
        return False

    return Abonnement.objects.filter(
        utilisateur=utilisateur,
        niveau=niveau,
        type_abonnement__in=[TypeAbonnement.SEANCE_UNIQUE, TypeAbonnement.SEANCE_INTEGRAL],
        statut=StatutAbonnement.ACTIF,
        date_debut__lte=timezone.now(),
        date_fin__gte=timezone.now()
    ).exists()


# ============================================================================
# VUES PUBLIQUES
# ============================================================================

def abonnement_choix_discipline(request):
    """
    Étape 1 : Sélection du cycle
    Affiche une grille de tous les cycles disponibles.
    """
    cycles = Cycle.objects.all().prefetch_related('disciplines')

    context = {
        'cycles': cycles,
    }

    return render(request, 'educalims_app/abonnement/choix_cycle.html', context)


def abonnement_disciplines_par_cycle(request, cycle_id):
    """
    Étape 1b : Sélection de la discipline pour un cycle donné
    Affiche les disciplines disponibles pour le cycle sélectionné.
    """
    cycle = get_object_or_404(Cycle, pk=cycle_id)

    # Disciplines de ce cycle
    disciplines = Discipline.objects.filter(cycle=cycle)

    context = {
        'cycle': cycle,
        'disciplines': disciplines,
    }

    return render(request, 'educalims_app/abonnement/choix_discipline.html', context)


def abonnement_choix_niveau(request, discipline_id):
    """
    Étape 3 : Sélection du niveau pour une discipline donnée
    Affiche les niveaux disponibles pour la discipline sélectionnée.
    Seuls les niveaux sans enfants (feuilles) sont affichés.
    """
    from .models import Niveau

    discipline = get_object_or_404(Discipline, pk=discipline_id)
    cycle = discipline.cycle

    # Niveaux de cette discipline qui n'ont pas d'enfants (niveaux "feuilles")
    # Si un niveau a des enfants, il ne s'affiche pas, seuls les enfants s'affichent
    from django.db.models import Q
    niveaux_avec_enfants = Niveau.objects.filter(discipline=discipline).filter(
        Q(enfants__isnull=False)
    ).values_list('pk', flat=True).distinct()

    niveaux = Niveau.objects.filter(
        discipline=discipline
    ).exclude(
        pk__in=niveaux_avec_enfants
    ).order_by('ordre', 'nom')

    context = {
        'discipline': discipline,
        'cycle': cycle,
        'niveaux': niveaux,
    }

    return render(request, 'educalims_app/abonnement/choix_niveau.html', context)


def abonnement_choix_formule(request, niveau_id):
    """
    Étape 4 : Choix de la formule pour un niveau donné
    Affiche les options d'abonnement pour le niveau sélectionné.

    Règles :
    - Accès Essentiel : toujours disponible
    - Séance Unique : disponible SEULEMENT si l'utilisateur a déjà l'Accès Essentiel
    - séance intégrale : disponible SEULEMENT si l'utilisateur a déjà l'Accès Essentiel
    """
    from .models import Niveau

    niveau = get_object_or_404(Niveau, pk=niveau_id)
    discipline = niveau.discipline
    cycle = discipline.cycle

    # Récupérer l'utilisateur Telegram depuis la session ou les headers
    telegram_user = getattr(request, 'telegram_user', None)

    # Vérifier si l'utilisateur a l'Accès Essentiel pour ce niveau
    a_essentiel = a_acces_essentiel_niveau(telegram_user, niveau) if telegram_user else False

    # Vérifier les abonnements existants pour ce niveau
    abonnements_existants = []
    if telegram_user:
        abonnements_existants = list(Abonnement.objects.filter(
            utilisateur=telegram_user,
            niveau=niveau,
            statut=StatutAbonnement.ACTIF
        ).select_related('seance'))

    # Vérifier si l'utilisateur a déjà un abonnement de séance pour ce niveau
    a_deja_seance = a_deja_abonnement_seance_niveau(telegram_user, niveau) if telegram_user else False

    context = {
        'niveau': niveau,
        'discipline': discipline,
        'cycle': cycle,
        'prix_abonnements': PRIX_ABONNEMENTS,
        'abonnements_existants': abonnements_existants,
        'a_essentiel': a_essentiel,
        'a_deja_seance': a_deja_seance,
    }

    return render(request, 'educalims_app/abonnement/choix_formule.html', context)


def abonnement_choix_seance(request, niveau_id):
    """
    Étape 4b : Choix de la séance (pour formule Séance Unique)
    Affiche les séances disponibles pour la discipline du niveau.
    """
    from .models import Niveau

    niveau = get_object_or_404(Niveau, pk=niveau_id)
    discipline = niveau.discipline
    cycle = discipline.cycle

    # Séances à venir de cette discipline
    seances = Seance.objects.filter(
        discipline=discipline,
        est_active=True,
        date_heure__gt=timezone.now()
    ).order_by('date_heure')

    context = {
        'niveau': niveau,
        'discipline': discipline,
        'cycle': cycle,
        'seances': seances,
    }

    return render(request, 'educalims_app/abonnement/choix_seance.html', context)


def abonnement_paiement(request, niveau_id, type_abonnement):
    """
    Étape 5 : Page de paiement
    Initialise une transaction et redirige vers la page de paiement.
    """
    from .models import Niveau

    niveau = get_object_or_404(Niveau, pk=niveau_id)
    discipline = niveau.discipline
    cycle = discipline.cycle

    # Vérifier que le type d'abonnement est valide
    types_valides = [t[0] for t in TypeAbonnement.choices]
    if type_abonnement not in types_valides:
        return redirect('educalims_app:abonnement_choix_formule', niveau_id=niveau_id)

    # Récupérer l'utilisateur Telegram
    telegram_user = getattr(request, 'telegram_user', None)

    if not telegram_user:
        return render(request, 'educalims_app/abonnement/erreur.html', {
            'message': "Vous devez être connecté via Telegram pour vous abonner."
        })

    # Vérifier les conditions d'accès
    if type_abonnement in [TypeAbonnement.SEANCE_UNIQUE, TypeAbonnement.SEANCE_INTEGRAL]:
        if not a_acces_essentiel_niveau(telegram_user, niveau):
            return render(request, 'educalims_app/abonnement/erreur.html', {
                'message': f"Vous devez d'abord avoir l'Accès Essentiel pour {discipline.nom} - {niveau.nom} avant de pouvoir vous abonner aux séances."
            })

    # Créer une transaction
    montant = PRIX_ABONNEMENTS[type_abonnement]
    reference = _generer_reference_transaction()

    transaction = Transaction.objects.create(
        reference=reference,
        utilisateur=telegram_user,
        montant=montant,
        devise='XAF'
    )

    # Créer l'abonnement (en attente de paiement)
    date_debut = timezone.now()
    date_fin = date_debut + timedelta(days=DUREE_ABONNEMENTS[type_abonnement])

    abonnement = Abonnement.objects.create(
        utilisateur=telegram_user,
        discipline=discipline,
        niveau=niveau,
        type_abonnement=type_abonnement,
        statut=StatutAbonnement.EN_ATTENTE,
        date_debut=date_debut,
        date_fin=date_fin,
        montant_paye=0,
        reference_transaction=reference
    )

    # Lier l'abonnement à la transaction
    transaction.abonnements.add(abonnement)

    # URL de retour après paiement (succès ou échec)
    url_succes = request.build_absolute_uri(f'/abonnement/succes/{reference}/')
    url_echec = request.build_absolute_uri(f'/abonnement/echec/{reference}/')
    url_callback = request.build_absolute_uri(f'/api/payment/callback/{reference}/')

    # TODO: Intégrer avec un vrai prestataire de paiement (Orange Money, MTN MoMo, etc.)
    # Pour l'instant, on simule avec une page de paiement de test

    context = {
        'niveau': niveau,
        'discipline': discipline,
        'cycle': cycle,
        'type_abonnement': type_abonnement,
        'type_abonnement_display': dict(TypeAbonnement.choices)[type_abonnement],
        'montant': montant,
        'reference': reference,
        'transaction': transaction,
        'url_succes': url_succes,
        'url_echec': url_echec,
        'url_callback': url_callback,
    }

    return render(request, 'educalims_app/abonnement/paiement.html', context)


def abonnement_succes(request, reference):
    """
    Page de succès après paiement.
    """
    transaction = get_object_or_404(Transaction, reference=reference)

    # Récupérer le niveau, la discipline et le cycle depuis le premier abonnement
    niveau = None
    discipline = None
    cycle = None
    if transaction.abonnements.exists():
        premier_abonnement = transaction.abonnements.first()
        niveau = premier_abonnement.niveau
        discipline = premier_abonnement.discipline
        cycle = discipline.cycle if discipline else None

    context = {
        'transaction': transaction,
        'abonnements': transaction.abonnements.all(),
        'niveau': niveau,
        'discipline': discipline,
        'cycle': cycle,
    }

    return render(request, 'educalims_app/abonnement/succes.html', context)


def abonnement_echec(request, reference):
    """
    Page d'échec après paiement.
    """
    transaction = get_object_or_404(Transaction, reference=reference)

    # Récupérer le niveau, la discipline et le cycle depuis le premier abonnement
    niveau = None
    discipline = None
    cycle = None
    if transaction.abonnements.exists():
        premier_abonnement = transaction.abonnements.first()
        niveau = premier_abonnement.niveau
        discipline = premier_abonnement.discipline
        cycle = discipline.cycle if discipline else None

    context = {
        'transaction': transaction,
        'niveau': niveau,
        'discipline': discipline,
        'cycle': cycle,
    }

    return render(request, 'educalims_app/abonnement/echec.html', context)


def abonnement_attente(request, reference):
    """
    Page d'attente pendant le traitement du paiement.
    """
    transaction = get_object_or_404(Transaction, reference=reference)

    # Récupérer le niveau, la discipline et le cycle depuis le premier abonnement
    niveau = None
    discipline = None
    cycle = None
    if transaction.abonnements.exists():
        premier_abonnement = transaction.abonnements.first()
        niveau = premier_abonnement.niveau
        discipline = premier_abonnement.discipline
        cycle = discipline.cycle if discipline else None

    context = {
        'transaction': transaction,
        'niveau': niveau,
        'discipline': discipline,
        'cycle': cycle,
    }

    return render(request, 'educalims_app/abonnement/attente.html', context)


def abonnement_mes_abonnements(request):
    """
    Page listant les abonnements de l'utilisateur.
    """
    telegram_user = getattr(request, 'telegram_user', None)

    if not telegram_user:
        return render(request, 'educalims_app/abonnement/erreur.html', {
            'message': "Vous devez être connecté via Telegram."
        })

    abonnements = Abonnement.objects.filter(
        utilisateur=telegram_user
    ).select_related('discipline', 'seance').order_by('-date_creation')

    # Grouper par discipline
    abonnements_par_discipline = {}
    for abo in abonnements:
        disc = abo.discipline
        if disc not in abonnements_par_discipline:
            abonnements_par_discipline[disc] = []
        abonnements_par_discipline[disc].append(abo)

    context = {
        'abonnements_par_discipline': abonnements_par_discipline,
        'abonnements': abonnements,
    }

    return render(request, 'educalims_app/abonnement/mes_abonnements.html', context)


def abonnement_seances(request, discipline_id):
    """
    Page listant les séances d'une discipline accessibles à l'utilisateur.
    """
    discipline = get_object_or_404(Discipline, pk=discipline_id)
    cycle = discipline.cycle
    telegram_user = getattr(request, 'telegram_user', None)

    # Toutes les séances à venir de cette discipline
    seances = Seance.objects.filter(
        discipline=discipline,
        est_active=True,
        date_heure__gt=timezone.now()
    ).order_by('date_heure')

    # Vérifier les accès pour chaque séance
    seances_avec_acces = []
    for seance in seances:
        a_acces = False
        abonnement = None

        if telegram_user:
            # Chercher un abonnement actif donnant accès à cette séance
            abonnements = Abonnement.objects.filter(
                utilisateur=telegram_user,
                discipline=discipline,
                statut=StatutAbonnement.ACTIF
            )

            for abo in abonnements:
                if abo.peut_acceder_seance(seance):
                    a_acces = True
                    abonnement = abo
                    break

        seances_avec_acces.append({
            'seance': seance,
            'a_acces': a_acces,
            'abonnement': abonnement,
        })

    context = {
        'discipline': discipline,
        'cycle': cycle,
        'seances': seances_avec_acces,
    }

    return render(request, 'educalims_app/abonnement/seances.html', context)


# ============================================================================
# API CALLBACK (WEBHOOK)
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def paiement_callback(request, reference):
    """
    Webhook de callback pour le prestataire de paiement.

    Cette URL est appelée par le prestataire de paiement pour notifier
    le succès ou l'échec d'une transaction.

    Format attendu du JSON (adaptable selon le prestataire):
    {
        "transaction_id": "ID chez le prestataire",
        "statut": "SUCCES" | "ECHEC",
        "montant": 2500,
        "signature": "signature HMAC pour vérification"
    }
    """
    try:
        # Récupérer la transaction
        transaction = get_object_or_404(Transaction, reference=reference)

        # Parser les données JSON
        donnees = json.loads(request.body)

        # TODO: Vérifier la signature HMAC pour la sécurité
        # signature_calculee = _calculer_signature(donnees)
        # if signature_calculee != donnees.get('signature'):
        #     return HttpResponse('Signature invalide', status=401)

        # Mettre à jour le statut de la transaction
        statut = donnees.get('statut', 'EN_ATTENTE')

        if statut == 'SUCCES':
            # Valider la transaction et activer les abonnements
            transaction.statut = 'SUCCES'
            transaction.date_validation = timezone.now()
            transaction.fournisseur_transaction_id = donnees.get('transaction_id', '')
            transaction.donnees_brutes = donnees
            transaction.save()

            # Activer tous les abonnements liés
            for abonnement in transaction.abonnements.all():
                abonnement.statut = StatutAbonnement.ACTIF
                abonnement.montant_paye = transaction.montant
                abonnement.save()

            return HttpResponse('OK', status=200)

        elif statut == 'ECHEC':
            transaction.statut = 'ECHEC'
            transaction.donnees_brutes = donnees
            transaction.save()

            return HttpResponse('OK', status=200)

        else:
            return HttpResponse('Statut inconnu', status=400)

    except json.JSONDecodeError:
        return HttpResponse('JSON invalide', status=400)
    except Exception as e:
        return HttpResponse(f'Erreur: {str(e)}', status=500)


@csrf_exempt
@require_http_methods(["POST"])
def paiement_callback_genrique(request):
    """
    Webhook générique pour les prestataires qui n'utilisent pas de référence
    dans l'URL. Le référence doit être dans les données JSON.

    {
        "reference": "TX-123456",
        "statut": "SUCCES",
        "transaction_id": "ID_PRESTATAIRE"
    }
    """
    try:
        donnees = json.loads(request.body)
        reference = donnees.get('reference')

        if not reference:
            return HttpResponse('Référence manquante', status=400)

        # Réutiliser la logique du callback standard
        # On simule une requête vers l'autre vue
        from django.test import RequestFactory
        factory = RequestFactory()
        callback_request = factory.post(
            f'/api/payment/callback/{reference}/',
            data=json.dumps(donnees),
            content_type='application/json'
        )
        callback_request.telegram_user = getattr(request, 'telegram_user', None)

        return paiement_callback(callback_request, reference)

    except json.JSONDecodeError:
        return HttpResponse('JSON invalide', status=400)
    except Exception as e:
        return HttpResponse(f'Erreur: {str(e)}', status=500)


# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def _generer_reference_transaction():
    """Génère une référence de transaction unique."""
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    unique = secrets.token_hex(3).upper()
    return f"TX-{timestamp}-{unique}"


def _calculer_signature(donnees, secret='SECRET_KEY'):
    """
    Calcule la signature HMAC pour vérifier l'authenticité du callback.
    À adapter selon votre prestataire de paiement.
    """
    # Chaine de données à signer (à adapter)
    chaine = f"{donnees.get('transaction_id')}{donnees.get('montant')}{donnees.get('statut')}"

    return hashlib.sha256(f"{chaine}{secret}".encode()).hexdigest()


def verifier_acces_fiches(utilisateur, discipline):
    """
    Vérifie si un utilisateur a accès aux fiches d'une discipline.
    """
    if not utilisateur:
        return False

    return Abonnement.objects.filter(
        utilisateur=utilisateur,
        discipline=discipline,
        statut=StatutAbonnement.ACTIF,
        date_debut__lte=timezone.now(),
        date_fin__gte=timezone.now()
    ).exists()


def verifier_acces_seance(utilisateur, seance):
    """
    Vérifie si un utilisateur a accès à une séance spécifique.
    """
    if not utilisateur:
        return False

    abonnements = Abonnement.objects.filter(
        utilisateur=utilisateur,
        discipline=seance.discipline,
        statut=StatutAbonnement.ACTIF,
        date_debut__lte=timezone.now(),
        date_fin__gte=timezone.now()
    )

    for abo in abonnements:
        if abo.peut_acceder_seance(seance):
            return True

    return False
