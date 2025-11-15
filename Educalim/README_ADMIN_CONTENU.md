# Guide d'utilisation de l'administration des Contenus

## 📋 Vue d'ensemble

Le modèle `Contenu` permet de gérer les ressources pédagogiques (fiches, sujets, cahiers types) rattachées à des leçons (collège) ou des chapitres (lycée).

## 🎯 Flux de travail dans l'administration Django

### 1. Accès à l'administration
- Connectez-vous à l'administration Django
- Allez dans la section "Educationalims" → "Contenus"

### 2. Étape 1 : Choix de la discipline
- Sélectionnez une discipline dans la liste déroulante
- Exemple : Mathématiques, SVT, Physique-Chimie, etc.

### 3. Étape 2 : Sélection automatique du niveau
- **Automatique** : Quand vous choisissez une discipline, les niveaux correspondants s'affichent
- **Organisation** : Les niveaux sont groupés par cycle (Collège / Lycée)
- Choisissez le niveau approprié (ex: 6ème, Seconde, Terminale, etc.)

### 4. Étape 3 : Sélection de l'unité d'apprentissage
Le champ s'adapte automatiquement selon le niveau choisi :

#### 🏫 Pour le Collège
- **Champ actif** : "Leçon"
- **Champ désactivé** : "Chapitre"
- Les leçons s'affichent avec leur numéro et leur palier/partie d'appartenance

#### 🎓 Pour le Lycée
- **Champ actif** : "Chapitre"
- **Champ désactivé** : "Leçon"
- Les chapitres s'affichent avec leur numéro et leur palier/partie d'appartenance

### 5. Étape 4 : Finalisation
- **Titre** : Donnez un titre clair au contenu
- **Description** : Ajoutez une description détaillée (optionnel)
- **Type de contenu** : Choisissez entre :
  - Fiche
  - Cahier Type
  - Sujet
- **Fichier** : Téléversez votre fichier (PDF, DOC, HTML, etc.)

## 📁 Types de fichiers supportés

- PDF (.pdf)
- Documents Word (.doc, .docx)
- Fichiers texte (.txt)
- Fichiers HTML (.html, .htm)
- Images (.jpg, .png, .gif)
- Vidéos (.mp4, .avi)
- Audio (.mp3, .wav)

## ✅ Validations automatiques

L'administration vérifie automatiquement :
- Que le niveau appartient bien à la discipline choisie
- Pour le collège : qu'une leçon est sélectionnée
- Pour le lycée : qu'un chapitre est sélectionné
- Que la leçon/chapitre appartient bien au niveau spécifié

## 🔧 Dépannage

### Le champ "Niveau" reste vide ?
- Assurez-vous d'avoir sélectionné une discipline d'abord
- La liste se charge automatiquement après sélection de la discipline

### Les champs "Leçon" ou "Chapitre" ne s'affichent pas ?
- Vérifiez qu'un niveau est bien sélectionné
- Assurez-vous qu'il existe des leçons/chapitres pour ce niveau

### Erreur de validation ?
- Le système vous indiquera précisément quel champ corriger
- Les messages d'erreur sont explicites et guidés

## 📊 Recherche et filtrage

Dans la liste des contenus, vous pouvez filtrer par :
- Discipline
- Niveau
- Cycle (Collège/Lycée)
- Type de contenu
- Date de création

La recherche fonctionne sur :
- Titre du contenu
- Description
- Nom de la discipline/niveau
- Titre de la leçon/chapitre associé

---

**Le système est conçu pour être intuitif et guider l'utilisateur à chaque étape !** 🚀