#!/bin/bash
set -e

echo "⏳ Waiting for PostgreSQL to be ready..."
until PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c '\q' 2>/dev/null; do
  echo "⏳ PostgreSQL is unavailable - sleeping"
  sleep 2
done
echo "✅ PostgreSQL is ready!"

echo "📦 Applying database migrations..."
python manage.py migrate --noinput
echo "✅ Migrations applied!"

echo "👤 Creating superuser if not exists..."
python manage.py shell << 'PYEOF'
from django.contrib.auth import get_user_model
import os

User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"✅ Superuser '{username}' created!")
else:
    print(f"ℹ️  Superuser '{username}' already exists.")
PYEOF

echo "🚀 Starting Gunicorn..."
exec gunicorn "$DJANGO_SETTINGS_MODULE.wsgi:application" --bind 0.0.0.0:8000
