# Generated by Django 2.0.2 on 2018-03-11 11:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('debates', '0011_debate_users_downvoting'),
    ]

    operations = [
        migrations.AddField(
            model_name='argument',
            name='modnote',
            field=models.TextField(blank=True, max_length=200000),
        ),
    ]
