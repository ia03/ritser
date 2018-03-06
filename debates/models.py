from django.db import models
from django.contrib.postgres.fields import ArrayField
from tinymce.models import HTMLField
from accounts.models import User

# Create your models here.

class Topic(models.Model):
	name = models.CharField(max_length=30)
	private = models.BooleanField(default=False)
	description = models.HTMLField(max_length=600000)
	created_on = models.DateField(auto_now_add=True)
	created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='topics_created')
	owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='topics_owned')
	moderators = models.ManyToManyField(User)
	def __str__(self):
		return self.name


class Debate(models.Model):
	owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='debates_owned')
	topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='debates_contained')
	question = models.CharField(max_length=300)
	description = models.HTMLField(max_length=200000)
	def __str__(self):
		return self.question

class Argument(models.Model):
	owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='arguments_owned')
	topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='arguments_contained')
	debate = models.ForeignKey(Debate, on_delete=models.CASCADE, related_name='arguments_contained')
	title = models.CharField(max_length=300)
	body = models.HTMLField(max_length=200000)
	def __str__(self):
		return self.title