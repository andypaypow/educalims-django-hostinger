# Guide de déploiement Educalims sur Hostinger

## État actuel du déploiement

### ✅ Composants déployés et fonctionnels

- **Django 6.0.1** : Application déployée
- **Gunicorn** : Serveur WSGI actif (3 workers)
- **Nginx** : Serveur web configuré
- **SQLite** : Base de données configurée
- **Services systemd** :
  - `educalims.service` : Application Django
  - `educalims-tunnel.service` : Tunnel public temporaire
  - `nginx.service` : Serveur web

### 🔐 Identifiants Admin

- **URL Admin** : https://educalims-hostinger.loca.lt/admin/
- **Username** : `admin`
- **Password** : `Admin1234!`
- **IMPORTANT** : Changez ce mot de passe après la première connexion !

### 🌡️ URLs d'accès

| URL | Statut | Description |
|-----|--------|-------------|
| http://72.62.181.239/ | ⚠️ Bloqué | Pare-feu Hostinger bloque le port 80 |
| https://educalims-hostinger.loca.lt/ | ✅ Actif | Tunnel temporaire (solution de contournement) |

---

## 🚨 ACTION REQUISE : Ouvrir le port 80

Le site est déployé mais **inaccessible** car le pare-feu Hostinger bloque le port 80.

### Étapes pour ouvrir le port 80 :

1. Connectez-vous au **panneau Hostinger** : https://hpanel.hostinger.com
2. Allez dans **VPS** → Sélectionnez votre serveur (72.62.181.239)
3. Cherchez **Network** ou **Firewall** ou **Pare-feu**
4. Cliquez sur **Add Rule** ou **Ajouter une règle** :

   ```
   Protocol: TCP
   Port: 80
   Source: Anywhere (0.0.0.0/0)
   Action: Accept
   ```

5. Répétez pour le **port 443** si vous voulez HTTPS

6. Sauvegardez les changements

Après configuration, le site sera accessible sur : **http://72.62.181.239/**

---

## 📡 Configuration du Webhook Cyberschool

### URL du webhook

Utilisez cette URL chez Cyberschool pour recevoir les notifications de paiement :

**Pour le tunnel (temporaire)** :
```
https://educalims-hostinger.loca.lt/webhook-cyberschool-simple/
```

**Pour l'accès direct (après ouverture du port 80)** :
```
http://72.62.181.239/webhook-cyberschool-simple/
```

### Test du webhook

```bash
curl -X POST https://educalims-hostinger.loca.lt/webhook-cyberschool-simple/ \
  -H "Content-Type: application/json" \
  -d '{"merchant_reference_id": "TEST123", "status": "SUCCESS", "code": 200}'
```

---

## 🔧 Commandes utiles

### Connexion SSH

```bash
ssh root@72.62.181.239
```

### Gérer les services

```bash
# Vérifier l'état
systemctl status educalims nginx educalims-tunnel

# Redémarrer les services
systemctl restart educalims nginx

# Voir les logs
journalctl -u educalims -f
tail -f /var/log/nginx/access.log
```

### Mettre à jour l'application

```bash
ssh root@72.62.181.239
cd /root/educalims_project
source venv/bin/activate
git pull  # si vous utilisez git
python manage.py migrate
python manage.py collectstatic --noinput
systemctl restart educalims
```

---

## 🔒 Sécurité - À faire après l'ouverture du port 80

### 1. Changer le mot de passe admin

```bash
ssh root@72.62.181.239
cd /root/educalims_project
source venv/bin/activate
python manage.py changepassword admin
```

### 2. Installer SSL (Let's Encrypt)

```bash
ssh root@72.62.181.239
apt-get install certbot python3-certbot-nginx
certbot --nginx -d votre-domaine.com
```

### 3. Mettre à jour ALLOWED_HOSTS

Une fois que vous avez un domaine, mettez à jour `ALLOWED_HOSTS` dans les settings :

```python
ALLOWED_HOSTS = ['votre-domaine.com', 'www.votre-domaine.com']
```

---

## 📊 Statut du système

### Services actifs

```
● educalims.service     - Application Django (Gunicorn)
● educalims-tunnel.service - Tunnel public (Localtunnel)
● nginx.service         - Serveur web
```

### Ports

- **80** (HTTP) : Nginx → Gunicorn → Django (bloqué par pare-feu Hostinger)
- **443** (HTTPS) : À configurer
- **22** (SSH) : Actif

---

## 🎯 Prochaines étapes

1. **IMMÉDIAT** : Ouvrir le port 80 dans le pare-feu Hostinger
2. Tester l'accès sur http://72.62.181.239/
3. Changer le mot de passe admin
4. Mettre à jour l'URL du webhook chez Cyberschool
5. Installer SSL (Let's Encrypt) pour HTTPS
6. Ajouter un domaine personnalisé (optionnel)

---

## 📝 Contact et support

Pour toute question sur le déploiement, consultez les logs :

```bash
ssh root@72.62.181.239
journalctl -u educalims -n 50
```

---

**Déployé le** : 15 janvier 2026
**Serveur** : Hostinger VPS (72.62.181.239)
**Framework** : Django 6.0.1 + Python 3.12
