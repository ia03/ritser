from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone
from django.urls import reverse
from accounts.models import User
import reversion
from reversion.models import Revision

# Create your models here.


@reversion.register()
class Topic(models.Model):
    name = models.SlugField(
        primary_key=True,
        max_length=30,
        unique=True,
        db_index=True)
    # to be displayed in the HTML title of the topic
    title = models.CharField(max_length=30, blank=True)
    private = models.BooleanField(default=False)
    description = models.TextField(
        max_length=600000,
        default='The description has not been set yet.',
        blank=True)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='topics_owned')
    # 0: All users can submit debates. 1: Users with at least 10 approved
    # arguments can submit debates. 2: Users with at least 10 approved
    # arguments can submit a debate request 3: Only moderators can submit
    # debates.
    slvl = models.IntegerField(default=0)
    debslvl = models.IntegerField(default=1)
    moderators = models.ManyToManyField(User, related_name='moderator_of')
    created_on = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='topics_created')
    edited_on = models.DateTimeField(default=timezone.now)

    def get_absolute_url(self):
        return reverse('topic', args=[self.name])

    def __str__(self):
        return self.name


@reversion.register()
class Debate(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='debates')
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name='debates')
    # if slvl = 0, approved, unapproved, denied arguments visible by def. if
    # slvl = 1 or 2(20+ approved args), approved and unapproved visible by
    # def., slvl=3 means only approved args visible(20+ approved args), slvl=4
    # means mod submissions only
    slvl = models.IntegerField(default=1)
    # 0: approved 1: unapproved 2: denied 3: deleted
    approvalstatus = models.IntegerField(default=1)
    karma = models.IntegerField(default=0, db_index=True)
    users_upvoting = models.ManyToManyField(
        User, related_name='debates_upvoted', blank=True)
    users_downvoting = models.ManyToManyField(
        User, related_name='debates_downvoted', blank=True)
    modnote = models.TextField(max_length=200000, blank=True)
    active = models.BooleanField(default=True)
    question = models.CharField(max_length=300)
    description = models.TextField(max_length=200000, blank=True)
    created_on = models.DateTimeField(default=timezone.now, db_index=True)
    edited_on = models.DateTimeField(default=timezone.now)
    approved_on = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        blank=True,
        null=True)

    def numapproved(self):
        return self.arguments.filter(approvalstatus=0).count()

    def numunapproved(self):
        return self.arguments.filter(approvalstatus=1).count()

    def numdenied(self):
        return self.arguments.filter(approvalstatus=2).count()

    def get_absolute_url(self):
        return reverse('debate', args=[self.topic.name, self.id])

    def __str__(self):
        return self.question


@reversion.register()
class Argument(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='arguments')
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name='arguments')
    debate = models.ForeignKey(
        Debate,
        on_delete=models.CASCADE,
        related_name='arguments')
    # 0: approved 1: unapproved 2: denied 3: deleted
    approvalstatus = models.IntegerField(default=1, db_index=True)
    order = models.IntegerField(
        default=0, db_index=True)  # owner.approvedargs?
    side = models.IntegerField(default=0)  # 0: for 1: against
    active = models.BooleanField(default=True)
    title = models.CharField(max_length=300)
    body = models.TextField(max_length=200000)
    modnote = models.TextField(max_length=200000, blank=True)
    created_on = models.DateTimeField(default=timezone.now)
    edited_on = models.DateTimeField(default=timezone.now)

    def get_absolute_url(self):
        return reverse(
            'argument',
            args=[
                self.topic.name,
                self.debate_id,
                self.id])

    def __str__(self):
        return self.title

# Revisions:


class RevisionData(models.Model):
    revision = models.ForeignKey(
        reversion.models.Revision,
        on_delete=models.CASCADE)
    ip = models.GenericIPAddressField()
    titchg = models.TextField(blank=True)
    bodchg = models.TextField(blank=True)
