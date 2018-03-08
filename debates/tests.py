from django.test import TestCase
from django.urls import resolve
from django.utils import timezone
from .models import Debate
from .views import index, topic

# Create your tests here.


class ViewTestCase (TestCase):
  def test_indexpage(self):
    found = resolve('/')
    self.assertEqual(found.func, index)
  def test_topicpage(self):
    found = resolve('/t/afw')
    self.assertEqual(found.func, topic)
