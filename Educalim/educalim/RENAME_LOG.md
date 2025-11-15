# Renommage du fichier `nul`

## Contexte
Le fichier `nul` (sans extension) était présent dans le dépôt.  
Ce nom est **réservé par Windows** (DOS) et provoque une erreur lors des opérations Git sur ce système.

## Action effectuée
- Date : $(Get-Date -Format "2025-11-15)")
- Auteur : $(git config user.name) &lt;$(git config user.email)&gt;
- Renommage : `nul` → `nul_save.txt`
- Commande :
  ```powershell
  Move-Item Educalim\nul Educalim\nul_save.txt