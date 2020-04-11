# Generated by Django 2.2 on 2020-04-11 01:26

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('debates', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topic',
            name='moderators',
            field=models.ManyToManyField(blank=True, related_name='moderator_of', to=settings.AUTH_USER_MODEL),
        ),
    ]
