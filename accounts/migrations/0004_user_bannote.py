# Generated by Django 2.0.2 on 2018-03-16 22:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_user_bandate'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='bannote',
            field=models.CharField(blank=True, max_length=10000),
        ),
    ]
