# Git Workflow - Gosen Filter

## Branches

- **`main`** : Branche principale stable
- **`prod`** : Branche de production (port 8083)
- **`dev`** : Branche de développement (port 8082)
- **Feature branches** : Branches temporaires pour les fonctionnalités

---

## Workflow standard

### 1. Créer une branche

```bash
cd C:\Users\HP\360\Desktop\hippique-django

# Depuis prod
git checkout prod

# Créer une nouvelle branche
git checkout -b feature/nouvelle-fonctionnalite
```

### 2. Faire les modifications

```bash
# Modifier les fichiers
# ...

# Voir les changements
git status
git diff
```

### 3. Commiter

```bash
# Ajouter les fichiers modifiés
git add .

# Commiter avec un message clair
git commit -m "feat: ajouter la fonctionnalité X"

# Ou pour un commit amendé
git commit --amend
```

### 4. Pousser

```bash
# Pousser la branche
git push origin feature/nouvelle-fonctionnalite

# Ou la première fois
git push -u origin feature/nouvelle-fonctionnalite
```

### 5. Merger dans prod

```bash
# Changer de branche
git checkout prod

# Mettre à jour prod
git pull origin prod

# Merger
git merge feature/nouvelle-fonctionnalite

# Pousser
git push origin prod

# Supprimer la branche de fonctionnalité
git branch -d feature/nouvelle-fonctionnalite
```

---

## Types de commits

Utilisez des préfixes clairs :

- `feat:` Nouvelle fonctionnalité
- `fix:` Correction de bug
- `docs:` Documentation
- `style:` Style (formatage, etc.)
- `refactor:` Refactorisation
- `test:` Tests
- `chore:` Tâche diverses

Exemples :
```bash
git commit -m "feat: ajouter le filtrage par alternance"
git commit -m "fix: corriger l'affichage des résultats"
git commit -m "docs: mettre à jour FILTREEXPERT_PAIEMENT.md"
```

---

## Commandes utiles

### Voir l'historique

```bash
# Graphique
git log --oneline --graph --all

# Derniers commits
git log --oneline -10

# Commit avec diff
git log -p -1
```

### Annuler des changements

```bash
# Annuler les modifications non commitées
git checkout -- fichier.py

# Annuler le dernier commit (garder les changements)
git reset --soft HEAD~1

# Annuler le dernier commit (supprimer les changements)
git reset --hard HEAD~1
```

### Stash

```bash
# Stasher les modifications
git stash

# Voir les stashes
git stash list

# Appliquer le dernier stash
git stash pop

# Appliquer un stash spécifique
git stash apply stash@{1}
```

---

## Conflits de fusion

```bash
# Quand il y a un conflit
git merge feature/branche

# Éditer les fichiers avec conflits
# Recherchez <<<<<<<, =======, >>>>>>

# Résoudre manuellement

# Marquer comme résolu
git add fichier.py

# Continuer le merge
git merge --continue

# Ou annuler
git merge --abort
```

---

## Reset hard (après discussion avec l'utilisateur)

⚠️ **DANGER : Cette commande supprime les modifications non commitées**

```bash
# Reset à un commit spécifique
git reset --hard 662ee73

# Nettoyer les fichiers non suivis
git clean -fd

# NE PAS utiliser pour exclure des dossiers
git clean -fd --dry-run  # Pour voir ce qui sera supprimé
```

---

## Synchroniser avec le serveur

```bash
# Récupérer les changements
git fetch origin

# Voir les différences
git diff origin/prod

# Merger les changements distants
git pull origin prod
```

---

## Tags

```bash
# Créer un tag
git tag v1.0.0

# Pousser les tags
git push origin --tags

# Voir les tags
git tag
```

---

## Bonnes pratiques

1. **Commits fréquents** : Commitez souvent avec des messages clairs
2. **Branche par fonctionnalité** : Une branche = une fonctionnalité
3. **Messages de commit clairs** : Utilisez les préfixes (feat:, fix:, etc.)
4. **Tester avant de merger** : Vérifiez que tout fonctionne
5. **Tirer souvent** : Gardez votre branche à jour avec `git pull`

---

## .gitignore

```gitignore
# Python
*.pyc
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
media/
staticfiles/

# Environnement
.env
.env.dev
.env.prod
.venv
venv/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Claude
.claude/settings.local.json
.github_token

# Autres
*.bak
nul
```

---

**Projet** : Gosen TurfFilter
**Documentation** : 30 Janvier 2026
