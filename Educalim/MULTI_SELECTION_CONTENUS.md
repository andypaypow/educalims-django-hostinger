# Multi-sélection des unités d'apprentissage dans les Contenus

## 🎯 Nouvelle fonctionnalité

Le modèle `Contenu` supporte maintenant la **multi-sélection** des leçons et/ou des chapitres, permettant à un contenu de couvrir plusieurs unités d'apprentissage.

## 🔄 Changements apportés

### 1. Relations ManyToMany
- **Avant** : Une leçon OU un chapitre (ForeignKey)
- **Maintenant** : Plusieurs leçons ET/OU plusieurs chapitres (ManyToMany)

### 2. Interface améliorée
- **Sélection multiple** : Interface `filter_horizontal` pour choisir plusieurs éléments
- **Flux intelligent** : Le formulaire s'adapte selon le cycle (collège/lycée)
- **Validation renforcée** : Vérifications selon le cycle et le niveau

## 📋 Flux de travail dans l'administration

### Étape 1 : Choix de la discipline
```
Discipline : [Mathématiques ▼]
```

### Étape 2 : Sélection du niveau
```
Niveau : [-----------------] → S'affiche automatiquement
          [optgroup Collège]
          ├── 6ème
          ├── 5ème
          └── 4ème
          [optgroup Lycée]
          ├── Seconde
          ├── Première
          └── Terminale
```

### Étape 3 : Multi-sélection des unités
Selon le niveau choisi :

#### 🏫 Pour le Collège
```
Leçons disponibles : [_________________________] [ Ajouter → ]
                  1. Numération      [ ___________________ ] [ × ]
                  2. Géométrie      [ ___________________ ] [ × ]
                  3. Mesures       [ ___________________ ] [ ← ]
Chapitres : [  Désactivé  ]
```

#### 🎓 Pour le Lycée
```
Leçons : [  Désactivé  ]
Chapitres disponibles : [__________________] [ Ajouter → ]
                     1. Algèbre      [ _______________ ] [ × ]
                     2. Fonctions   [ _______________ ] [ × ]
                     3. Trigonométrie[ _______________ ] [ ← ]
```

#### 🌟 Usage mixte (si nécessaire)
```
Leçons disponibles : [...]
Chapitres disponibles : [...]
```

## ✅ Validation automatique

### Règles de cycle
- **Collège** : Au moins une leçon doit être sélectionnée
- **Lycée** : Au moins un chapitre doit être sélectionné
- **Mixte** : Possible mais déconseillé pour rester cohérent

### Validation de cohérence
- Les leçons/chapitres doivent appartenir au **niveau** choisi
- Les leçons/chapitres doivent appartenir à la **discipline** choisie

### Messages d'erreur clairs
```
❌ "Pour le collège, au moins une leçon doit être sélectionnée."
❌ "La leçon 'Algèbre' ne correspond pas au niveau spécifié."
❌ "Le chapitre 'Fonctions' n'appartient pas à la discipline spécifiée."
```

## 📊 Affichage amélioré

### Dans la liste des contenus
- **Compteur visuel** : `[2 leçons, 1 chapitre]`
- **Concise** : `2 Leçons` ou `1 Chapitre`
- **Mixte** : `2L, 1C`

### Dans le formulaire
- **Bordure verte** : Confirme que le JavaScript est chargé
- **Interface `filter_horizontal`** : Sélection intuitive avec double colonne
- **Désactivation automatique** : Les champs non pertinents sont grisés

## 🛠 Fonctionnalités techniques

### Propriétés du modèle
```python
# Compte les unités associées
contenu.lecons.count()        # → 3
contenu.chapitres.count()      # → 2

# Affichage formaté
contenu.unite_apprentissage_display  # → "3 Leçons, 2 Chapitres"

# Liste complète
contenu.unites_apprentissage        # → ["Leçon: Titre1", "Chapitre: Titre2"]
```

### JavaScript dynamique
- **Rechargement automatique** : Les listes se mettent à jour selon le niveau
- **Mode dégradé** : Script de secours si le fichier externe ne se charge pas
- **Console debugging** : Logs détaillés pour le dépannage

## 🎨 Cas d'usage

### 1. Fiche de révision (Collège)
- **Sélection** : Leçons 3, 4, 5 d'un palier
- **Avantage** : Une seule fiche couvre plusieurs leçons

### 2. Cahier de synthèse (Lycée)
- **Sélection** : Chapitres 1, 2, 3 d'un même niveau
- **Avantage** : Cohérence thématique

### 3. Ressource transversale
- **Sélection** : Plusieurs chapitres de niveaux différents (même discipline)
- **Usage** : Document de révision pour examen

### 4. Support personnalisé
- **Sélection** : Leçons + chapitres pour un support complet
- **Avantage** : Flexibilité maximale

## 🔍 Dépannage

### Les champs ManyToMany ne s'affichent pas ?
1. **Vérifiez la console** (F12) → Messages de debugging
2. **Rechargez la page** avec Ctrl+F5
3. **Vérifiez la migration** : `python manage.py migrate`

### Impossible de sélectionner plusieurs éléments ?
1. Le champ est-il bien en mode `filter_horizontal` ?
2. Les flèches "Ajouter →" et "←" fonctionnent-elles ?
3. Essayez de cliquer sur les éléments pour les sélectionner

### Validation échoue ?
1. Vérifiez que le niveau et la discipline sont cohérents
2. Pour le collège : assurez-vous d'avoir sélectionné des leçons
3. Pour le lycée : assurez-vous d'avoir sélectionné des chapitres

---

La multi-sélection rend l'administration beaucoup plus flexible et **parfaitement adaptée aux besoins réels** des ressources pédagogiques ! 🚀