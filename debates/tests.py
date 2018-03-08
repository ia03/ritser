from django.test import TestCase
from django.utils import timezone
from .models import Debate

# Create your tests here.


class DebateTestCase (TestCase):
  def test_badmaths(self):
    self.assertEqual(1 + 1, 4)
