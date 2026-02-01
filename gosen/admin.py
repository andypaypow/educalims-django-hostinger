from django.contrib import admin
from django.contrib.auth.models import User

# Personnalisation de l'admin User pour l'adapter à Gosen
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'is_active', 'is_staff', 'date_joined', 'last_login']
    list_filter = ['is_active', 'is_staff', 'is_superuser']
    search_fields = ['username', 'email']

# Désenregistrer l'admin par défaut et réenregistrer avec notre version
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
