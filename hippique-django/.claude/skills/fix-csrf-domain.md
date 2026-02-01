# Fix CSRF Error 403 with Custom Domain

## Problem
Erreur 403 CSRF lors de la connexion à l'admin via un nom de domaine (ex: dev.filtreexpert.org/admin) alors que ça fonctionne avec l'IP.

## Solution

```bash
ssh -i ~/.ssh/id_ed25519 root@72.62.181.239

# Modifier settings.py pour ajouter le domaine aux CSRF_TRUSTED_ORIGINS
docker exec -i gosen-dev-web python3 << 'PYEOF'
with open('/code/gosen_project/settings.py', 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'CSRF_TRUSTED_ORIGINS' in line and 'else' in line:
        lines[i] = "CSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',') if os.environ.get('CSRF_TRUSTED_ORIGINS') else ['http://72.62.181.239:8082', 'http://localhost:8082', 'http://72.62.181.239:8083', 'http://localhost:8083', 'http://VOTRE_DOMAINE', 'https://VOTRE_DOMAINE']\n"
        break

with open('/code/gosen_project/settings.py', 'w') as f:
    f.writelines(lines)
print('Done')
PYEOF

# Redémarrer le conteneur
docker restart gosen-dev-web
```

## Remplacer VOTRE_DOMAINE

Exemples:
- `dev.filtreexpert.org`
- `filtreexpert.org`
- `www.mondomaine.com`

## Verification

```bash
docker exec gosen-dev-web grep 'VOTRE_DOMAINE' /code/gosen_project/settings.py
```
