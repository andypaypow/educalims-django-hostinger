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
    from django.contrib.staticfiles.storage import staticfiles_storage

    # Mapping des partenaires vers leurs logos statiques (pour GM et EDUCALIMs)
    static_logos = {
        "GM": "gosen/images/partners/logo GM..webp",
        "EDUCALIMs": "gosen/images/partners/logo EDUCALIMs - Rachelle Mbouala.png",
    }

    partners = Partner.objects.filter(est_actif=True).order_by("ordre_affichage", "nom")
    partners_data = []
    for partner in partners:
        partner_data = {
            "nom": partner.nom or "",
            "lien": partner.lien or "",
            "description": partner.description or "",
        }

        # Utiliser les logos statiques pour GM et EDUCALIMs
        # Utiliser les logos uploadés via admin pour les autres
        if partner.nom and partner.nom in static_logos:
            # Logo statique (avec hash Whitenoise)
            partner_data["logo"] = staticfiles_storage.url(static_logos[partner.nom])
        elif partner.logo:
            # Logo uploadé via admin (fichier media - pas de hash)
            partner_data["logo"] = partner.logo.url
        else:
            # Pas de logo
            partner_data["logo"] = ""

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
        indicatif = data.get("indicatif", "").strip()
        whatsapp = data.get("whatsapp", "").strip()
        type_demande = data.get("type_demande", "autre").strip()
        message = data.get("message", "").strip()

        # Validation
        if not nom:
            return JsonResponse({"success": False, "error": "Le nom est obligatoire"}, status=400)
        if not indicatif:
            return JsonResponse({"success": False, "error": "L'indicatif est obligatoire"}, status=400)
        if not whatsapp:
            return JsonResponse({"success": False, "error": "Le numéro WhatsApp est obligatoire"}, status=400)

        # Valider que le numéro contient uniquement des chiffres
        if not whatsapp.isdigit():
            return JsonResponse({"success": False, "error": "Le numéro WhatsApp doit contenir uniquement des chiffres"}, status=400)

        # Valider la longueur du numéro (entre 6 et 15 chiffres)
        if len(whatsapp) < 6 or len(whatsapp) > 15:
            return JsonResponse({"success": False, "error": "Le numéro WhatsApp doit contenir entre 6 et 15 chiffres"}, status=400)

        if not message:
            return JsonResponse({"success": False, "error": "Le message est obligatoire"}, status=400)

        if len(message) < 10:
            return JsonResponse({"success": False, "error": "Le message doit contenir au moins 10 caractères"}, status=400)

        # Combiner l'indicatif et le numéro
        whatsapp_complet = f"{indicatif}{whatsapp}"

        # Enregistrer le message
        ContactMessage.objects.create(
            nom=nom,
            email=whatsapp_complet,  # Stocker dans le champ email pour compatibilité
            type_demande=type_demande,
            message=message
        )

        return JsonResponse({"success": True, "message": "Message envoyé avec succès"})

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Données JSON invalides"}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
