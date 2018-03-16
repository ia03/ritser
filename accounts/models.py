from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse

# Create your models here.
class User(AbstractUser):
	approvedargs = models.IntegerField(default=0)
	modstatus = models.IntegerField(default=0) #0: regular user #1: global moderator #2: admin #3: owner
	bandate = models.DateTimeField(blank=True, null=True)
	bannote = models.CharField(max_length=10000, blank=True)
	def get_absolute_url(self):
		return reverse('profile', args=[self.username])
	def ismod(self, topic):
		return (self.modstatus > 0) or (self.moderator_of.filter(name=topic.name))
	def isgmod(self):
		return (self.modstatus > 0)
	def isadmin(self):
		return (self.modstatus > 1)
	def __str__(self):
		return self.username
