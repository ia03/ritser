from django.test import TestCase
from django.utils import timezone
from .models import Debate

# Create your tests here.


class DebateTestCase (TestCase):
  def badmaths(self):
    self.assertEqual(1 + 1, 4)
