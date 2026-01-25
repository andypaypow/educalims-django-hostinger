# Filtre Expert + - Système de Paiement Complet

## Résumé du système

J'ai **intelligemment transposé** le système educalims qui fonctionne vers Filtre Expert +, en adaptant uniquement les configurations Telegram et les URLs.

## Ce qui a été fait

### 1. Modèles de données (hippie/models.py)
- **UserProfile** : Profil utilisateur avec `device_id` pour la sécurité
- **SessionUser** : Utilisateur par session (conservé pour compatibilité)
- **ProduitAbonnement** : Produit avec config Cyberschool
- **Abonnement** : Abonnement utilisateur avec gestion des états
- **WebhookLog** : Journal des webhooks reçus

### 2. Middleware (hippie/middleware.py)
- **DeviceIdMiddleware** : Gère l'identifiant unique de l'appareil
- **JWT tokens** : Crée et vérifie les tokens JWT pour la sécurité
- **device_required** : Décorateur pour protéger les vues

### 3. Authentification (hippie/forms.py, hippie/views.py)
- **CustomUserCreationForm** : Formulaire d'inscription
- **LoginForm** : Formulaire de connexion
- **custom_login/register/logout/profile** : Vues d'authentification complètes

### 4. Templates
- **hippie/auth/login.html** : Page de connexion/inscription moderne
- **hippie/auth/profile.html** : Page de profil utilisateur
- **hippie/device_not_authorized.html** : Erreur appareil non autorisé

### 5. Webhook Cyberschool amélioré
- Gestion des prolongations d'abonnement
- Notifications Telegram détaillées
- Logs complets des webhooks
- Gestion robuste des erreurs

### 6. Bot Telegram @Filtrexpert_bot
- Token: `8547430409:AAGx2LxGxP6fBd9mn13LSmRbU4y3wlopIq4`
- Commandes: /start, /compteur, /help
- Notifications de paiement en temps réel

## URLs importantes

### Configuration Cyberschool

**URL de Callback à configurer chez Cyberschool:**
```
http://72.62.181.239:8000/hippie/webhook/cyberschool/
```

**Lien du produit Cyberschool:**
```
https://sumb.cyberschool.ga/?productId=KzIfBGUYU6glnH3JlsbZ&operationAccountCode=ACC_6835C458B85FF&maison=moov&amount=100
```

### URLs de l'application

- **Page principale**: http://72.62.181.239:8000/hippie/turf-filter/
- **Login**: http://72.62.181.239:8000/hippie/login/
- **Register**: http://72.62.181.239:8000/hippie/register/
- **Profile**: http://72.62.181.239:8000/hippie/profile/
- **Admin**: http://72.62.181.239:8000/admin/
- **Webhook Telegram**: http://72.62.181.239:8000/hippie/telegram-webhook/

## Comment ça marche

### Système avec authentification Django (recommandé)

1. **L'utilisateur s'inscrit** sur `/hippie/register/`
2. **Il se connecte** sur `/hippie/login/`
3. **Le device_id est enregistré** dans UserProfile
4. **Un cookie JWT est créé** pour sécuriser la session
5. **Il configure ses filtres** sur `/hippie/turf-filter/`
6. **Il clique sur "Payer maintenant"**
7. **Il est redirigé vers Cyberschool**
8. **Après paiement**, Cyberschool envoie un webhook
9. **L'abonnement est activé automatiquement**
10. **Les résultats s'affichent !**

### Système sans authentification (compatible)

1. **L'utilisateur arrive** sur `/hippie/turf-filter/`
2. **Un session_id est généré** (localStorage)
3. **Il configure ses filtres**
4. **Il paie via Cyberschool**
5. **Le webhook active l'abonnement**
6. **Les résultats s'affichent !**

## Prochaines étapes

### 1. Redémarrer le serveur

```bash
cd C:\Users\HP 360\Desktop\hippique-django
python manage.py runserver 8000
```

### 2. Tester l'authentification

1. Allez sur http://72.62.181.239:8000/hippie/register/
2. Créez un compte
3. Connectez-vous
4. Vérifiez que le device_id est enregistré

### 3. Configurer le webhook Cyberschool

Copiez cette URL dans votre dashboard Cyberschool:
```
http://72.62.181.239:8000/hippie/webhook/cyberschool/
```

### 4. Tester le bot Telegram

Envoyez `/start` à @Filtrexpert_bot

### 5. Tester le paiement complet

1. Allez sur http://72.62.181.239:8000/hippie/turf-filter/
2. Configurez vos filtres
3. Cliquez sur "Payer maintenant"
4. Effectuez le paiement sur Cyberschool
5. Vérifiez que l'abonnement s'active
6. Les résultats devraient apparaître !

## Dépannage

### Erreur CSRF 403
- J'ai déjà corrigé les ports dans `CSRF_TRUSTED_ORIGINS`
- Redémarrez le serveur pour prendre en compte les changements

### Le webhook ne fonctionne pas
- Vérifiez l'URL configurée chez Cyberschool
- Testez avec curl:
```bash
curl -X POST http://72.62.181.239:8000/hippie/webhook/cyberschool/ \
  -H "Content-Type: application/json" \
  -d '{"merchantReferenceId":"test123","code":200,"status":"success","amount":100,"operator":"MOOV","numero_tel":"+2411234567"}'
```

### Le bot ne répond pas
- Vérifiez que le webhook Telegram est configuré
- Utilisez `python setup_telegram_webhook.py info`

## Fichiers créés/modifiés

### Créés:
- `hippie/middleware.py` - DeviceIdMiddleware
- `hippie/forms.py` - Formulaires d'authentification
- `hippie/templates/hippie/auth/login.html` - Page de connexion
- `hippie/templates/hippie/auth/profile.html` - Page de profil
- `hippie/templates/hippie/device_not_authorized.html` - Erreur device
- `create_produit_abonnement.py` - Script de création produit
- `setup_telegram_webhook.py` - Script webhook Telegram
- `INSTRUCTIONS_PAIEMENT.md` - Instructions paiement
- `SYSTEME_FILTRE_EXPERT.md` - Ce fichier

### Modifiés:
- `hippie/models.py` - Ajouté UserProfile
- `hippie/views.py` - Ajouté vues auth + webhook amélioré
- `hippie/urls.py` - Ajouté routes auth
- `hippie_project/settings.py` - Ajouté DeviceIdMiddleware + CSRF trusted origins
- `hippie/admin.py` - Déjà configuré pour les nouveaux modèles

## Migration

La migration `0004_add_user_profile.py` a été créée et appliquée automatiquement.

## Support

En cas de problème:
1. Vérifiez les logs Django
2. Vérifiez les logs dans `/admin/hippie/webhooklog/`
3. Vérifiez les abonnements dans `/admin/hippie/abonnement/`
4. Contactez le support technique

---

**Système transposé intelligemment depuis educalims ✅**
