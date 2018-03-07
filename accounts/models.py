from django.db import models
from django.contrib.auth.models import AbstractUser
from debates.models import Debate

# Create your models here.
class User(AbstractUser):
	upvoted = models.ManyToManyField(Debate, related_name='users_upvoting')
