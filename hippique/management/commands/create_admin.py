"""
Management command to create admin user with username 'admin' and password 'admin'
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Create admin user with username "admin" and password "admin"'

    def handle(self, *args, **options):
        User = get_user_model()

        # Check if admin user already exists
        if User.objects.filter(username='admin').exists():
            self.stdout.write(self.style.WARNING('Admin user already exists'))
            return

        # Create admin user
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin'
        )

        self.stdout.write(self.style.SUCCESS('Admin user created successfully'))
        self.stdout.write(self.style.SUCCESS('Username: admin'))
        self.stdout.write(self.style.SUCCESS('Password: admin'))
