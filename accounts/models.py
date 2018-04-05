from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from timezone_field import TimeZoneField

# Create your models here.
class User(AbstractUser):
	approvedargs = models.IntegerField(default=0)
	modstatus = models.IntegerField(default=0) #0: regular user #1: global moderator #2: admin #3: owner
	active = models.IntegerField(default=0) #0: not banned 1: account deleted 2: temporarily banned 3: permanently banned
	bandate = models.DateField(blank=True, null=True)
	bannote = models.CharField(max_length=10000, blank=True)
	bio = models.TextField(max_length=200000, blank=True)
	stopics = models.ManyToManyField('debates.Topic', related_name='susers', blank=True)
	timezone = TimeZoneField(default='Europe/London')
	def get_absolute_url(self):
		if self.is_active:
			return reverse('user', args=[self.username])
		else:
			return '#'
	def get_username(self):
		if self.active == 0 or self.active == 2:
			return self.username
		else:
			return '[DELETED]'
	def get_debates(self):
		return reverse('userdebates', args=[self.username])
		
	def get_arguments(self):
		return reverse('userarguments', args=[self.username])
	def ismodof(self, topic):
		return (self.modstatus > 0) or (self.moderator_of.filter(name=topic.name)) or topic.owner == self
	def ismod(self):
		return self.moderator_of.all().exists() or self.modstatus > 0
	def isowner(self, topic):
		return self.modstatus > 0 or topic.owner == self
	def isgmod(self):
		return (self.modstatus > 0)
	def isadmin(self):
		return (self.modstatus > 1)
	def hasperm(self):
		return self.is_authenticated and self.active != 2
	def __str__(self):
		return self.username
