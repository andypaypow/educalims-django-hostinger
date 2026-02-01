# Django Migrations - Gosen Filter

## Vue d'ensemble

Les migrations Django permettent de gérer les changements de schéma de base de données de manière versionnée.

---

## Processus de migration

### 1. Créer les migrations

```bash
# Se connecter au serveur
ssh -i ~/.ssh/id_ed25519 root@72.62.181.239

# Entrer dans le conteneur
docker exec -it gosen-dev-web bash

# Créer les migrations
python manage.py makemigrations

# Pour une application spécifique
python manage.py makemigrations gosen
```

### 2. Vérifier les migrations

```bash
# Voir toutes les migrations
python manage.py showmigrations

# Voir les migrations d'une app
python manage.py showmigrations gosen

# Voir le SQL qui sera exécuté
python manage.py sqlmigrate gosen 0001
```

### 3. Appliquer les migrations

```bash
# Appliquer toutes les migrations
python manage.py migrate

# Appliquer une migration spécifique
python manage.py migrate gosen 0001

# Appliquer en mode simulation (dry run)
python manage.py migrate --plan
```

### 4. Redémarrer le conteneur

```bash
# Sortir du conteneur
exit

# Redémarrer
docker restart gosen-dev-web
```

---

## Scénarios courants

### Ajouter un champ à un modèle

```python
# 1. Modifier le modèle (gosen/models.py)
class Produit(Model):
    nouveau_champ = CharField(max_length=100, blank=True)

# 2. Créer la migration
python manage.py makemigrations

# 3. Vérifier
python manage.py showmigrations gosen

# 4. Appliquer
python manage.py migrate

# 5. Redémarrer
docker restart gosen-dev-web
```

### Créer un nouveau modèle

```python
# 1. Ajouter le modèle dans models.py
class NouveauModele(Model):
    nom = CharField(max_length=100)

# 2. Créer la migration
python manage.py makemigrations

# 3. Appliquer
python manage.py migrate
```

### Annuler une migration

```bash
# Annuler la dernière migration
python manage.py migrate gosen zero

# Ou annuler une migration spécifique
python manage.py migrate gosen 0002_previous
```

### Résoudre les conflits

```bash
# En cas de conflit de fusion
python manage.py makemigrations --merge

# Voir les dépendances
python manage.py showmigrations --plan
```

---

## Dépannage

### Erreur "No migrations to apply"

```bash
# Vérifier les migrations appliquées
python manage.py showmigrations

# Faux-migration (marquer comme appliqué)
python manage.py migrate --fake gosen zero
python manage.py migrate gosen
```

### Erreur "Relation already exists"

```bash
# Créer une migration vide
python manage.py makemigrations --empty gosen

# Éditer la migration pour ajouter RunSQL
# Puis appliquer
python manage.py migrate
```

### La base de données est désynchronisée

```bash
# Solution radicale : supprimer et recréer
docker compose -f docker-compose.dev.yml down -v
docker compose -f docker-compose.dev.yml up -d
docker exec gosen-dev-web python manage.py migrate
```

---

## Bonnes pratiques

1. **Toujours vérifier** avant d'appliquer : `python manage.py showmigrations`
2. **Tester en local** avant de migrer en production
3. **Sauvegarder** la base de données avant les migrations importantes
4. **Redémarrer** le conteneur après les migrations

---

## Sauvegarde avant migration

```bash
# Dump de la base de données
docker exec gosen-dev-db pg_dump -U gosen gosen_dev > backup_$(date +%Y%m%d_%H%M%S).sql

# Restaurer si nécessaire
cat backup_20260130.sql | docker exec -i gosen-dev-db psql -U gosen -d gosen_dev
```

---

**Projet** : Gosen TurfFilter
**Documentation** : 30 Janvier 2026
