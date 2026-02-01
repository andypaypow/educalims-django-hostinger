# Gosen TurfFilter - Système de Paiement

## 🎯 Vue d'ensemble

**Application** : Gosen TurfFilter - Application de filtrage de combinaisons hippiques
**VPS** : Hostinger (72.62.181.239)
**Port** : 8082 (DEV) / 8083 (PROD)
**Tech** : Django + PostgreSQL + Gunicorn + Whitenoise

---

## ⚠️ IMPORTANT : Problème Webhook Cyberschool

### Problème actuel
Les produits Cyberschool partagent les mêmes `productId` qu'Educalims (port 8081), donc :
- **Le webhook pointe vers le port 8081** (Educalims)
- **Les notifications vont vers @educalims_bot** au lieu de @Filtrexpert_bot

### Solution à implémenter
1. Connectez-vous à https://sumb.cyberschool.ga/
2. Créez 2 nouveaux produits avec webhook `http://72.62.181.239:8082/webhook-cyberschool/`
3. Mettez à jour les URLs dans Django

---

## 📱 Accès Telegram

### ✅ Bot Gosen TurfFilter
- **Bot** : @Filtrexpert_bot
- **Token** : `8547430409:AAGx2LxGxP6fBd9mn13LSmRbU4y3wlopIq4`
- **Chat ID** : `1646298746`

### ❌ Bot Educalims (à NE PAS utiliser)
- **Bot** : @educalims_bot
- **Token** : `8539115405:...` (port 8081)

---

## 🔧 Configuration Django

### settings.py
```python
# Telegram Bot - GOSEN TURFFILTER
TELEGRAM_BOT_TOKEN = '8547430409:AAGx2LxGxP6fBd9mn13LSmRbU4y3wlopIq4'
TELEGRAM_CHAT_ID = '1646298746'

# Cyberschool
CYBERSCHOOL_WEBHOOK = 'http://72.62.181.239:8082/webhook-cyberschool/'
```

---

## 🎯 Logique du Système

### Interface complète
- Page http://72.62.181.239:8082/ affiche TOUT le contenu
- PAS de classe `content-locked`
- Toute l'interface est visible

### Device Fingerprinting
```python
fingerprint = f"{user_agent}|{accept_language}|{accept_encoding}"
device_id = hashlib.sha256(fingerprint.encode()).hexdigest()
```

### Utilisateurs Anonymes
- Pas d'authentification traditionnelle
- Middleware crée automatiquement un utilisateur Django
- Username : `device_{device_id[:16]}`

### Flux de paiement
```
1. Clic "S'abonner (100F/jour)"
2. Redirection → Cyberschool
3. Paiement réussi (code "200")
4. Webhook : http://72.62.181.239:8082/webhook-cyberschool/
5. Création abonnement + notification @Filtrexpert_bot
6. Expire à 23h59 le jour du paiement
```

---

## 🗄️ Base de Données

### Tables principales
- `gosen_produit` : Produits d'abonnement
- `gosen_abonnement` : Abonnements utilisateurs
- `gosen_gosenuserprofile` : Profils avec device_id
- `gosen_webhooklog` : Journal webhooks

### Models
```python
class Produit:
    nom, prix, moov_money_url, airtel_money_url, est_actif

class Abonnement:
    user, niveau, produit, statut, reference_interne
    merchant_reference_id, code_paiement, methode_paiement
    montant_paye, date_debut, date_fin

class GosenUserProfile:
    user, device_id, fingerprint_data, telephone
```

---

## 📋 Commandes Utiles

### SSH
```bash
ssh -i ~/.ssh/id_ed25519 root@72.62.181.239
```

### Docker
```bash
docker ps | grep gosen
docker logs gosen-dev-web -f
docker restart gosen-dev-web
docker exec -it gosen-dev-web python manage.py shell
```

### Vérifier abonnements
```python
from gosen.models import Abonnement
Abonnement.objects.filter(statut='ACTIF').count()
```

### Mettre à jour Produit
```python
from gosen.models import Produit
p = Produit.objects.get(id=2)
p.moov_money_url = 'https://sumb.cyberschool.ga/?productId=NEW_ID&operationAccountCode=NEW_CODE&maison=moov&amount=100'
p.save()
```

---

## 🚨 Dépannage

### Notifications sur mauvais bot
→ Créer nouveaux produits Cyberschool (voir section "IMPORTANT")

### Interface "tout noir"
→ Vérifier que body n'a PAS `class="content-locked"`

### Webhook non appelé
→ Vérifier configuration dans dashboard Cyberschool

---

## 📝 Documentation complète

Voir : `FILTREEXPERT_PAIEMENT.md`

---

**Dernière mise à jour** : 30 Janvier 2026
