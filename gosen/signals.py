"""
Signaux Django pour gérer les fichiers uploadés des partenaires
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.files.storage import default_storage
import shutil
import os

@receiver(post_save, sender='gosen.Partner')
def copy_partner_logo_to_static(sender, instance, created, **kwargs):
    """Copier le logo du partenaire vers static/ après l'upload"""
    if not instance.logo:
        return
    
    # Définir les dossiers
    static_partners_dir = os.path.join('/code/staticfiles', 'gosen', 'images', 'partners')
    os.makedirs(static_partners_dir, exist_ok=True)
    
    # Copier le fichier vers static/partners/
    file_extension = instance.logo.name.split('.')[-1]
    safe_name = f"{instance.nom or 'partner'}_{instance.id}.{file_extension}"
    static_path = os.path.join(static_partners_dir, safe_name)
    
    shutil.copy(instance.logo.path, static_path)
    
    # Mettre à jour le champ logo pour pointer vers le fichier statique
    from gosen.models import Partner
    relative_path = f"gosen/images/partners/{safe_name}"
    Partner.objects.filter(id=instance.id).update(logo=relative_path)
