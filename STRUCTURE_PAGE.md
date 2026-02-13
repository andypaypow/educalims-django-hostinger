# Structure de la page daccueil (home)

## Sections principales de la page

### 1. Header
- Lieu: base.html, apres le navbar
- Contenu: Logo, titre, sous-titre

### 2. Section Configuration
- Lieu: base.html, dans grid-container
- Contenu: Inputs pour nombre de partants et taille de combinaison

### 3. Section Saisie des pronostics
- Lieu: base.html, dans pronostics-card
- Contenu: Zone de saisie avec bouton dupload dimage

### 4. Section Synthese des Pronostics
- Lieu: base.html, dans synthesis-pronos-card
- Contenu: Carte avec 2 sous-sections (Par Citation, Par Position)

### 5. Section Criteres de filtrage
- Lieu: base.html, dans filter-card
- Contenu: Conteneur filtres + bouton dajout

### 6. Section Resultats du filtrage
- Lieu: base.html, dans subscription-content-block
- Contenu: Tabs (Resultats/Backtest) + affichage

### 7. Section Synthese de lExpert
- Lieu: base.html, apres Resultats
- Contenu: Classement global pondere

### 8. Footer
- Lieu: base.html, fin de page
- Fichier: gosen/templates/gosen/footer.html
- Contenu: Copyright uniquement

### 9. Section Contact (formulaire)
- Lieu: base.html, apres le footer
- Fichier: gosen/templates/gosen/contact_section.html
- Contenu: Formulaire de contact

### 10. Modals
- Lieu: base.html, apres la section contact
- Contenu: Modals (ajout filtre, source image)

### 11. Floating Counter
- Lieu: base.html, apres modals
- Contenu: Bouton flottant (combinaisons restantes)

### 12. Scripts
- Lieu: base.html, fin du body
- Fichier: static/gosen/js/main.js
- Contenu: Scripts JavaScript

---

## Fichiers templates

- base.html - Template principal
- footer.html - Footer (inclus dans base.html)
- contact_section.html - Section contact (incluse dans base.html)

---

## Comment localiser et modifier

Pour modifier une section specifique, se referer au tableau ci-dessus et trouver:
1. Le fichier template concerne
2. La ligne dans base.html (approximative)
3. Le contenu de la section
