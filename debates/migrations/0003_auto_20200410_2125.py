# Generated by Django 2.2 on 2020-04-10 21:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('debates', '0002_auto_20200410_2019'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topic',
            name='is_default',
            field=models.BooleanField(default=False, verbose_name='users are subscribed by default'),
        ),
    ]
