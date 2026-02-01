from django.db import migrations

def upgrade(apps, schema_editor):
    # Modifier la contrainte gosen_userprofile pour ON DELETE CASCADE
    if schema_editor.connection.vendor == 'postgresql':
        schema_editor.execute('''
            ALTER TABLE gosen_userprofile 
            DROP CONSTRAINT gosen_userprofile_user_id_5afcdb0c_fk_auth_user_id;
            
            ALTER TABLE gosen_userprofile 
            ADD CONSTRAINT gosen_userprofile_user_id_5afcdb0c_fk_auth_user_id 
            FOREIGN KEY (user_id) REFERENCES auth_user(id) 
            ON DELETE CASCADE 
            DEFERRABLE INITIALLY DEFERRED;
        ''')

def downgrade(apps, schema_editor):
    # Remettre la contrainte d'origine
    if schema_editor.connection.vendor == 'postgresql':
        schema_editor.execute('''
            ALTER TABLE gosen_userprofile 
            DROP CONSTRAINT gosen_userprofile_user_id_5afcdb0c_fk_auth_user_id;
            
            ALTER TABLE gosen_userprofile 
            ADD CONSTRAINT gosen_userprofile_user_id_5afcdb0c_fk_auth_user_id 
            FOREIGN KEY (user_id) REFERENCES auth_user(id) 
            DEFERRABLE INITIALLY DEFERRED;
        ''')

class Migration(migrations.Migration):
    dependencies = [
        ('gosen', '0005_alter_abonnement_user_constraint'),
    ]

    operations = [
        migrations.RunPython(upgrade, downgrade),
    ]
