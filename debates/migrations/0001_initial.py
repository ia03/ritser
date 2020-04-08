# Generated by Django 2.2 on 2020-03-29 00:24

import debates.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
from django.contrib.postgres.operations import CITextExtension


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('reversion', '0001_squashed_0004_auto_20160611_1202'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        CITextExtension(),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('name', debates.models.ISlugField(max_length=30, primary_key=True, serialize=False, unique=True)),
                ('title', models.CharField(blank=True, max_length=30)),
                ('private', models.BooleanField(default=False)),
                ('description', models.TextField(blank=True, default='The description has not been set yet.', max_length=600000)),
                ('slvl', models.IntegerField(default=0, verbose_name='security level')),
                ('debslvl', models.IntegerField(default=1, verbose_name='default debate security level')),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('edited_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='topics_created', to=settings.AUTH_USER_MODEL)),
                ('moderators', models.ManyToManyField(related_name='moderator_of', to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='topics_owned', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RevisionData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.GenericIPAddressField()),
                ('titchg', models.TextField(blank=True)),
                ('bodchg', models.TextField(blank=True)),
                ('modaction', models.BooleanField(default=False)),
                ('revision', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reversion.Revision')),
            ],
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rule', models.IntegerField(choices=[(0, 'Other'), (1, 'Content Policy - 1.1 - Illegal Content'), (2, 'Content Policy - 1.2 - Off-Topic Content'), (3, 'Content Policy - 1.3 - Spam'), (4, 'Content Policy - 1.4 - Personal Information'), (5, 'Content Policy - 1.5 - Harassment'), (6, 'Content Policy - 1.6 - Manipulates Emotions'), (7, 'Content Policy - 1.7 - Manipulates Biases Excl. Emotions'), (8, 'Content Policy - 1.8 - Duplicates Other Content'), (9, 'Content Policy - 2.1 - Argument Does Not Have Sufficient Evidence'), (10, 'Content Policy - 2.2 - Argument Does Not Contribute to Debate'), (11, 'Content Policy - 2.3 - Argument Includes Unnecessary Details'), (12, 'Content Policy - 3.1 - Debate Is Biased'), (13, 'Content Policy - 3.2 - Debate Does Not Have Useful Description'), (14, 'Content Policy - 3.3 - Debate About Personal Preferences'), (15, 'Content Policy - 4.1 - Topic Is Biased'), (16, 'Content Policy - 4.2 - Topic Has Inactive Mod Team'), (17, 'Content Policy - 4.3 - Topic Does Not Have Useful Description'), (18, 'Content Policy - 4.4 - Topic Does Not Have Public Channel'), (19, 'User Policy - 1.1 - User Is an Imposter'), (20, 'User Policy - 1.2 - User Abuses Debate Voting System'), (21, 'User Policy - 1.3 - User Removes Useful Content'), (22, 'User Policy - 1.4 - User Abuses or Hacks Website'), (23, 'User Policy - 1.5 - User Evades Ban'), (24, 'User Policy - 1.6 - User Offers Bribe'), (25, 'User Policy - 1.7 - User Submits False Reports'), (26, 'User Policy - 2.2 - Moderator Uses Punishment Not In Rules'), (27, 'User Policy - 2.3 - Moderator Accepts Bribes'), (28, 'User Policy - 2.7 - Moderator Improperly Uses Powers'), (29, 'User Policy - 2.8 - Moderator Does Not Leave Detailed Mod Notes'), (30, 'User Policy - 3.4 - Global Moderator Issues Unreasonably Long Suspension')], default=0, verbose_name='rule broken')),
                ('ip', models.GenericIPAddressField()),
                ('description', models.TextField(blank=True, max_length=50000)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('closed_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('status', models.IntegerField(default=0)),
                ('modnote', models.TextField(blank=True, max_length=200000, verbose_name='moderator note')),
                ('object_id', models.CharField(max_length=30)),
                ('content_type', models.ForeignKey(limit_choices_to=models.Q(models.Q(('app_label', 'debates'), ('model', 'topic')), models.Q(('app_label', 'debates'), ('model', 'debate')), models.Q(('app_label', 'debates'), ('model', 'argument')), models.Q(('app_label', 'accounts'), ('model', 'user')), _connector='OR'), on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Debate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slvl', models.IntegerField(default=1, verbose_name='security level')),
                ('approvalstatus', models.IntegerField(choices=[(0, 'Approved'), (1, 'Unapproved'), (2, 'Denied'), (3, 'Hidden')], default=1, verbose_name='approval status')),
                ('karma', models.IntegerField(default=0)),
                ('modnote', models.TextField(blank=True, max_length=200000, verbose_name='moderator note')),
                ('active', models.BooleanField(default=True)),
                ('question', models.CharField(max_length=300)),
                ('description', models.TextField(blank=True, max_length=200000)),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('edited_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('approved_on', models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='debates', to=settings.AUTH_USER_MODEL)),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='debates', to='debates.Topic')),
                ('users_downvoting', models.ManyToManyField(blank=True, related_name='debates_downvoted', to=settings.AUTH_USER_MODEL)),
                ('users_upvoting', models.ManyToManyField(blank=True, related_name='debates_upvoted', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Argument',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('approvalstatus', models.IntegerField(choices=[(0, 'Approved'), (1, 'Unapproved'), (2, 'Denied'), (3, 'Hidden')], default=1, verbose_name='approval status')),
                ('order', models.IntegerField(default=0)),
                ('side', models.IntegerField(choices=[(0, 'For'), (1, 'Against')], default=0)),
                ('active', models.BooleanField(default=True)),
                ('title', models.CharField(max_length=300)),
                ('body', models.TextField(max_length=200000)),
                ('modnote', models.TextField(blank=True, max_length=200000)),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('edited_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('debate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='arguments', to='debates.Debate')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='arguments', to=settings.AUTH_USER_MODEL)),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='arguments', to='debates.Topic')),
            ],
        ),
    ]