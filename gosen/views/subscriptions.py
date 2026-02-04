"""
Vues pour la gestion des abonnements et produits
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from gosen.models import SubscriptionProduct, SubscriptionPayment
from django.utils import timezone


def api_products_list(request):
    """API pour récupérer la liste des produits d'abonnement actifs"""
    products = SubscriptionProduct.objects.filter(est_actif=True).order_by('ordre_affichage', 'prix')

    products_data = []
    for product in products:
        products_data.append({
            'id': product.id,
            'nom': product.nom,
            'description': product.description,
            'type_abonnement': product.type_abonnement,
            'prix': float(product.prix),
            'devise': product.devise,
            'duree_jours': product.duree_jours,
            'duree_heures': product.duree_heures,
            'duree_affichage': product.duree_affichage,
            'url_moov_money': product.url_moov_money,
            'url_airtel_money': product.url_airtel_money,
            'est_populaire': product.est_populaire,
        })

    return JsonResponse({'products': products_data})


@login_required
def api_create_payment(request):
    """API pour créer un paiement à partir d'un produit"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)

    product_id = request.POST.get('product_id')
    telephone = request.POST.get('telephone')

    if not product_id or not telephone:
        return JsonResponse({'success': False, 'error': 'Paramètres manquants'}, status=400)

    try:
        product = SubscriptionProduct.objects.get(id=product_id, est_actif=True)
    except SubscriptionProduct.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Produit invalide'}, status=404)

    # Créer un paiement en attente
    payment = SubscriptionPayment.objects.create(
        utilisateur=request.user,
        produit=product,
        type_abonnement=product.type_abonnement,
        montant=product.prix,
        devise=product.devise,
        telephone=telephone,
        reference_transaction=f'PENDING-{timezone.now().timestamp()}',
        statut='en_attente'
    )

    # Générer les URLs de paiement
    payment_urls = {}
    if product.url_moov_money:
        payment_urls['moov_money'] = product.url_moov_money.replace('{telephone}', telephone).replace('{reference}', payment.reference_transaction)
    if product.url_airtel_money:
        payment_urls['airtel_money'] = product.url_airtel_money.replace('{telephone}', telephone).replace('{reference}', payment.reference_transaction)

    return JsonResponse({
        'success': True,
        'payment_id': payment.id,
        'payment_urls': payment_urls,
        'redirect': f'/payment/process/{payment.id}/'
    })
