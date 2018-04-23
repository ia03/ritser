from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.urls import reverse
from django.apps import apps
from timezone_field import TimeZoneField
from django.db.models import Q
from model_utils import Choices
import django
# Create your models here.

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
                'report') + '?type=5&id=' + self.get_username()

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

    def isowner(self, topic):
        return self.modstatus > 0 or topic.owner == self

    def isgmod(self):
        return (self.modstatus > 0)

    def isadmin(self):
        return (self.modstatus > 1)

    def hasperm(self):
        return self.is_authenticated and self.active != 2

    def get_approvedargs(self):
        return self.arguments.filter(approvalstatus=0).count()

    def unapprovedargslist(self):
        Argument = apps.get_model('debates.Argument')
        if self.isgmod():
            query = Argument.objects.filter(approvalstatus=1)
        else:
            query = Argument.objects.none()
            queries = Q()
            for topic in self.topics_owned.all():
                queries = queries | Q(topic=topic)
            for topic in self.moderator_of.all():
                queries = queries | Q(topic=topic)
            query = Argument.objects.filter(queries & Q(approvalstatus=1))
        return query

    def unapprovedarguments(self):
        return (self.unapprovedargslist()
                .order_by('-owner__approvedargs', 'created_on'))

    def unapproveddebslist(self):
        Debate = apps.get_model('debates.Debate')
        if self.isgmod():
            query = Debate.objects.filter(approvalstatus=1)
        else:
            query = Debate.objects.none()
            queries = Q()
            for topic in self.topics_owned.all():
                queries = queries | Q(topic=topic)
            for topic in self.moderator_of.all():
                queries = queries | Q(topic=topic)
            query = Debate.objects.filter(queries & Q(approvalstatus=1))
        return query

    def unapproveddebates(self):
        return (self.unapproveddebslist()
                .order_by('-owner__approvedargs', '-created_on'))

    def dcount(self):
        return self.debates.filter(~Q(approvalstatus=3)).count()
    
    def acount(self):
        return self.arguments.filter(~Q(approvalstatus=3)).count()

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