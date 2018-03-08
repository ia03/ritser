from django.test import TestCase
from django.urls import resolve
from django.utils import timezone
from .models import Topic
from accounts.models import User
from .views import index, topic

# Create your tests here.

#todo: add setup that creates a "test" topic

class ViewTestCase (TestCase):
    user = User.objects.create_user(username="test", email="test@test.com", password="test123")
  def setUp(self):
    test_topic = Topic.objects.create(name="test", private=False, owner=user, moderators=[user], created_by=[user])
    test_topic.save()
  def test_indexpage(self):
    found = resolve('/')
    self.assertEqual(found.func, index)
  def test_topicpage(self):
    found = resolve('/t/afw')
    self.assertEqual(found.func, topic)
  def test_invalidtopic(self):
    response = self.client.get('t/akvurov_u439j')
    self.assertEqual(response.status_code, 404) #checks to see if an invalid topic url will return a 404 (NOT FOUND)
  def test_validtopic(self):
    response = self.client.get('t/test')
    self.assertEqual(response.status_code, 200) #checks to see if a valid topic url will return a 200 (OK)
  def test_topicnamepassed(self):
    response = self.client.get('t/test')
    self.assertEqual(response.context['topic'].name, 'test') #checks to see if a valid topic url will return a 200 (OK)
