# Reset Gosen DEV (8082) - Version Simplifiée

```bash
ssh -i ~/.ssh/id_ed25519 root@72.62.181.239

# 0. Identifier et choisir le commit
cd /root/gosen-filter-dev && git log --oneline -10  # Liste les 10 derniers commits
# Notez le commit (ex: e4ffbc1)

# 1. Arrêter DEV
docker compose -f docker-compose.dev.yml down

# 2. Copier depuis PROD vers DEV
rsync -av --delete --exclude '*.pyc' --exclude '__pycache__' --exclude '.git' --exclude 'postgres_data' --exclude 'staticfiles' /root/gosen-prod/ /root/gosen-filter-dev/

# 3. Démarrer DEV
docker compose -f docker-compose.dev.yml up -d

# 4. Vérifier
curl -s http://localhost:8082/ | grep -E '(config-card|pronostics-card)'
```
