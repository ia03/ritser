from django.db import models
from django.contrib.postgres.fields import ArrayField
from accounts.models import User

# Create your models here.

class Topic(models.Model):
	name = models.CharField(max_length=30, unique=True)
	private = models.BooleanField(default=False)
	description = models.TextField(max_length=600000, default='The description has not been set yet.', blank=True)
	created_on = models.DateField(auto_now_add=True)
	created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='topics_created')
	owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='topics_owned')
	moderators = models.ManyToManyField(User, related_name='moderator_of')
	def __str__(self):
		return self.name


class Debate(models.Model):
	owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='debates_owned')
	topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='debates_contained')
	slvl = models.IntegerField(default="0")
	karma = models.IntegerField(default="0")
	users_upvoting = models.ManyToManyField(User, related_name='debates_upvoted')
	active = models.BooleanField(default=True)
	question = models.CharField(max_length=300)
	description = models.TextField(max_length=200000, blank=True)
	created_on = models.DateField(auto_now_add=True)
	def __str__(self):
		return self.question

class Argument(models.Model):
	owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='arguments_owned')
	topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='arguments_contained')
	debate = models.ForeignKey(Debate, on_delete=models.CASCADE, related_name='arguments_contained')
	approvedstatus = models.IntegerField(default=0)
	order = models.IntegerField(default="0")
	active = models.BooleanField(default=True)
	title = models.CharField(max_length=300)
	body = models.TextField(max_length=200000)
	created_on = models.DateField(auto_now_add=True)
	def __str__(self):
		return self.title

#Revisions:

class ArgumentRevision(models.Model):
	argument = models.ForeignKey(Argument, on_delete=models.CASCADE, related_name='revisions')
	title = models.CharField(max_length=300)
	body = models.TextField(max_length=200000)
	approvedstatus = models.IntegerField(default=0)
	order = models.IntegerField(default="0")
	datetime = models.DateField(auto_now_add=True)
	def __str__(self):
		return self.datetime


class DebateRevision(models.Model):
	debate = models.ForeignKey(Debate, on_delete=models.CASCADE, related_name='revisions')
	topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='debaterevisions_contained')
	slvl = models.IntegerField(default="0")
	question = models.CharField(max_length=300)
	description = models.TextField(max_length=200000, blank=True)
	datetime = models.DateField(auto_now_add=True)
	def __str__(self):
		return self.datetime


class TopicRevision(models.Model):
	topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='revisions')
	owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='topicrevisions_owned')
	moderators = models.ManyToManyField(User)
	description = models.TextField(max_length=600000, default='The description has not been set yet.', blank=True)
	private = models.BooleanField(default=False)
	datetime = models.DateField(auto_now_add=True)
	def __str__(self):
		return self.datetime
