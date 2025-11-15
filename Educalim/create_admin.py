#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'site_educatif.settings')
django.setup()

from django.contrib.auth.models import User

# Check if superuser already exists
if User.objects.filter(username='admin').exists():
    print("Superuser 'admin' already exists")
else:
    # Create superuser
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("Superuser 'admin' created successfully")
    print("Username: admin")
    print("Password: admin123")