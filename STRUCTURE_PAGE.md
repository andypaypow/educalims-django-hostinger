# Structure de la page d'accueil (home) - Ordre de navigation du haut vers le bas

## Sections principales de la page

### 1. Auth Navbar
- **Lieu :** base.html, tout en haut du body
- **Fichier :** gosen/templates/gosen/auth_navbar.html
- **Contenu :** Barre de navigation avec authentification

### 2. Header
- **Lieu :** base.html, dans container
- **Contenu :** Logo (lien WhatsApp), titre "Filtre Expert", sous-titre

### 3. Section Configuration (1)
- **Lieu :** base.html, dans grid-container
- **Contenu :** Inputs pour nombre de partants et taille de combinaison

### 4. Section Saisie des pronostics (2)
- **Lieu :** base.html, dans grid-container
- **Contenu :** Zone de saisie avec bouton d'upload d'image et explication des filtres

### 5. Section Synthèse des Pronostics
- **Lieu :** base.html, synthesis-pronos-card
- **Contenu :** 2 sous-sections
  - Par Citation (classement par nombre d'apparitions)
  - Par Position (classement pondéré)

### 6. Section Critères de filtrage (3)
- **Lieu :** base.html, filter-card
- **Contenu :** Conteneur filtres + bouton d'ajout

### 7. Section Résultats du filtrage (4)
- **Lieu :** base.html, subscription-content-block
- **Contenu :** Tabs (Résultats/Backtest) + Synthèse des Chevaux Filtrés

### 8. Section Synthèse de l'Expert
- **Lieu :** base.html, après Résultats
- **Contenu :** Classement global pondéré (citation + position + résultats filtrés)

### 9. Section Contact (formulaire)
- **Lieu :** base.html, avant le footer
- **Fichier :** gosen/templates/gosen/contact_section.html
- **Contenu :** Formulaire de contact inline

### 10. Footer
- **Lieu :** base.html, après contact
- **Fichier :** gosen/templates/gosen/footer.html
- **Contenu :** Copyright

### 11. Floating Counter
- **Lieu :** base.html, après footer
- **Contenu :** Bouton flottant (combinaisons restantes)

### 12. Modals
- **Lieu :** base.html, après floating counter
- **Contenu :** 2 modals
  - Modal ajout filtre (Expert 1/2, Poids, Statistiques, Alternance)
  - Modal source image (Fichier/Photo)

### 13. Scripts
- **Lieu :** base.html, fin du body
- **Fichier :** static/gosen/js/main.js
- **Contenu :** Scripts JavaScript

---

## Fichiers templates (dans l'ordre d'apparition)

- `base.html` - Template principal (contient la structure de page)
- `auth_navbar.html` - Barre de navigation avec auth (incluse dans base.html)
- `contact_section.html` - Section contact formulaire (incluse dans base.html)
- `footer.html` - Footer (inclus dans base.html)

---

## Comment localiser et modifier

Pour modifier une section spécifique, se reporter au tableau ci-dessus et trouver :
1. Le fichier template concerne
2. La ligne dans base.html (approximative)
3. Le contenu de la section

---

## Notes importantes

1. **CSS :** La plupart des styles sont définis inline dans les templates ou dans `static/gosen/css/styles.css`
2. **JavaScript :** Toute la logique interactive est dans `static/gosen/js/main.js`
3. **Base de données :** Les modèles sont dans `gosen/models.py`
4. **Admin :** L'interface admin est configurée dans `gosen/admin.py`