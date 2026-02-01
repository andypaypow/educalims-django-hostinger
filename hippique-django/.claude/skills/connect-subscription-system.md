# Connecter le Système d'Abonnement (Côté Serveur)

## Situation Actuelle

Le bloc "Résultats + Synthèses" est contrôlé **côté serveur** via Django :
```django
{% if user.is_authenticated and has_subscription %}
    <!-- Contenu abonnement -->
{% else %}
    <!-- Message: Abonnement requis -->
{% endif %}
```

**La variable `has_subscription` est définie dans :** `/code/gosen/views/base.py`

## Connecter un Vrai Système d'Abonnement

### 1. Modifier la vue `base.py`

```python
def index(request):
    """Vue principale de l'application Gosen TurfFilter"""
    from django.utils import timezone

    has_subscription = False

    if request.user.is_authenticated:
        # REMPLACER par votre vraie logique d'abonnement
        from gosen.models_abonnement import Abonnement

        abo = Abonnement.objects.filter(
            utilisateur=request.user,
            statut='ACTIF',
            date_fin__gt=timezone.now()
        ).first()

        has_subscription = (abo is not None and abo.est_actif())

    context = {
        'has_subscription': has_subscription,
        'user': request.user,
    }

    return render(request, 'gosen/base.html', context)
```

### 2. API Endpoint pour vérifier l'abonnement (pour AJAX)

```python
# Dans views/base.py ou views_abonnement.py
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET"])
def check_subscription_api(request):
    """API pour vérifier l'abonnement via JavaScript"""
    if not request.user.is_authenticated:
        return JsonResponse({'has_access': False, 'reason': 'not_authenticated'})

    from gosen.models_abonnement import Abonnement
    from django.utils import timezone

    abo = Abonnement.objects.filter(
        utilisateur=request.user,
        statut='ACTIF',
        date_fin__gt=timezone.now()
    ).first()

    has_access = abo is not None and abo.est_actif()

    return JsonResponse({
        'has_access': has_access,
        'reason': 'no_subscription' if not has_access else None
    })
```

### 3. Ajouter l'URL

```python
# Dans urls.py
from .views.base import check_subscription_api

urlpatterns = [
    # ...
    path('api/check-subscription/', check_subscription_api, name='check_subscription_api'),
]
```

## Sécurité

✅ **Ce qui est sécurisé (côté serveur)** :
- Le contenu n'est PAS envoyé au client si `has_subscription = False`
- Django évalue la condition AVANT d'envoyer le HTML
- Impossible de contourner en modifiant le CSS/JavaScript

❌ **Ce qui N'EST PAS sécurisé (à éviter)** :
- Cacher uniquement avec CSS (`display: none`)
- Cacher uniquement avec JavaScript
- Vérifier uniquement côté client

## Test

Pour tester sans abonnement :

```python
# Dans views/base.py, temporairement :
has_subscription = False  # Le contenu sera masqué
```

Pour tester avec abonnement :

```python
has_subscription = True  # Le contenu sera visible
```

## Models d'Abonnement Suggérés

```python
# models_abonnement.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Abonnement(models.Model):
    STATUT_CHOICES = [
        ('ACTIF', 'Actif'),
        ('EXPIRE', 'Expiré'),
        ('ANNULE', 'Annulé'),
    ]

    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES)
    date_debut = models.DateTimeField(auto_now_add=True)
    date_fin = models.DateTimeField()

    def est_actif(self):
        return self.statut == 'ACTIF' and self.date_fin > timezone.now()
```
