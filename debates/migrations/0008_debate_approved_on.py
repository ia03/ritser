# Generated by Django 2.0.2 on 2018-03-10 02:13

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('debates', '0007_auto_20180308_0453'),
    ]

    operations = [
        migrations.AddField(
            model_name='debate',
            name='approved_on',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
