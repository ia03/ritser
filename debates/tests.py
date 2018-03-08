from django.test import TestCase
from django.urls import resolve
from django.utils import timezone
from .models import Topic
from accounts.models import User
from django.apps import apps
from .views import index, topic

# Create your tests here.

User = apps.get_model('accounts', 'User')

class ViewTestCase (TestCase):
    def setUp(self):
        tuser = User.objects.create_user(username="test", email="test@test.com", password="test123")
        tuser.save()
        test_topic = Topic.objects.create(name="test", private=False, owner=tuser, moderators=[tuser], created_by=[tuser])
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
