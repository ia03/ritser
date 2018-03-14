# Generated by Django 2.0.2 on 2018-03-14 03:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('reversion', '0001_squashed_0004_auto_20160611_1202'),
    ]

    operations = [
        migrations.CreateModel(
            name='Argument',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('approvalstatus', models.IntegerField(db_index=True, default='1')),
                ('order', models.IntegerField(db_index=True, default='0')),
                ('side', models.IntegerField(default='0')),
                ('active', models.BooleanField(default=True)),
                ('title', models.CharField(max_length=300)),
                ('body', models.TextField(max_length=200000)),
                ('modnote', models.TextField(blank=True, max_length=200000)),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('edited_on', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Debate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slvl', models.IntegerField(default='1')),
                ('approvalstatus', models.IntegerField(default='1')),
                ('karma', models.IntegerField(db_index=True, default='0')),
                ('active', models.BooleanField(default=True)),
                ('question', models.CharField(max_length=300)),
                ('description', models.TextField(blank=True, max_length=200000)),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('edited_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('approved_on', models.DateTimeField(blank=True, db_index=True, default=django.utils.timezone.now, null=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='debates_owned', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RevisionData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.GenericIPAddressField()),
                ('revision', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reversion.Revision')),
            ],
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('name', models.CharField(db_index=True, max_length=30, primary_key=True, serialize=False, unique=True)),
                ('title', models.CharField(blank=True, max_length=30)),
                ('private', models.BooleanField(default=False)),
                ('description', models.TextField(blank=True, default='The description has not been set yet.', max_length=600000)),
                ('slvl', models.IntegerField(default='0')),
                ('debslvl', models.IntegerField(default='1')),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('edited_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='topics_created', to=settings.AUTH_USER_MODEL)),
                ('moderators', models.ManyToManyField(related_name='moderator_of', to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='topics_owned', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='debate',
            name='topic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='debates', to='debates.Topic'),
        ),
        migrations.AddField(
            model_name='debate',
            name='users_downvoting',
            field=models.ManyToManyField(blank=True, related_name='debates_downvoted', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='debate',
            name='users_upvoting',
            field=models.ManyToManyField(blank=True, related_name='debates_upvoted', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='argument',
            name='debate',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='arguments', to='debates.Debate'),
        ),
        migrations.AddField(
            model_name='argument',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='arguments_owned', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='argument',
            name='topic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='arguments', to='debates.Topic'),
        ),
    ]
