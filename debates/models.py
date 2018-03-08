from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone
from accounts.models import User

# Create your models here.

class Topic(models.Model):
	name = models.CharField(max_length=30, unique=True)
	title = models.CharField(max_length=30, blank=True) #to be displayed in the HTML title of the topic; should also be protected from xss attacks
	private = models.BooleanField(default=False)
	description = models.TextField(max_length=600000, default='The description has not been set yet.', blank=True)
	owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='topics_owned')
	slvl = models.IntegerField(default='0')
	debslvl = models.IntegerField(default='0')
	moderators = models.ManyToManyField(User, related_name='moderator_of')
	created_on = models.DateTimeField(default=timezone.now)
	created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='topics_created')
	edited_on = models.DateTimeField(default=timezone.now)
	def __str__(self):
		return self.name


class Debate(models.Model):
	owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='debates_owned')
	topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='debates')
	slvl = models.IntegerField(default='0')
	approvedstatus = models.IntegerField(default='0')
	karma = models.IntegerField(default='0')
	users_upvoting = models.ManyToManyField(User, related_name='debates_upvoted')
	active = models.BooleanField(default=True)
	question = models.CharField(max_length=300)
	description = models.TextField(max_length=200000, blank=True)
	created_on = models.DateTimeField(default=timezone.now)
	edited_on = models.DateTimeField(default=timezone.now)
	def __str__(self):
		return self.question

class Argument(models.Model):
	owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='arguments_owned')
	topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='arguments')
	debate = models.ForeignKey(Debate, on_delete=models.CASCADE, related_name='arguments')
	approvedstatus = models.IntegerField(default=0)
	order = models.IntegerField(default='0')
	active = models.BooleanField(default=True)
	title = models.CharField(max_length=300)
	body = models.TextField(max_length=200000)
	created_on = models.DateTimeField(default=timezone.now)
	edited_on = models.DateTimeField(default=timezone.now)
	def __str__(self):
		return self.title

#Revisions:

class ArgumentRevision(models.Model):
	argument = models.ForeignKey(Argument, on_delete=models.CASCADE, related_name='revisions')
	title = models.CharField(max_length=300)
	body = models.TextField(max_length=200000)
	approvedstatus = models.IntegerField(default=0)
	order = models.IntegerField(default='0')
	datetime = models.DateTimeField(default=timezone.now)
	ip = models.CharField(max_length=45, blank=True)
	def __str__(self):
		return self.datetime


class DebateRevision(models.Model):
	debate = models.ForeignKey(Debate, on_delete=models.CASCADE, related_name='revisions')
	topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='debaterevisions')
	slvl = models.IntegerField(default='0')
	question = models.CharField(max_length=300)
	description = models.TextField(max_length=200000, blank=True)
	datetime = models.DateTimeField(default=timezone.now)
	ip = models.CharField(max_length=45, blank=True)
	def __str__(self):
		return self.datetime


class TopicRevision(models.Model):
	topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='revisions')
	owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='topicrevisions_owned')
	moderators = models.ManyToManyField(User)
	description = models.TextField(max_length=600000, default='The description has not been set yet.', blank=True)
	private = models.BooleanField(default=False)
	datetime = models.DateTimeField(default=timezone.now)
	ip = models.CharField(max_length=45, blank=True)
	def __str__(self):
		return self.datetime
