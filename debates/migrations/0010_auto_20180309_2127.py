# Generated by Django 2.0.2 on 2018-03-10 02:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('debates', '0009_auto_20180309_2117'),
    ]

    operations = [
        migrations.AlterField(
            model_name='debate',
            name='question',
            field=models.CharField(max_length=300, unique=True),
        ),
    ]