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
    static_partners_dir = os.path.join(os.environ.get('DJANGO_STATIC_ROOT', '/code/staticfiles'), 'gosen', 'images', 'partners')
    os.makedirs(static_partners_dir, exist_ok=True)
    
    # Copier le fichier vers static/partners/
    file_extension = instance.logo.name.split('.')[-1]
    safe_name = f"{instance.nom or 'partner'}_{instance.id}.{file_extension}"
    static_path = os.path.join(static_partners_dir, safe_name)
    
    shutil.copy(instance.logo.path, static_path)
    
    # Mettre à jour le chemin du logo vers static/
    instance.logo.name = f"gosen/images/partners/{safe_name}"
    instance.logo.path = static_path
    instance.logo.url = f"/static/gosen/images/partners/{safe_name}"
    
    # Sauvegarder pour mettre à jour le champ logo
    instance.save(update_fields=['logo'])
