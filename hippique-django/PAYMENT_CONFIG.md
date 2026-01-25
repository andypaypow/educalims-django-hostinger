# 🏇 Filtre Expert + - Configuration du Système de Paiement

## 🔗 URLs Importantes (à configurer chez Cyberschool)

### Webhook Callback URL (URL de notification)
```
http://72.62.181.239:8000/hippie/webhook/cyberschool/
```
⚠️ **IMPORTANT**: Cette URL doit être configurée dans votre dashboard Cyberschool comme URL de notification (webhook/callback).

Si Cyberschool exige HTTPS, utilisez ngrok ou configurez SSL sur votre serveur.

### URLs de l'application
- **Page principale**: http://72.62.181.239:8000/hippie/turf-filter/
- **Webhook Telegram**: http://72.62.181.239:8000/hippie/telegram-webhook/

## 🤖 Bot Telegram

- **Nom du bot**: @Filtrexpert_bot
- **Token**: `8547430409:AAGx2LxGxP6fBd9mn13LSmRbU4y3wlopIq4`

### Commandes disponibles
- `/start` - Initialiser et vérifier l'abonnement
- `/compteur` - Voir le temps restant
- `/help` - Aide

## 💰 Configuration du Produit Cyberschool

### Informations du produit
- **Nom**: Filtre Expert + - Accès Journalier
- **Prix**: 100 FCFA
- **Durée**: 1 jour (jusqu'à 23h59)
- **ID Produit**: `FILTRE_EXPERT_JOURNALIER`

### Configuration requise chez Cyberschool

Dans votre dashboard Cyberschool, pour ce produit:

1. **URL de notification (Webhook)**: `http://72.62.181.239:8000/hippie/webhook/cyberschool/`
2. **Méthode**: POST
3. **Paramètres attendus dans le webhook**:
   - `merchantReferenceId` - Référence unique du paiement
   - `code` - Code de réponse (200 = succès)
   - `status` - Statut du paiement
   - `amount` - Montant payé
   - `operator` - Opérateur de paiement
   - `numero_tel` ou `customerID` - Numéro de téléphone

## 🚀 Instructions de Configuration

### Étape 1: Créer le Produit d'Abonnement

```bash
cd C:\Users\HP 360\Desktop\hippique-django
python create_produit_abonnement.py
```

### Étape 2: Configurer le webhook Telegram (si nécessaire)

Le bot est déjà configuré pour educalims. Vérifiez qu'il fonctionne:

```bash
python setup_telegram_webhook.py info
```

### Étape 3: Configurer Cyberschool

1. Connectez-vous à votre dashboard Cyberschool
2. Créez un nouveau produit ou modifiez l'existant
3. Configurez l'URL de webhook:
   - **URL**: `http://72.62.181.239:8000/hippie/webhook/cyberschool/`
   - **Méthode**: POST
   - **Content-Type**: application/json

### Étape 4: Tester le flux

1. Allez sur http://72.62.181.239:8000/hippie/turf-filter/
2. Configurez vos filtres
3. Cliquez sur "Payer maintenant"
4. Effectuez le paiement sur Cyberschool
5. Le webhook devrait activer automatiquement l'abonnement
6. Les résultats apparaîtront !

## 📊 Structure du système

### Modèles de données
- **SessionUser**: Utilisateur identifié par session (localStorage ou Telegram)
- **ProduitAbonnement**: Produit d'abonnement avec prix et durée
- **Abonnement**: Abonnement utilisateur avec statut (EN_ATTENTE, ACTIF, EXPIRE)
- **WebhookLog**: Journal des webhooks reçus

### Flux de paiement
1. Utilisateur clique sur "Payer" → `api_creer_paiement()` génère un merchantReferenceId
2. Redirection vers Cyberschool avec la référence
3. Paiement effectué sur Cyberschool
4. Cyberschool envoie un webhook → `webhook_cyberschool()`
5. Si code=200, l'abonnement est activé
6. Le frontend vérifie toutes les 3s → `api_verifier_abonnement()`
7. Quand abonnement actif, les résultats sont affichés

## 🔧 Dépannage

### Le bot ne répond pas
Vérifiez le webhook:
```bash
python setup_telegram_webhook.py info
```

### Les webhook Cyberschool ne sont pas reçus
1. Vérifiez l'URL configurée chez Cyberschool
2. Vérifiez les logs dans le admin Django: `/admin/hippie/webhooklog/`
3. Testez manuellement avec curl:
```bash
curl -X POST http://72.62.181.239:8000/hippie/webhook/cyberschool/ \
  -H "Content-Type: application/json" \
  -d '{"merchantReferenceId":"test123","code":200,"status":"success","amount":100,"operator":"TMONEY","numero_tel":"+2411234567"}'
```

### L'abonnement ne s'active pas
1. Vérifiez dans le admin: `/admin/hippie/abonnement/`
2. Vérifiez les logs webhook: `/admin/hippie/webhooklog/`
3. Le code doit être 200 pour l'activation

## 📞 Support

Pour toute question, contactez l'administrateur ou vérifiez les logs Django.
