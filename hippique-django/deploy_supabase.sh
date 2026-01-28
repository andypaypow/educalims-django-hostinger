#!/bin/bash
# Script de déploiement des Edge Functions Supabase pour FiltreExpert

# Configuration
SUPABASE_PROJECT_REF="qfkyzljqykymahlpmdnu"
SUPABASE_DIR="/root/supabase-functions"

# Couleurs pour le output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Déploiement des Edge Functions FiltreExpert ===${NC}"
echo ""

# Vérifier si l'access token est fourni
if [ -z "$SUPABASE_ACCESS_TOKEN" ]; then
    echo -e "${RED}Erreur: SUPABASE_ACCESS_TOKEN non défini${NC}"
    echo -e "${YELLOW}Pour générer un token:${NC}"
    echo "1. Allez sur https://supabase.com/dashboard/account/tokens"
    echo "2. Cliquez sur 'Generate new token'"
    echo "3. Exécutez: export SUPABASE_ACCESS_TOKEN='sbp_...'"
    exit 1
fi

# Se connecter à Supabase
echo -e "${YELLOW}Connexion à Supabase...${NC}"
~/.local/bin/supabase login --token "$SUPABASE_ACCESS_TOKEN"

# Créer le dossier des fonctions s'il n'existe pas
mkdir -p "$SUPABASE_DIR/functions"

# Copier les fichiers de fonctions
echo -e "${YELLOW}Copie des fichiers Edge Functions...${NC}"
mkdir -p "$SUPABASE_DIR/functions/turboquinte-filter"
mkdir -p "$SUPABASE_DIR/functions/turboquinte-backtest"

# Note: Les fichiers doivent être copiés depuis le local vers Hostinger
# Veuillez copier manuellement les fichiers ou utiliser scp

# Lier le projet
echo -e "${YELLOW}Liaison du projet Supabase...${NC}"
cd "$SUPABASE_DIR" || exit 1
~/.local/bin/supabase link --project-ref "$SUPABASE_PROJECT_REF"

# Déployer les fonctions
echo -e "${GREEN}Déploiement de turboquinte-filter...${NC}"
~/.local/bin/supabase functions deploy turboquinte-filter

echo -e "${GREEN}Déploiement de turboquinte-backtest...${NC}"
~/.local/bin/supabase functions deploy turboquinte-backtest

echo ""
echo -e "${GREEN}=== Déploiement terminé ===${NC}"
echo ""
echo "URLs des Edge Functions:"
echo "  - turboquinte-filter: https://qfkyzljqykymahlpmdnu.supabase.co/functions/v1/turboquinte-filter"
echo "  - turboquinte-backtest: https://qfkyzljqykymahlpmdnu.supabase.co/functions/v1/turboquinte-backtest"
echo ""
echo "Frontend: http://72.62.181.239:8090/"
