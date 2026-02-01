from django.db import migrations

def upgrade(apps, schema_editor):
    # Supprimer l'ancienne contrainte et en créer une nouvelle avec ON DELETE CASCADE
    if schema_editor.connection.vendor == 'postgresql':
        schema_editor.execute('''
            ALTER TABLE gosen_abonnement 
            DROP CONSTRAINT gosen_abonnement_utilisateur_id_fdd1e3e5_fk_auth_user_id;
            
            ALTER TABLE gosen_abonnement 
            ADD CONSTRAINT gosen_abonnement_utilisateur_id_fdd1e3e5_fk_auth_user_id 
            FOREIGN KEY (utilisateur_id) REFERENCES auth_user(id) 
            ON DELETE CASCADE 
            DEFERRABLE INITIALLY DEFERRED;
        ''')

def downgrade(apps, schema_editor):
    # Remettre la contrainte d'origine
    if schema_editor.connection.vendor == 'postgresql':
        schema_editor.execute('''
            ALTER TABLE gosen_abonnement 
            DROP CONSTRAINT gosen_abonnement_utilisateur_id_fdd1e3e5_fk_auth_user_id;
            
            ALTER TABLE gosen_abonnement 
            ADD CONSTRAINT gosen_abonnement_utilisateur_id_fdd1e3e5_fk_auth_user_id 
            FOREIGN KEY (utilisateur_id) REFERENCES auth_user(id) 
            DEFERRABLE INITIALLY DEFERRED;
        ''')

class Migration(migrations.Migration):
    dependencies = [
        ('gosen', '0004_delete_adminuser'),
    ]

    operations = [
        migrations.RunPython(upgrade, downgrade),
    ]
