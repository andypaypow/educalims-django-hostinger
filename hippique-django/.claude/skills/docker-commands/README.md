# Docker Commands - Gosen Filter

## Connexion SSH

```bash
ssh -i ~/.ssh/id_ed25519 root@72.62.181.239
```

---

## Voir l'état des conteneurs

```bash
# Tous les conteneurs Gosen
docker ps | grep gosen

# Formaté
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep gosen
```

---

## Voir les logs

```bash
# Logs en temps réel
docker logs gosen-dev-web -f

# 100 dernières lignes
docker logs gosen-dev-web --tail 100

# Logs de la base de données
docker logs gosen-dev-db
```

---

## Redémarrer un conteneur

```bash
# Port 8082 (DEV)
docker restart gosen-dev-web

# Port 8083 (PROD)
docker restart gosen-prod-web

# Base de données
docker restart gosen-dev-db
```

---

## Arrêter/Démarrer

```bash
cd /root/gosen-filter-dev

# Arrêter
docker compose -f docker-compose.dev.yml down

# Démarrer
docker compose -f docker-compose.dev.yml up -d

# Reconstruction + démarrage
docker compose -f docker-compose.dev.yml up -d --build
```

---

## Entrer dans un conteneur

```bash
# Shell bash
docker exec -it gosen-dev-web bash

# Shell Django
docker exec -it gosen-dev-web python manage.py shell

# Base de données
docker exec -it gosen-dev-db psql -U gosen -d gosen_dev
```

---

## Migrations Django

```bash
# Créer des migrations
docker exec gosen-dev-web python manage.py makemigrations

# Appliquer les migrations
docker exec gosen-dev-web python manage.py migrate

# Vérifier les migrations
docker exec gosen-dev-web python manage.py showmigrations
```

---

## Nettoyer

```bash
# Supprimer les conteneurs arrêtés
docker container prune

# Supprimer les images non utilisées
docker image prune -a

# Voir l'espace disque
docker system df
```

---

## Vérifier l'application

```bash
# Test HTTP
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:8082/

# Vérifier le body tag
curl -s http://localhost:8082/ | grep '<body>' | head -1

# Compter les lignes
curl -s http://localhost:8082/ | wc -l
```

---

## Dépannage

### Conteneur ne démarre pas

```bash
# Voir les logs d'erreur
docker logs gosen-dev-web

# Vérifier les ports
netstat -tlnp | grep 8082
```

### Base de données inaccessible

```bash
# Redémarrer la base de données
docker restart gosen-dev-db

# Attendre 5 secondes
sleep 5

# Vérifier
docker exec gosen-dev-db psql -U gosen -c "SELECT 1;"
```

### Problème de volume

```bash
# Supprimer les volumes et recréer
docker compose -f docker-compose.dev.yml down -v
docker compose -f docker-compose.dev.yml up -d
```

---

**Projet** : Gosen TurfFilter
**VPS** : Hostinger (72.62.181.239)
