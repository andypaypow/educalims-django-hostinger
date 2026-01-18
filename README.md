# Educalims - Plateforme Educative

## 📚 Documentation

- **[DEV_LOG.md](./DEV_LOG.md)** - Journal de développement complet (modifs, problèmes, solutions)
- **[DEPLOIEMENT_HOSTINGER.md](./DEPLOIEMENT_HOSTINGER.md)** - Guide de déploiement

---

## 🚀 Architecture Hostinger

Hostinger VPS (72.62.181.239)
│
├── /root/educalims-dev/          ← ESPACE DE DÉVELOPPEMENT
│   ├── Port 8081 (HTTP)
│   ├── Port 8001 (Direct Gunicorn)
│   ├── Base de données: educalims_dev
│   └── DEBUG=True
│
└── /root/educalims-prod/         ← ESPACE DE PRODUCTION
    ├── Port 80 (HTTP)
    ├── Port 8000 (Direct Gunicorn)
    ├── Base de données: educalims_prod
    └── DEBUG=False

---

## 🔗 Accès

### Environnement de Dev
- URL: http://72.62.181.239:8081/
- Admin: http://72.62.181.239:8081/admin/

### Environnement de Prod
- URL: http://72.62.181.239/
- Admin: http://72.62.181.239/admin/

### SSH
ssh -i ~/.ssh/id_ed25519 root@72.62.181.239

---

## 🔄 Workflow Rapide

1. Se connecter au serveur
   ssh -i ~/.ssh/id_ed25519 root@72.62.181.239
   cd /root/educalims-dev

2. Modifier les fichiers
   nano educalims/views.py

3. Appliquer les migrations (si modification des modèles)
   docker compose -f docker-compose.dev.yml exec web python manage.py makemigrations
   docker compose -f docker-compose.dev.yml exec web python manage.py migrate

4. Redémarrer le conteneur
   docker compose -f docker-compose.dev.yml restart web

5. Tester sur http://72.62.181.239:8081/

6. Déployer en prod
   ./deploy-to-prod.sh

---

## 📝 Derniers Changements (18 Janvier 2026)

### ✅ Admin - Champ "Recommandé par" visible
- Le champ recommande_par est maintenant affiché dans la page User de l'admin
- Affiche également le téléphone de l'utilisateur

### ✅ Notifications Telegram améliorées
- Ajout de "Recommandé par" dans toutes les notifications
- Fonctions modifiées: notifier_nouveau_abonnement_telegram(), notifier_paiement_telegram(), webhook

### ✅ Modèle Produit: duree_jours → date_expiration
- Champ remplacé par date_expiration
- Valeur par défaut: 31 août de l'année en cours
- Migration 0006 appliquée

**Pour plus de détails sur les problèmes rencontrés et solutions, voir DEV_LOG.md**

---

## 🛠️ Commandes Utiles

# Voir les logs
docker compose -f docker-compose.dev.yml logs -f web

# Ouvrir un shell Django
docker compose -f docker-compose.dev.yml exec web python manage.py shell

# Créer un superutilisateur
docker compose -f docker-compose.dev.yml exec web python manage.py createsuperuser

# Sauvegarder la base
docker compose -f docker-compose.dev.yml exec db pg_dump -U educalims educalims_dev > backup.sql

---

## ⚠️ Règles d'Or

1. TOUJOURS tester en dev avant de déployer en prod
2. TOUJOURS faire les migrations après modification des modèles
3. NE JAMAIS modifier directement en prod
4. TOUJOURS vérifier les logs après modification

---

**Tout le développement se fait sur Hostinger VPS directement.**

Pour plus d'informations, consulter DEV_LOG.md
