#!/bin/bash
# Script de déploiement Docker pour Educalims sur Hostinger

set -e

echo "🐳 Déploiement Docker d'Educalims..."

# Installer Docker si pas installé
if ! command -v docker &> /dev/null; then
    echo "📦 Installation de Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    systemctl enable docker
    systemctl start docker
fi

# Installer Docker Compose si pas installé
if ! command -v docker-compose &> /dev/null; then
    echo "📦 Installation de Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

echo "✅ Docker et Docker Compose sont prêts"

# Créer le répertoire de déploiement
DEPLOY_DIR="/root/educalims-docker"
mkdir -p $DEPLOY_DIR
cd $DEPLOY_DIR

# Copier les fichiers Docker
echo "📋 Copie des fichiers..."
# Les fichiers doivent être copiés depuis le répertoire du projet

# Créer le fichier .env
if [ ! -f .env ]; then
    echo "🔑 Création du fichier .env..."
    cat > .env << EOF
SECRET_KEY=django-insecure-$(openssl rand -base64 32)
DEBUG=True
ALLOWED_HOSTS=srv1256927.hstgr.cloud,72.62.181.239,localhost
POSTGRES_DB=educalims
POSTGRES_USER=educalims
POSTGRES_PASSWORD=$(openssl rand -base64 16 | tr -d '/+=')
DB_HOST=db
DB_PORT=5432
EOF
fi

# Arrêter les conteneurs existants
echo "🛑 Arrêt des conteneurs existants..."
docker-compose down 2>/dev/null || true

# Arrêter les services systemd existants
echo "🛑 Arrêt des services systemd..."
systemctl stop educalims 2>/dev/null || true
systemctl stop nginx 2>/dev/null || true

# Construire et démarrer
echo "🔨 Construction des images Docker..."
docker-compose build

echo "🚀 Démarrage des conteneurs..."
docker-compose up -d

# Attendre que les services soient prêts
echo "⏳ Attente du démarrage des services..."
sleep 10

# Exécuter les migrations
echo "📊 Exécution des migrations..."
docker-compose exec web python manage.py migrate --noinput

# Créer le superutilisateur
echo "👤 Création du superutilisateur..."
docker-compose exec web python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@educalims.com', 'Admin1234!')
    print('Superutilisateur admin créé')
else:
    print('Superutilisateur admin existe déjà')
"

# Collecter les static files
echo "📁 Collecte des fichiers statiques..."
docker-compose exec web python manage.py collectstatic --noinput

echo ""
echo "✅ Déploiement terminé !"
echo ""
echo "🌍 URLs d'accès :"
echo "   Site: http://srv1256927.hstgr.cloud/"
echo "   Admin: http://srv1256927.hstgr.cloud/admin/"
echo "   Webhook: http://srv1256927.hstgr.cloud/webhook/cyberschool/"
echo ""
echo "🔐 Identifiants admin:"
echo "   Username: admin"
echo "   Password: Admin1234!"
echo ""
echo "📊 Vérifier l'état:"
echo "   docker-compose ps"
echo "   docker-compose logs -f"
