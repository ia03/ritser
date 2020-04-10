# Generated by Django 2.2 on 2020-04-10 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('debates', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='topic',
            name='private',
        ),
        migrations.AddField(
            model_name='topic',
            name='is_default',
            field=models.BooleanField(default=False),
        ),
    ]
