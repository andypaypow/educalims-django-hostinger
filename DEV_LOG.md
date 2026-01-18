# Journal de Developpement - Educalims

## 18 Janvier 2026 - Modifications Admin & Notifications

### 1. Affichage du champ "Recommande par" dans l'admin Django

**Probleme** : Le champ `recommande_par` du modele `UserProfile` n'etait pas visible dans l'admin.

**Solution** : Ajoute un `Inline` et etendu `UserAdmin` dans `educalims/admin.py`

**Fichier modifie** : `/root/educalims-dev/educalims/admin.py`

---

### 2. Ajout de "Recommande par" dans les notifications Telegram

**Solution** : Modifie 3 fonctions dans `educalims/views.py` :

- `notifier_nouveau_abonnement_telegram()` (ligne ~90)
- `notifier_paiement_telegram()` (ligne ~53)
- Notification "ABONNEMENT ACTIVE" dans le webhook (ligne ~616)

**IMPORTANT** : Pour acceder au profil d'un utilisateur :
```python
# CORRECT
profile = abonnement.user.profile if hasattr(abonnement.user, 'profile') else None

# INCORRECT (requete SQL supplementaire)
profile = UserProfile.objects.filter(user=abonnement.user).first()
```

---

### 3. Modification du modele Produit : `duree_jours` -> `date_expiration`

**Probleme** : Le champ `duree_jours` n'etait pas adapte au systeme educatif.

**Solution** : Remplace par `date_expiration` avec defaut au **31 aout** de l'annee en cours.

#### Changements dans `educalims/models.py` :

**a) Fonction helper** (avant la classe Produit) :
```python
def get_default_expiration_date():
    from datetime import date
    return date(date.today().year, 8, 31)
```

**b) Nouveau champ** :
```python
# AVANT
duree_jours = models.PositiveIntegerField(default=30)

# APRES
date_expiration = models.DateField(default=get_default_expiration_date)
```

**c) Methode `activer_abonnement`** :
```python
def activer_abonnement(self, date_expiration=None):
    from datetime import datetime, time
    self.statut = 'ACTIF'
    self.date_debut = timezone.now()
    
    if date_expiration:
        self.date_fin = datetime.combine(date_expiration, time.max)
    else:
        from datetime import date
        default_expiration = date(date.today().year, 8, 31)
        self.date_fin = datetime.combine(default_expiration, time.max)
    self.save()
```

#### Changements dans `educalims/views.py` (ligne ~589) :
```python
# Webhook - Calcul de date_fin
if abonnement.produit and abonnement.produit.date_expiration:
    from datetime import datetime, time
    abonnement.date_fin = datetime.combine(abonnement.produit.date_expiration, time.max)
```

#### Changements dans `educalims/admin.py` :
- Remplacer 'duree_jours' par 'date_expiration' dans :
  - list_display
  - list_filter
  - list_editable

#### Migration Django :
```bash
docker compose -f docker-compose.dev.yml exec web python manage.py makemigrations
docker compose -f docker-compose.dev.yml exec web python manage.py migrate
```

**Migration creee** : `0006_remove_produit_duree_jours_produit_date_expiration.py`

---

## PROBLEMES RENCONTRES & SOLUTIONS

### Probleme 1 : Emojis UTF-8
**Cause** : Encodage multi-octet des emojis.
**Solution** : Utiliser des chaines brutes f"""..."""

### Probleme 2 : Lambda dans les modeles
**Symptome** : `ValueError: Cannot serialize function: lambda`
**Solution** : Utiliser une fonction nommee, pas un lambda.

### Probleme 3 : Acces UserProfile
**Solution** : Toujours verifier avec `hasattr(user, 'profile')`

### Probleme 4 : Modification via SSH
**Solution** : Eviter les imbrications de guillemets complexes

---

## Structure du Projet

```
/root/educalims-dev/
├── educalims/
│   ├── models.py
│   ├── views.py
│   ├── admin.py
│   ├── migrations/
│   └── ...
├── docker-compose.dev.yml
└── manage.py
```

---

## Workflow

```bash
# 1. SSH
ssh -i ~/.ssh/id_ed25519 root@72.62.181.239

# 2. Dev
cd /root/educalims-dev

# 3. Modifier
nano educalims/views.py

# 4. Migrer
docker compose -f docker-compose.dev.yml exec web python manage.py makemigrations
docker compose -f docker-compose.dev.yml exec web python manage.py migrate

# 5. Redemarrer
docker compose -f docker-compose.dev.yml restart web

# 6. Tester
# http://72.62.181.239:8081/

# 7. Deployer
./deploy-to-prod.sh
```

---

## Commandes Utiles

```bash
# Logs
docker compose -f docker-compose.dev.yml logs -f web

# Shell Django
docker compose -f docker-compose.dev.yml exec web python manage.py shell

# Superuser
docker compose -f docker-compose.dev.yml exec web python manage.py createsuperuser
```

---

## Access

- **Dev** : http://72.62.181.239:8081/
- **Admin Dev** : http://72.62.181.239:8081/admin/
- **Prod** : http://72.62.181.239/
- **SSH** : ssh -i ~/.ssh/id_ed25519 root@72.62.181.239

---

## Pieges a Eviter

1. Ne JAMAIS modifier directement en prod
2. Toujours migrer apres modification des modeles
3. Ne pas utiliser de lambda dans les modeles
4. Ne pas oublier de redemarrer le conteneur

---

**Derniere mise a jour** : 18 Janvier 2026
**Projet** : Educalims - Plateforme educative
