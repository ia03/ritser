# Generated by Django 2.0.2 on 2018-03-11 16:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='approvedargs',
            field=models.IntegerField(default='0'),
        ),
    ]
