from django.db import migrations

def upgrade(apps, schema_editor):
    # Supprimer les tables inutiles dans l'ordre inverse des dépendances
    if schema_editor.connection.vendor == 'postgresql':
        schema_editor.execute('DROP TABLE IF EXISTS gosen_abonnement CASCADE;')
        schema_editor.execute('DROP TABLE IF EXISTS gosen_paymentrecord CASCADE;')
        schema_editor.execute('DROP TABLE IF EXISTS gosen_produit CASCADE;')
        schema_editor.execute('DROP TABLE IF EXISTS gosen_userprofile CASCADE;')
        schema_editor.execute('DROP TABLE IF EXISTS gosen_webhooklog CASCADE;')

def downgrade(apps, schema_editor):
    # Pour rollback, on ne peut pas recréer les tables facilement sans les modèles
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('gosen', '0006_alter_userprofile_user_constraint'),
    ]

    operations = [
        migrations.RunPython(upgrade, migrations.RunPython.noop),
    ]
