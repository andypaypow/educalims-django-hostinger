"""
Signaux Django pour gérer les fichiers uploadés des partenaires
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
import shutil
import os

@receiver(post_save, sender='gosen.Partner')
def copy_partner_logo_to_static(sender, instance, created, **kwargs):
    """Copier le logo du partenaire vers static/ après l'upload (uniquement sur PROD)"""
    if not instance.logo:
        return
    
    # Seulement sur PROD (DEBUG=False)
    if settings.DEBUG:
        print("DEV: pas de copie automatique du logo")
        return
    
    # Définir les dossiers
    static_partners_dir = os.path.join(settings.BASE_DIR, 'static', 'gosen', 'images', 'partners')
    os.makedirs(static_partners_dir, exist_ok=True)
    
    # Copier le fichier vers static/partners/
    file_extension = instance.logo.name.split('.')[-1]
    safe_name = f"{instance.nom or 'partner'}_{instance.id}.{file_extension}"
    static_path = os.path.join(static_partners_dir, safe_name)
    
    # Copier le fichier
    shutil.copy(instance.logo.path, static_path)
    
    # Construire le chemin relatif
    relative_path = f"gosen/images/partners/{safe_name}"
    
    # Empêcher la signalisation en boucle
    from django.db.models.signals import post_save
    post_save.disconnect(copy_partner_logo_to_static, sender='gosen.Partner')
    
    # Mettre à jour le champ logo en utilisant save() pour déclencher le signal
    instance.logo.name = relative_path
    instance.logo.path = static_path
    instance.logo.url = f"/static/gosen/images/partners/{safe_name}"
    instance.save(update_fields=['logo'])
    
    # Réactiver le signal
    post_save.connect(copy_partner_logo_to_static, sender='gosen.Partner')
    
    print(f"Signal: logo copié vers {relative_path}")
