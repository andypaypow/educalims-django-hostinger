# Filtre Expert + - Instructions Configuration Paiement

## URL CALLBACK A CONFIGURER CHEZ CYBERSCHOOL

Copiez cette URL et configurez-la dans votre dashboard Cyberschool comme URL de notification/webhook:

```
http://72.62.181.239:8000/hippie/webhook/cyberschool/
```

### Comment configurer chez Cyberschool:

1. Connectez-vous à votre dashboard Cyberschool: https://sumb.cyberschool.ga/
2. Allez dans la configuration de votre produit (ID: KzIfBGUYU6glnH3JlsbZ)
3. Cherchez le champ "URL de notification", "Webhook URL" ou "Callback URL"
4. Collez l'URL ci-dessus
5. Sauvegardez

---

## INFOS BOT TELEGRAM

- **Bot**: @Filtrexpert_bot
- **Token**: 8547430409:AAGx2LxGxP6fBd9mn13LSmRbU4y3wlopIq4
- **Webhook Telegram**: http://72.62.181.239:8000/hippie/telegram-webhook/

---

## FLUX DE PAIEMENT

1. **Utilisateur arrive sur** http://72.62.181.239:8000/hippie/turf-filter/
2. **Il configure ses filtres** et voit le message "Abonnement requis"
3. **Il clique sur "Payer maintenant"**
4. **Le système génère** un merchantReferenceId unique
5. **Il est redirigé vers Cyberschool** avec tous les paramètres:
   - productId=KzIfBGUYU6glnH3JlsbZ
   - operationAccountCode=ACC_6835C458B85FF
   - merchantReferenceId=XXXXX
   - maison=moov
   - amount=100
6. **Il paie sur Cyberschool**
7. **Cyberschool envoie un webhook** à votre URL de callback
8. **Le système active l'abonnement** (si code=200)
9. **Le frontend détecte** l'abonnement actif (polling toutes les 3s)
10. **Les résultats s'affichent !**

---

## PARAMETRES WEBHOOK CYBERSCHOOL

Cyberschool enverra un POST JSON à votre URL de callback avec ces paramètres:

```json
{
  "merchantReferenceId": "uuid-unique-ici",
  "code": 200,
  "status": "success",
  "amount": 100,
  "operator": "MOOV",
  "numero_tel": "+241XXXXXXX",
  "timestamp": "2026-01-25T10:30:00Z"
}
```

- **code=200**: Paiement réussi → On active l'abonnement
- **code!=200**: Paiement échoué → On logue l'erreur

---

## TESTER LE SYSTEME

### 1. Tester le webhook manuellement avec curl:

```bash
curl -X POST http://72.62.181.239:8000/hippie/webhook/cyberschool/ \
  -H "Content-Type: application/json" \
  -d '{
    "merchantReferenceId": "test-manuel-123",
    "code": 200,
    "status": "success",
    "amount": 100,
    "operator": "MOOV",
    "numero_tel": "+2411234567"
  }'
```

Réponse attendue: `{"status": "ok"}`

### 2. Vérifier les logs dans Django Admin:

- Allez sur: http://72.62.181.239:8000/admin/
- Section "HIPPIE" → "Journaux Webhooks"
- Vous verrez tous les webhooks reçus

### 3. Tester le flux complet:

1. Ouvrez http://72.62.181.239:8000/hippie/turf-filter/
2. Faites vos filtres
3. Cliquez sur "Payer maintenant"
4. Sur la page Cyberschool, simulez un paiement réussi
5. Revenez sur la page Filtre Expert +
6. Attendez quelques secondes (polling toutes les 3s)
7. Les résultats devraient apparaître !

---

## STRUCTURE DES DONNEES

### SessionUser
- session_id: Identifiant unique (localStorage ou Telegram)
- telegram_user_id: ID Telegram utilisateur (optionnel)
- phone_number: Numéro de téléphone (optionnel)

### ProduitAbonnement
- produit_id: "KzIfBGUYU6glnH3JlsbZ" (ID Cyberschool)
- nom: "Filtre Expert + - Accès Journalier"
- prix: 100 FCFA
- duree_jours: 1

### Abonnement
- session_user: L'utilisateur
- produit: Le produit acheté
- merchant_reference_id: Référence unique pour tracker
- statut: EN_ATTENTE → ACTIF → EXPIRE
- date_fin: 23h59 le jour du paiement

---

## COMMANDES RAPIDES

```bash
# Créer le produit d'abonnement
python create_produit_abonnement.py

# Vérifier le webhook Telegram
python setup_telegram_webhook.py info

# Lancer le serveur Django
python manage.py runserver 8000
```

---

## URLS IMPORTANTES

- **Page Filtre Expert**: http://72.62.181.239:8000/hippie/turf-filter/
- **Admin Django**: http://72.62.181.239:8000/admin/
- **Webhook Cyberschool**: http://72.62.181.239:8000/hippie/webhook/cyberschool/
- **Webhook Telegram**: http://72.62.181.239:8000/hippie/telegram-webhook/

---

## SUPPORT

En cas de problème:
1. Vérifiez les logs Webhook dans l'admin Django
2. Testez le webhook avec curl
3. Vérifiez que l'URL de callback est bien configurée chez Cyberschool
4. Contactez le support technique
