
"""
Vues pour le formulaire de contact
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from . import contact as contact_module
import json

from gosen.models import Partner, ContactMessage
from gosen.forms import ContactForm


def contact_page(request):
    """Page de contact avec formulaire"""
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            from django.contrib import messages
            messages.success(request, "Votre message a été envoyé avec succès !")
            form = ContactForm()  # Reset form
    else:
        form = ContactForm()
    
    return render(request, "gosen/contact.html", {"form": form})


def get_partners(request):
    """API pour récupérer la liste des partenaires actifs"""
    partners = Partner.objects.filter(est_actif=True).order_by("ordre_affichage", "nom")
    partners_data = []
    for partner in partners:
        partner_data = {
            "nom": partner.nom,
            "lien": partner.lien or "",
            "description": partner.description or "",
        }
        if partner.logo:
            partner_data["logo"] = partner.logo.url
        partners_data.append(partner_data)
    return JsonResponse({"partners": partners_data})


@csrf_exempt
def submit_contact(request):
    """API pour soumettre un message de contact"""
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Méthode non autorisée"}, status=405)
    
    try:
        data = json.loads(request.body)
        nom = data.get("nom", "").strip()
        email = data.get("email", "").strip()
        type_demande = data.get("type_demande", "autre").strip()
        message = data.get("message", "").strip()
        
        # Validation
        if not nom:
            return JsonResponse({"success": False, "error": "Le nom est requis"}, status=400)
        if not email:
            return JsonResponse({"success": False, "error": "L\"email est requis"}, status=400)
        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({"success": False, "error": "L\"email n\"est pas valide"}, status=400)
        if not message:
            return JsonResponse({"success": False, "error": "Le message est requis"}, status=400)
        if len(message) < 10:
            return JsonResponse({"success": False, "error": "Le message doit contenir au moins 10 caractères"}, status=400)
        
        # Créer le message
        ContactMessage.objects.create(
            nom=nom,
            email=email,
            type_demande=type_demande,
            message=message
        )
        
        return JsonResponse({"success": True, "message": "Votre message a été envoyé avec succès !"})
        
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Données invalides"}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
