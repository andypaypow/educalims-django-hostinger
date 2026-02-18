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
    """Copier le logo du partenaire vers media/ après l'upload (uniquement sur PROD)"""
    # Éviter la boucle infinie - ne pas traiter si le logo commence déjà par partners/
    if instance.logo and instance.logo.name.startswith('partners/'):
        return
    
    if not instance.logo:
        return
    
    # Seulement sur PROD (DEBUG=False)
    if settings.DEBUG:
        print("DEV: pas de copie automatique du logo")
        return
    
    # Pour GM et EDUCALIMs, utiliser les logos statiques
    static_logos = ['GM', 'EDUCALIMs']
    if instance.nom in static_logos:
        # Ces partenaires utilisent des logos statiques
        return
    
    # Copier le fichier vers media/partners/
    file_extension = instance.logo.name.split('.')[-1]
    safe_name = f"partner_{instance.id}.{file_extension}"
    media_path = os.path.join(settings.MEDIA_ROOT, 'partners', safe_name)
    
    # Créer le dossier si nécessaire
    os.makedirs(os.path.dirname(media_path), exist_ok=True)
    
    # Copier le fichier
    shutil.copy(instance.logo.path, media_path)
    
    # Mettre à jour le champ logo DIRECTEMENT dans la base pour éviter la boucle
    sender.objects.filter(id=instance.id).update(logo=f"partners/{safe_name}")
    
    print(f"Signal: logo copié vers media/partners/{safe_name}")
