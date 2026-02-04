from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('gosen', '0010_subscriptionpayment_userprofile_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='device_id',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='derniere_connexion',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='nb_filtres_realises',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='est_actif',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='a_un_abonnement',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='type_abonnement',
            field=models.CharField(
                choices=[('mensuel', 'Mensuel'), ('annuel', 'Annuel'), ('a_vie', 'À vie'), ('gratuit', 'Gratuit')],
                default='gratuit',
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='date_debut_abonnement',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='date_fin_abonnement',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='filtres_gratuits_utilises',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='date_reset_filtres',
            field=models.DateField(auto_now_add=True),
        ),
    ]
