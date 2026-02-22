# Guide de modification - base.html

## 📍 Emplacement du fichier

/root/gosen-filter-dev/gosen/templates/gosen/base.html

---

## 🎯 Structure du fichier

### 1. HEAD (Meta tags et CSS)
- Meta tags pour le cache
- Titre de la page
- Feuille de style CSS

### 2. HERO SECTION (Section dorée d'accueil)
- Badge: Pour les Turfistes Stratèges
- Titre: Filtre Expert (doré)
- Sous-titre: Description
- 3 étapes (Stratégies, Filtres, Combinaisons)
- Stats: 8008 → 20+

### 3. HEADER (Logo + Titre + Sous-titre)
- Logo (lien WhatsApp)
- Titre: Filtre Expert
- Sous-titre: Application de filtrage...

### 4. GRID CONTAINER (Cartes principales)
- Configuration (nombre de partants, taille combinaison)
- Pronostics (saisie des groupes)
- Synthèse des Pronostics
- Critères de Filtrage
- Résultats du Filtrage
- Synthèse de l'Expert
- Partenaires

---

## 🎨 Modifications courantes

### Modifier le texte du Badge
Chercher: Pour les Turfistes Stratèges
Remplacer par: VOTRE TEXTE

### Modifier le titre principal
Chercher: Filtre Expert
Remplacer par: VOTRE TITRE

### Modifier les 3 étapes

Étape 1 - Rechercher:
<h3>Vos Stratégies Favorites</h3>
<p>Système, presse...</p>

Étape 2 - Rechercher:
<h3>Filtres Experts</h3>
<p>Expert 1 et Poids, notre combo</p>

Étape 3 - Rechercher:
<h3>Vos Combinaisons</h3>
<p>20+ combinaisons fiables</p>

### Modifier les couleurs

Couleur dorée: #D4AF37
Or brillant: #FFD700
Vert Gabon: #009E60
Jaune Gabon: #FFCE00
Bleu Gabon: #3A75C4

---

## 🚀 Comment appliquer les modifications

1. Éditer le fichier:
   nano /root/gosen-filter-dev/gosen/templates/gosen/base.html

2. Sauvegarder: Ctrl+O, Entrée
3. Quitter: Ctrl+X

4. Redémarrer:
   cd /root/gosen-filter-dev
   docker compose -f docker-compose.dev.yml restart web

5. Vider le cache navigateur: Ctrl+F5
