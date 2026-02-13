"""
Vues pour gérer les logos des partenaires
"""
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from gosen.models import Partner
import os
import mimetypes


def serve_partner_logo(request, partner_id):
    """Servir le logo d'un partenaire (y compris uploadés via admin)"""
    partner = get_object_or_404(Partner, id=partner_id, est_actif=True)
    
    if not partner.logo:
        raise Http404("Ce partenaire n'a pas de logo")
    
    # Vérifier que le fichier existe
    if not partner.logo.path or not os.path.exists(partner.logo.path):
        raise Http404("Logo non trouvé")
    
    # Déterminer le type MIME
    mime_type, _ = mimetypes.guess_type(partner.logo.path)
    if mime_type is None:
        mime_type = 'application/octet-stream'
    
    # Lire et retourner le fichier
    with open(partner.logo.path, 'rb') as f:
        return HttpResponse(f.read(), content_type=mime_type)
