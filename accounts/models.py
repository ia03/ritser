from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
# Create your models here.
class User(AbstractUser):
	approvedargs = models.IntegerField(default='0')
	def get_absolute_url(self):
		return reverse('profile', args=[self.username])
	def __str__(self):
		return self.title
