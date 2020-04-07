from django.db import models
from django.contrib.contenttypes.fields import (
    GenericForeignKey, GenericRelation)
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField
from django.utils.text import slugify
from django.utils import timezone
from django.urls import reverse
from accounts.models import User
import reversion
from reversion.models import Revision
from model_utils import Choices


# Create your models here.

class ISlugField(models.SlugField):
    def db_type(self, connection):
        return 'citext'


apprsc = Choices(
    (0, 'approved', 'Approved'),
    (1, 'unapproved', 'Unapproved'),
    (2, 'denied', 'Denied'),
    (3, 'hidden', 'Hidden'),
    )
sides = Choices(
    (0, 'fo', 'For'),
    (1, 'ag', 'Against'),
    )
rules = Choices(
    (0, 'other', 'Other'),
    (1, 'cillegal', 'Content Policy - 1.1 - Illegal Content'),
    (2, 'cofftopic', 'Content Policy - 1.2 - Off-Topic Content'),
    (3, 'cspam', 'Content Policy - 1.3 - Spam'),
    (4, 'cpinfo', 'Content Policy - 1.4 - Personal Information'),
    (5, 'charassment', 'Content Policy - 1.5 - Harassment'),
    (6, 'cemomani', 'Content Policy - 1.6 - Manipulates Emotions'),
    (7, 'cbiamani', 'Content Policy - 1.7 - Manipulates Biases Excl. Emotions'),
    (8, 'cduplicate', 'Content Policy - 1.8 - Duplicates Other Content'),
    (9, 'caievidence', 'Content Policy - 2.1 - Argument Does Not Have Sufficient Evidence'),
    (10, 'cacontrib', 'Content Policy - 2.2 - Argument Does Not Contribute to Debate'),
    (11, 'caunnecessary', 'Content Policy - 2.3 - Argument Includes Unnecessary Details'),
    (12, 'cdbiased', 'Content Policy - 3.1 - Debate Is Biased'),
    (13, 'cduselessdes', 'Content Policy - 3.2 - Debate Does Not Have Useful Description'),
    (14, 'cdpersprefs', 'Content Policy - 3.3 - Debate About Personal Preferences'),
    (15, 'ctbiased', 'Content Policy - 4.1 - Topic Is Biased'),
    (16, 'ctinactive', 'Content Policy - 4.2 - Topic Has Inactive Mod Team'),
    (17, 'ctuselessdes', 'Content Policy - 4.3 - Topic Does Not Have Useful Description'),
    (18, 'ctnopubch', 'Content Policy - 4.4 - Topic Does Not Have Public Channel'),
    (19, 'uuimpersonates', 'User Policy - 1.1 - User Is an Imposter'),
    (20, 'uuabusevote', 'User Policy - 1.2 - User Abuses Debate Voting System'),
    (21, 'uuremovecont', 'User Policy - 1.3 - User Removes Useful Content'),
    (22, 'uuabuse', 'User Policy - 1.4 - User Abuses or Hacks Website'),
    (23, 'uuevade', 'User Policy - 1.5 - User Evades Ban'),
    (24, 'uubribe', 'User Policy - 1.6 - User Offers Bribe'),
    (25, 'uufreport', 'User Policy - 1.7 - User Submits False Reports'),
    (26, 'umipunish', 'User Policy - 2.2 - Moderator Uses Punishment Not In Rules'),
    (27, 'umaccbribe', 'User Policy - 2.3 - Moderator Accepts Bribes'),
    (28, 'umiaction', 'User Policy - 2.7 - Moderator Improperly Uses Powers'),
    (29, 'uminote', 'User Policy - 2.8 - Moderator Does Not Leave Detailed Mod Notes'),
    (30, 'uglongsusp', 'User Policy - 3.4 - Global Moderator Issues Unreasonably Long Suspension'),
    )


class Report(models.Model):
    rule = models.IntegerField(
        default=rules.other,
        choices=rules,
        verbose_name='rule broken',
        )
    ip = models.GenericIPAddressField()
    description = models.TextField(
        max_length=50000,
        blank=True)
    date = models.DateTimeField(default=timezone.now)
    closed_on = models.DateTimeField(default=timezone.now)
    # 0: open, 1: closed; action taken, 2: closed; no action taken
    status = models.IntegerField(default=0)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reports',
        )
    modnote = models.TextField(
        max_length=200000,
        blank=True,
        verbose_name='moderator note')
    limit = models.Q(app_label='debates', model='topic') | models.Q(
        app_label='debates', model='debate') | models.Q(
            app_label='debates', model='argument') | models.Q(
                app_label='accounts', model='user')
    # mandatory fields for generic relation
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to=limit)
    object_id = models.CharField(max_length=30)
    content_object = GenericForeignKey()
    
    def get_absolute_url(self):
        return reverse('report', args=[self.id])
    
    def __str__(self):
        return str(self.content_object)

@reversion.register()
class Topic(models.Model):
    name = ISlugField(
        primary_key=True,
        max_length=30,
        unique=True)
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
    slvl = models.IntegerField(
        default=0,
        verbose_name='security level')
    debslvl = models.IntegerField(
        default=1,
        verbose_name='default debate security level')
    moderators = models.ManyToManyField(User, related_name='moderator_of')
    created_on = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='topics_created')
    edited_on = models.DateTimeField(default=timezone.now)
    reports = GenericRelation(Report, related_query_name='topic')

    def get_absolute_url(self):
        return reverse('topic', args=[self.name])

    def get_info_url(self):
        return reverse('topicinfo', args=[self.name])

    def get_edit_url(self):
        return reverse(
            'edittopic',
            args=[self.name])
    
    def get_edits_url(self):
        return reverse(
            'topicedits',
            args=[
                self.name])

    def get_submit_url(self):
        return reverse(
            'submitdebate') + '?topic=' + self.name

    def get_report_url(self):
        return reverse(
            'submitreport') + '?type=4&id=' + self.name

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
    slvl = models.IntegerField(default=1, verbose_name='security level')
    # 0: approved 1: unapproved 2: denied 3: deleted
    approvalstatus = models.IntegerField(
        default=apprsc.unapproved,
        choices=apprsc,
        verbose_name='approval status')
    karma = models.IntegerField(default=0)
    users_upvoting = models.ManyToManyField(
        User, related_name='debates_upvoted', blank=True)
    users_downvoting = models.ManyToManyField(
        User, related_name='debates_downvoted', blank=True)
    modnote = models.TextField(
        max_length=200000,
        blank=True,
        verbose_name='moderator note')
    active = models.BooleanField(default=True)
    question = models.CharField(max_length=300)
    description = models.TextField(max_length=200000, blank=True)
    created_on = models.DateTimeField(default=timezone.now)
    edited_on = models.DateTimeField(default=timezone.now)
    approved_on = models.DateTimeField(
        default=timezone.now,
        blank=True,
        null=True)
    reports = GenericRelation(Report, related_query_name='debate')

    def numapproved(self):
        return self.arguments.filter(approvalstatus=0).count()

    def numunapproved(self):
        return self.arguments.filter(approvalstatus=1).count()

    def numdenied(self):
        return self.arguments.filter(approvalstatus=2).count()

    def get_absolute_url(self):
        return reverse('debate', args=[
            self.topic.name,
            self.id,
            self.slugify()])

    def get_edit_url(self):
        return reverse(
            'editdebate',
            args=[
                self.topic_id,
                self.id,
                self.slugify()])
                
    def get_edits_url(self):
        return reverse(
            'debateedits',
            args=[
                self.topic_id,
                self.id,
                self.slugify()])

    def get_submit_url(self):
        return reverse(
            'submitargument') + '?debate=' + str(self.id)

    def get_report_url(self):
        return reverse(
            'submitreport') + '?type=2&id=' + str(self.id)

    def slugify(self):
        return slugify(self.question)

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
    approvalstatus = models.IntegerField(
        default=apprsc.unapproved,
        choices=apprsc, 
        verbose_name='approval status')
    order = models.IntegerField(
        default=0)  # owner.approvedargs?
    side = models.IntegerField(
        default=sides.fo,
        choices=sides)  # 0: for 1: against
    active = models.BooleanField(default=True)
    title = models.CharField(max_length=300)
    body = models.TextField(max_length=200000)
    modnote = models.TextField(max_length=200000, blank=True)
    created_on = models.DateTimeField(default=timezone.now)
    edited_on = models.DateTimeField(default=timezone.now)
    reports = GenericRelation(Report, related_query_name='argument')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.owner.approvedargs = self.owner.get_approvedargs()

    def get_absolute_url(self):
        return reverse(
            'argument',
            args=[
                self.topic_id,
                self.debate_id,
                self.debate.slugify(),
                self.id,
                self.slugify()])

    def get_edit_url(self):
        return reverse(
            'editargument',
            args=[
                self.topic_id,
                self.debate_id,
                self.debate.slugify(),
                self.id,
                self.slugify()])
                
    def get_edits_url(self):
        return reverse(
            'argumentedits',
            args=[
                self.topic_id,
                self.debate_id,
                self.debate.slugify(),
                self.id,
                self.slugify()])

    def get_report_url(self):
        return reverse(
            'submitreport') + '?type=1&id=' + str(self.id)

    def slugify(self):
        return slugify(self.title)

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
    modaction = models.BooleanField(default=False)
