from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.urls import reverse
from django.apps import apps
from django.http import Http404
from timezone_field import TimeZoneField
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from django.db.models import Q
from model_utils import Choices
from django.db.models.signals import post_save
import django
# Create your models here.

modrules = [
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
    13,
    14,
    ]

class User(AbstractUser):
    modschoices = Choices(
    (0, 'normal', 'Normal'),
    (1, 'gmod', 'Global Moderator'),
    (2, 'admin', 'Admin'),
    (3, 'owner', 'Owner'))
    approvedargs = models.IntegerField(default=0)
    # 0: regular user #1: global moderator #2: admin #3: owner
    modstatus = models.IntegerField(
        default=modschoices.normal,
        choices=modschoices,
        verbose_name='moderator status')
    # 0: not banned 1: account deleted 2: temporarily banned 3: permanently
    # banned
    active = models.IntegerField(default=0)
    bandate = models.DateField(default=timezone.now)
    bannote = models.CharField(max_length=10000, blank=True)
    bio = models.TextField(max_length=200000, blank=True)
    stopics = models.ManyToManyField(
        'debates.Topic',
        related_name='susers',
        blank=True)
    savedd = models.ManyToManyField(
        'debates.Debate',
        related_name='usaved',
        blank=True,
        through='SavedDebate')
    saveda = models.ManyToManyField(
        'debates.Argument',
        related_name='usaved',
        blank=True,
        through='SavedArgument')
    timezone = TimeZoneField(default='Europe/London')
    reports = GenericRelation('debates.Report', related_query_name='ruser')

    def get_absolute_url(self):  # modlogs bypasses this
        if self.is_active:
            return reverse('user', args=[self.username])
        else:
            return '#'

    def get_abs_url_mod(self):
        return reverse('user', args=[self.username])

    def get_modstatus_url(self):
        return reverse('usermodstatus', args=[self.get_username()])

    def get_report_url(self):
        if not self.is_active:
            return '#'
        else:
            return reverse(
                'submitreport') + ('?type=' +
                str(ContentType.objects.get_for_model(User).id) + '&id=' +
                str(self.get_username()))

    def get_ban_url(self):
        return reverse('ban') + '?user=' + self.username

    def get_username(self):  # modlogs bypasses this
        if self.active == 0 or self.active == 2:
            return self.username
        else:
            return '[DELETED]'

    def get_debates(self):
        return reverse('userdebates', args=[self.username])

    def get_arguments(self):
        return reverse('userarguments', args=[self.username])

    def ismodof(self, topic):
        return (
            self.isgmod()) or (
            self.moderator_of.filter(
                name=topic.name)) or topic.owner == self

    def ismod(self):
        return self.moderator_of.all().exists() or self.topics_owned.all().exists() or self.modstatus > 0

    def isowner(self, *args):
        if len(args) > 0:
            topic = args[0]
            return self.modstatus > 0 or topic.owner == self
        else:
            return (self.modstatus > 2)

    def isgmod(self):
        return (self.modstatus > 0)

    def isadmin(self):
        return (self.modstatus > 1)

    def hasperm(self):
        return self.is_authenticated and self.active != 2

    def topics(self):
        return self.topics_owned.all().union(
            self.moderator_of.all())

    def intopics(self):
        queries = Q()
        for topic in self.topics():
            queries = queries | Q(topic=topic)
        return queries

    def arintopics(self):
        Report = apps.get_model('debates.Report')
        query = Report.objects.none()
        for topic in self.topics().prefetch_related('arguments'):
            for argument in topic.arguments.all():
                query = query.union(argument.reports.filter(status=0))
        return query

    def drintopics(self):
        Report = apps.get_model('debates.Report')
        query = Report.objects.none()
        for topic in self.topics().prefetch_related('debates'):
            for debate in topic.debates.all():
                query = query.union(debate.reports.filter(status=0))
        return query


    def get_approvedargs(self):
        return self.arguments.filter(approvalstatus=0).count()

    def unapprovedargslist(self):
        Argument = apps.get_model('debates.Argument')

        query = Argument.objects.filter(approvalstatus=1)
        if not self.isgmod():
            query = query.filter(self.intopics())
        return query

    def unapprovedarguments(self):
        return (self.unapprovedargslist()
                .order_by('-owner__approvedargs', 'created_on'))

    def unapproveddebslist(self):
        Debate = apps.get_model('debates.Debate')
        query = Debate.objects.filter(approvalstatus=1)
        if not self.isgmod():
            query = query.filter(self.intopics())
        return query

    def unapproveddebates(self):
        return (self.unapproveddebslist()
                .order_by('-owner__approvedargs', '-created_on'))

    def argreportslist(self):
        if self.isgmod():
            Report = apps.get_model('debates.Report')
            ct = ContentType.objects.get_for_model(
                apps.get_model('debates.Argument'))
            query = Report.objects.filter(
                status=0,
                content_type=ct)
        else:
            query = self.arintopics()
        return query

    def argreports(self):
        return (self.argreportslist().order_by(
            'date'))

    def debreportslist(self):
        if self.isgmod():
            Report = apps.get_model('debates.Report')
            ct = ContentType.objects.get_for_model(
                apps.get_model('debates.Debate'))
            query = Report.objects.filter(
                status=0,
                content_type=ct,)
        else:
            query = self.drintopics()
        return query

    def debreports(self):
        return (self.debreportslist().order_by(
            'date'))

    def topicreportslist(self):
        Report = apps.get_model('debates.Report')
        if not self.isgmod():
            return Report.objects.none()
        ct = ContentType.objects.get_for_model(
            apps.get_model('debates.Topic'))

        query = Report.objects.filter(
            status=0,
            content_type=ct)

        return query

    def topicreports(self):
        return (self.topicreportslist().order_by(
            'date'))

    def userreportslist(self):
        Report = apps.get_model('debates.Report')
        if not self.isgmod():
            return Report.objects.none()
        ct = ContentType.objects.get_for_model(
            apps.get_model('accounts.User'))

        query = Report.objects.filter(
            status=0,
            content_type=ct)

        if not self.isadmin():
            query = query.filter(
                ruser__modstatus=0)
        elif not self.isowner():
            query = query.exclude(
                object_id=self.id)
        return query

    def userreports(self):
        return (self.userreportslist().order_by(
            'date'))

    def dcount(self):
        return self.debates.filter(~Q(approvalstatus=3)).count()

    def acount(self):
        return self.arguments.filter(~Q(approvalstatus=3)).count()

    def report(self, rid):
        Report = apps.get_model('debates.Report')
        notfoundmsg = 'Report not found or you do not have permission to view it.'
        notfoundex = Http404(notfoundmsg)
        try:
            report = Report.objects.get(id=rid)
        except Report.DoesNotExist:
            raise notfoundex
        reported = report.content_object
        ctype = report.content_type.model
        if not self.isgmod():
            # If user is not a gmod and report is not arg/deb or
            # report is not in a topic moderated by them, raise 404
            if (not (ctype == 'argument' or ctype == 'debate')) or (
                reported.topic not in self.topics()):
                    raise notfoundex
        else:
            if ctype == 'user' and not self.isowner():
                if self.isadmin() and reported == self:
                    raise notfoundex
                elif reported.isgmod() and not self.isadmin():
                    raise notfoundex
        return report
    def __str__(self):
        return self.username

class ModAction(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='modlogs')
    mod = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='modactions')
    # 0: suspend 1: unsuspend 2: terminate 3: del. arg 4: del. debate
    # 5: mov. debate 6: mov. topic
    action = models.IntegerField(default=0)
    pid = models.CharField(max_length=150, blank=True)
    pid2 = models.CharField(max_length=150, blank=True)
    modnote = models.CharField(max_length=10000, blank=True)
    date = models.DateTimeField(default=timezone.now)
    until = models.DateField(default=timezone.now, null=True, blank=True)

    class Meta:
        ordering = ['-date']

class SavedDebate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    debate = models.ForeignKey('debates.Debate', on_delete=models.CASCADE)
    added_on = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-added_on']

class SavedArgument(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    argument = models.ForeignKey('debates.Argument', on_delete=models.CASCADE)
    added_on = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-added_on']

def get_default_topics():
    return apps.get_model('debates.Topic').objects.filter(is_default=True)


def set_default_topics(**kwargs):
    if kwargs.get('created'):
        instance = kwargs.get('instance')

        instance.stopics.set(apps.get_model('debates.Topic').objects.filter(
            is_default=True))

post_save.connect(set_default_topics, User)
