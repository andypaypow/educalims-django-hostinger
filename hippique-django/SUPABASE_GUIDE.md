# 📋 Guide Supabase - Informations Requises

Ce guide liste toutes les informations nécessaires pour permettre à Claude Code de gérer votre projet Supabase (Base de données, JWT, Edge Functions).

---

## 🔐 1. INFORMATIONS DE CONNEXION

### URL du projet Supabase
```
URL du projet: https://xxxxxxxxx.supabase.co
```
> Où la trouver: Dashboard → Settings → API

### Clés API
```
Project URL: https://xxxxxxxxx.supabase.co
anon/public key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
service_role key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```
> Où les trouver: Dashboard → Settings → API

### Accès Direct (Optionnel)
```
Database Password: (mot de passe de la base PostgreSQL)
Connection string: postgresql://postgres:[password]@db.xxxxxxx.supabase.co:5432/postgres
```

---

## 🗄️ 2. STRUCTURE DE LA BASE DE DONNÉES

### Schéma Actuel
Fournissez l'un des éléments suivants:

**Option A - Export du schéma:**
```bash
# Connectez-vous à votre projet et exportez
psql -h db.xxxxxxx.supabase.co -U postgres -c "\d" > schema.txt
```

**Option B - Liste des tables:**
```
- Table 1: nom_table_1
  Colonnes: id, nom, email, created_at, etc.
  Relations: avec table_2 (foreign key)

- Table 2: nom_table_2
  ...
```

**Option C - Capture d'écran:**
> Du Dashboard → Table Editor

### RLS (Row Level Security)
```
RLS activé sur: tables_ou_rls_est_actif
Policies actuelles:
- policy_name_1: description
- policy_name_2: description
```

---

## 🔑 3. AUTHENTIFICATION & JWT

### Configuration Auth
```
Email signup: activé/désactivé
Phone signup: activé/désactivé
Providers configurés: email, google, github, etc.
```

### JWT Secret
```
JWT Secret: (votre-jwt-secret)
```
> Où le trouver: Dashboard → Settings → API → jwt secret

### Configuration JWT (si personnalisée)
```json
{
  "exp": 3600,
  "token_duration": "1h",
  "refresh_token_rotation": true
}
```

### Custom Claims (si utilisés)
```
Custom claims ajoutés au JWT:
- role: user_role
- tenant_id: xxx
- etc.
```

---

## ⚡ 4. EDGE FUNCTIONS

### Fonctions Déployées
```
Liste des edge functions:
- function-name-1: description rapide
- function-name-2: description rapide
```

### Code des Edge Functions (optionnel)
```
Fichier: functions/function-name-1/index.ts
[Collez le code ici ou fournissez le chemin]

Fichier: functions/function-name-2/index.ts
[Collez le code ici ou fournissez le chemin]
```

### Variables d'Environment des Edge Functions
```
Variables globales:
- VAR_NAME_1: value
- VAR_NAME_2: value

Variables par fonction:
- function-name-1:
  - FUNCTION_VAR: value
```

---

## 🪝 5. WEBHOOKS - PAIEMENT & NOTIFICATIONS

### Configuration des Webhooks
```
URL du webhook: https://xxxxxxxxx.supabase.co/functions/v1/webhook-payment
Endpoint HTTP: POST
```

### Prestataire de Paiement
```
Nom: (PayPal, Stripe, CinetPay, etc.)
Clé API: pk_test_... / pk_live_...
Secret API: sk_test_... / sk_live_...
Webhook Secret: whsec_... (pour vérifier la signature)
```

### Événements Webhook (à configurer)
```
Liste des événements à écouter:
- payment.succeeded: Paiement réussi
- payment.failed: Paiement échoué
- payment.pending: Paiement en attente
- subscription.created: Abonnement créé
- subscription.cancelled: Abonnement annulé
- invoice.paid: Facture payée
```

### Structure du Payload Webhook
```json
{
  "event": "payment.succeeded",
  "timestamp": "2026-01-28T10:30:00Z",
  "data": {
    "payment_id": "pay_xxxxx",
    "amount": 5000,
    "currency": "XOF",
    "customer_id": "cust_xxxxx",
    "customer_email": "user@example.com",
    "customer_phone": "+225xxxxxxxx",
    "metadata": {
      "device_id": "unique-device-identifier",
      "plan": "monthly",
      "duration": "30d"
    }
  }
}
```

### Tables pour Webhooks (si utilisées)
```
Table: webhooks_logs
- id: UUID (PK)
- event_type: VARCHAR
- payload: JSONB
- processed: BOOLEAN
- created_at: TIMESTAMP

Table: payments
- id: UUID (PK)
- provider_payment_id: VARCHAR
- amount: DECIMAL
- currency: VARCHAR
- status: VARCHAR
- customer_email: VARCHAR
- customer_phone: VARCHAR
- device_id: VARCHAR
- metadata: JSONB
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

### Edge Function pour Webhook
```
Fichier: functions/webhook-payment/index.ts
Rôle: Recevoir et traiter les notifications du prestataire de paiement

Actions à effectuer:
1. Vérifier la signature du webhook
2. Parser le payload JSON
3. Valider les données
4. Enregistrer dans la base de données
5. Mettre à jour le statut de l'abonnement
6. Envoyer une notification Telegram (optionnel)
7. Retourner une réponse 200 OK
```

### Variables d'Environnement Webhook
```env
WEBHOOK_SECRET=whsec_xxxxx (signature pour vérification)
PAYMENT_API_KEY=sk_test_xxxxx
PAYMENT_API_SECRET=sk_live_xxxxx
TELEGRAM_BOT_TOKEN=8539115405:AAFxfimKuOeVKqYL5mQaclVsQ5Lh2hIcIok
TELEGRAM_CHAT_ID=1646298746
```

### Signature du Webhook (Vérification)
```
Méthode de signature: HMAC-SHA256
Header: X-Webhook-Signature ou X-Signature
Format: sha256=hash_du_payload_avec_secret

Code de vérification (TypeScript):
const cryptoProvider = new CryptoProvider();
const signature = cryptoProvider.computeHmacSignature(
  'sha256',
  payload,
  WEBHOOK_SECRET
);
```

### Tester le Webhook Localement
```bash
# Via ngrok ou tunnel similaire
ngrok http 8082

# Puis utiliser cette URL pour tester
URL: https://xxxxx.ngrok.io/functions/v1/webhook-payment
```

### Logs et Monitoring
```
Table: webhook_logs
- id: UUID
- event_type: VARCHAR
- source_ip: VARCHAR
- payload: JSONB
- response_status: INTEGER
- response_body: TEXT
- error_message: TEXT
- processed_at: TIMESTAMP
- created_at: TIMESTAMP
```

### Sécurité du Webhook
```
✅ Vérifier la signature HMAC
✅ Valider l'IP source (si disponible)
✅ Limiter aux méthodes POST
✅ Rate limiting
✅ Logs complets pour audit
✅ Retry automatique en cas d'échec
```

### Intégration avec Telegram
```typescript
// Notification Telegram après paiement réussi
async function notifyTelegram(payment: Payment) {
  const message = `
💰 *Nouveau Paiement Réussi*

*Montant:* ${payment.amount} ${payment.currency}
*Email:* ${payment.customer_email}
*Téléphone:* ${payment.customer_phone}
*Device ID:* ${payment.device_id}
*Date:* ${new Date().toLocaleString('fr-FR')}
  `;

  await fetch(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      chat_id: TELEGRAM_CHAT_ID,
      text: message,
      parse_mode: 'Markdown'
    })
  });
}
```

---

## 📤 6. EXPORT COMPLET (RECOMMANDÉ)

### Méthode 1 - Via Supabase CLI
```bash
# Installer Supabase CLI si pas déjà fait
npm install -g supabase

# Se connecter
supabase login

# Lier au projet
supabase link --project-ref xxxxxxxxx

# Exporter tout
supabase db dump -f dump.sql
supabase functions export
```

### Méthode 2 - Via psql
```bash
# Exporter le schéma complet
pg_dump -h db.xxxxxxx.supabase.co -U postgres --schema-only -f schema.sql

# Exporter les données
pg_dump -h db.xxxxxxx.supabase.co -U postgres --data-only -f data.sql
```

### Méthode 3 - Depuis le Dashboard
1. Database → Migrations → Copier les migrations
2. Database → API → Generate TypeScript types
3. Edge Functions → Télécharger le code de chaque fonction

---

## 📋 7. CHECKLIST DES INFORMATIONS À FOURNIR

Cochez les éléments que vous pouvez fournir:

- [ ] URL du projet Supabase
- [ ] Clé API publique (anon key)
- [ ] Clé service_role (à utiliser avec précaution)
- [ ] Mot de passe base de données OU connection string
- [ ] JWT Secret
- [ ] Liste des tables avec colonnes
- [ ] Schéma des relations (foreign keys)
- [ ] Configuration RLS et policies
- [ ] Liste des Edge Functions déployées
- [ ] Code des Edge Functions (ou dossier complet)
- [ ] Variables d'environnement
- [ ] Export SQL (si disponible)

### Webhooks (Paiement)
- [ ] Prestataire de paiement (Stripe, PayPal, CinetPay, etc.)
- [ ] Clés API du prestataire
- [ ] Webhook Secret (signature)
- [ ] URL du webhook Supabase Edge Function
- [ ] Liste des événements à écouter
- [ ] Structure du payload webhook
- [ ] Tables pour logs et paiements
- [ ] Configuration Telegram (optionnel)

---

## 🎯 8. CE QUE CLAUDE POURRA FAIRE

Une fois les informations fournies, Claude pourra:

### Base de Données
- ✅ Créer/modifier/supprimer des tables
- ✅ Ajouter/modifier des colonnes
- ✅ Créer des indexes
- ✅ Configurer les foreign keys
- ✅ Écrire et appliquer des migrations
- ✅ Configurer RLS et les policies
- ✅ Optimiser les requêtes

### JWT & Auth
- ✅ Configurer les providers d'authentification
- ✅ Personnaliser les JWT claims
- ✅ Créer des policies d'accès basées sur le JWT
- ✅ Intégrer avec des systèmes externes

### Edge Functions
- ✅ Créer de nouvelles fonctions
- ✅ Modifier le code existant
- ✅ Déployer les fonctions
- ✅ Déboguer et optimiser
- ✅ Configurer les variables d'environnement

### Webhooks & Paiements
- ✅ Créer l'Edge Function de webhook
- ✅ Implémenter la vérification de signature HMAC
- ✅ Parser et valider les payloads
- ✅ Enregistrer les logs de webhooks
- ✅ Mettre à jour les tables de paiements
- ✅ Gérer les abonnements
- ✅ Intégrer les notifications Telegram
- ✅ Configurer le retry en cas d'échec
- ✅ Sécuriser le webhook (rate limiting, IP filtering)

---

## 🔒 9. SÉCURITÉ - BONNES PRATIQUES

### ⚠️ JAMAIS committer dans Git
```
❌ JWT Secret
❌ Service Role Key
❌ Database Password
❌ Variables d'environnement sensibles
❌ Webhook Secret
❌ Clés API de paiement
```

### ✅ Utiliser des fichiers .env
```env
# .env.local (NE PAS COMMITTER)
SUPABASE_URL=https://xxxxxxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGci...
SUPABASE_SERVICE_KEY=eyJhbGci...
SUPABASE_JWT_SECRET=votre-jwt-secret

# Webhook & Paiement
WEBHOOK_SECRET=whsec_xxxxx
PAYMENT_API_KEY=pk_xxxxx
PAYMENT_API_SECRET=sk_xxxxx

# Telegram
TELEGRAM_BOT_TOKEN=8539115405:AAFxfimKuOeVKqYL5mQaclVsQ5Lh2hIcIok
TELEGRAM_CHAT_ID=1646298746
```

### ✅ Fichier .gitignore
```
.env
.env.local
.env.*.local
supabase/.env
*.webhook-secret
```

---

## 🚀 10. DÉMARRAGE RAPIDE

### Scénario 1 - Nouveau Projet
```
1. Créer le projet sur Supabase
2. Me fournir: URL + API Keys + JWT Secret
3. Je crée la structure de base
```

### Scénario 2 - Projet Existant
```
1. Fournir l'export complet (méthode section 6)
2. OU fournir les éléments checklist (section 7)
3. J'analyse la structure actuelle
4. Je peux ensuite aider pour les modifications
```

### Scénario 3 - Intégration Django + Webhook Paiement
```
1. Fournir: URL + Keys + Schéma DB
2. Je configure le projet Django
3. Je crée les modèles correspondants
4. Je configure l'auth JWT
5. Je crée l'Edge Function pour le webhook de paiement
6. J'intègre avec Telegram
```

### Scénario 4 - Webhook de Paiement Uniquement
```
1. Fournir: Prestataire + Clés API + Webhook Secret
2. Je crée l'Edge Function webhook-payment
3. J'implémente la vérification de signature
4. Je crée les tables (payments, webhook_logs)
5. J'intègre les notifications Telegram
```

---

## 📞 11. POUR COMMENCER

Copiez et complétez ce template avec vos informations:

```yaml
# === INFORMATIONS SUPABASE ===

# Connexion
supabase_url: "https://xxxxxxxxx.supabase.co"
supabase_anon_key: "eyJhbGci..."
supabase_service_role_key: "eyJhbGci..." # Optionnel, opérations admin uniquement
database_password: "votre-password" # Optionnel

# JWT
jwt_secret: "votre-jwt-secret"

# Structure
tables:
  - name: "table1"
    columns: ["col1", "col2", "col3"]
  - name: "table2"
    columns: ["col1", "col2"]

# Edge Functions
edge_functions:
  - name: "function1"
    description: "Description"
  - name: "function2"
    description: "Description"

# Webhook & Paiement
payment_provider: "Stripe|PayPal|CinetPay|Autre"
payment_api_key: "pk_xxxxx"
payment_api_secret: "sk_xxxxx"
webhook_secret: "whsec_xxxxx"
webhook_url: "https://xxxxxxxxx.supabase.co/functions/v1/webhook-payment"
webhook_events:
  - "payment.succeeded"
  - "payment.failed"
  - "subscription.created"

# Telegram (optionnel)
telegram_bot_token: "8539115405:AAFxfimKuOeVKqYL5mQaclVsQ5Lh2hIcIok"
telegram_chat_id: "1646298746"

# Export (optionnel)
schema_export: "chemin/vers/schema.sql"
data_export: "chemin/vers/data.sql"
functions_path: "chemin/vers/functions/"
```

---

## 📌 12. PROJET FILTREEXPERT - DÉPLOIEMENT

### 🎯 Contexte
Le projet **FiltreExpert Supabase** utilise les Edge Functions pour le filtrage de combinaisons hippiques.

### 📋 Informations du Projet
```
Projet: FiltreExpert
Dashboard: https://supabase.com/dashboard/project/qfkyzljqykymahlpmdnu
Project URL: https://qfkyzljqykymahlpmdnu.supabase.co
Project ID: qfkyzljqykymahlpmdnu
```

### 🔑 Clés API (FiltreExpert)
```
Anon Key (public):
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFma3l6bGpxeWt5bWFobHBtZG51Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk2Mjc1NzIsImV4cCI6MjA4NTIwMzU3Mn0.g_Rmxo8lY8KAnrQqyzcz0PLh03T1M7_RuBUQT6ObtXg

Service Role Key (admin):
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFma3l6bGpxeWt5bWFobHBtZG51Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2OTYyNzU3MiwiZXhwIjoyMDg1MjAzNTcyfQ.qwZ9S95QLHoROmwcQTqhP8std9eW2NJ4-_Lv8hzeUbo

JWT Secret:
ojdJ5aNShf27eP0g+XNMdKAWlGZRdW1BjJtSPajmpOp/od2aX2XRzdD02d6b7p5kak/pMUottx+QVaVNemmxJw==

Database Password:
RK8AY46O3WhOlwrA
```

### ⚡ Edge Functions à Déployer

#### 1. turboquinte-filter
**URL:** https://qfkyzljqykymahlpmdnu.supabase.co/functions/v1/turboquinte-filter
**Rôle:** Filtrage des combinaisons hippiques

**Code source:** `C:\Users\HP 360\Desktop\hippique-django\supabase\functions\turboquinte-filter\index.ts`

**Filtres implémentés:**
- Filtres de Groupes (Min/Max)
- Expert 1 (OR logic)
- Expert 2 (AND logic)
- Filtres de Poids (sources: default, manual, citation, position, results, expert)
- Filtres Statistiques (pair/impair, petit/grand, consécutifs)
- Filtres d'Alternance

#### 2. turboquinte-backtest
**URL:** https://qfkyzljqykymahlpmdnu.supabase.co/functions/v1/turboquinte-backtest
**Rôle:** Analyse d'arrivée par backtest

**Code source:** `C:\Users\HP 360\Desktop\hippique-django\supabase\functions\turboquinte-backtest\index.ts`

### 🚀 Instructions de Déploiement

#### Option A: Via le Dashboard Supabase (Recommandé)

1. **Accéder au Dashboard**
   - URL: https://supabase.com/dashboard/project/qfkyzljqykymahlpmdnu/functions

2. **Créer la fonction turboquinte-filter**
   - Cliquez sur "New Function"
   - Nom: `turboquinte-filter`
   - Copiez le code depuis: `C:\Users\HP 360\Desktop\hippique-django\DEPLOY_EDGE_FUNCTIONS.md`

3. **Créer la fonction turboquinte-backtest**
   - Cliquez sur "New Function"
   - Nom: `turboquinte-backtest`
   - Copiez le code depuis le fichier index.ts correspondant

4. **Vérifier le déploiement**
   ```bash
   curl https://qfkyzljqykymahlpmdnu.supabase.co/functions/v1/turboquinte-filter
   ```

#### Option B: Via la CLI Supabase (depuis Hostinger)

```bash
# Sur Hostinger
ssh -i ~/.ssh/id_ed25519 root@72.62.181.239

# Se connecter à Supabase (nécessite un Access Token)
~/.local/bin/supabase login

# Lier le projet
~/.local/bin/supabase link --project-ref qfkyzljqykymahlpmdnu

# Déployer les fonctions
~/.local/bin/supabase functions deploy turboquinte-filter
~/.local/bin/supabase functions deploy turboquinte-backtest
```

### 🌐 Frontend Déployé

**URL:** http://72.62.181.239:8090/
**Type:** HTML/CSS/JS statique
**Backend:** Supabase Edge Functions
**Port:** 8090

### 📊 Vérification du Déploiement

Une fois les Edge Functions déployées, testez avec:

```bash
# Test turboquinte-filter
curl -X POST "https://qfkyzljqykymahlpmdnu.supabase.co/functions/v1/turboquinte-filter" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFma3l6bGpxeWt5bWFobHBtZG51Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk2Mjc1NzIsImV4cCI6MjA4NTIwMzU3Mn0.g_Rmxo8lY8KAnrQqyzcz0PLh03T1M7_RuBUQT6ObtXg" \
  -d '{"config":{"numPartants":16,"tailleCombinaison":6},"groups":[],"standardFilters":[],"advancedFilters":[],"weightFilters":[],"evenOddFilters":[],"smallLargeFilters":[],"consecutiveFilters":[],"alternanceFilters":[]}'
```

### ✅ Checklist de Déploiement

- [ ] Se connecter au Dashboard Supabase
- [ ] Créer la fonction `turboquinte-filter`
- [ ] Copier le code complet depuis DEPLOY_EDGE_FUNCTIONS.md
- [ ] Créer la fonction `turboquinte-backtest`
- [ ] Copier le code depuis `supabase/functions/turboquinte-backtest/index.ts`
- [ ] Tester les deux fonctions avec curl
- [ ] Vérifier que http://72.62.181.239:8090/ fonctionne

### 📝 Fichiers de Référence

- **Guide de déploiement complet:** `C:\Users\HP 360\Desktop\hippique-django\DEPLOY_EDGE_FUNCTIONS.md`
- **Code turboquinte-filter:** `C:\Users\HP 360\Desktop\hippique-django\supabase\functions\turboquinte-filter\index.ts`
- **Code turboquinte-backtest:** `C:\Users\HP 360\Desktop\hippique-django\supabase\functions\turboquinte-backtest\index.ts`
- **Documentation:** `C:\Users\HP 360\Desktop\hippique-django\CLAUDE.md` (Étape 8)

---

**Dernière mise à jour** : 28 Janvier 2026
**Projet** : Guide de configuration Supabase pour Claude Code + FiltreExpert

---

## 🔗 LIENS UTILES

- **Supabase Dashboard** : https://app.supabase.com
- **Documentation** : https://supabase.com/docs
- **CLI Reference** : https://supabase.com/docs/reference/cli
- **Edge Functions** : https://supabase.com/docs/guides/functions
