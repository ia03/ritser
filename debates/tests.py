from django.test import TestCase
from django.urls import resolve
from django.utils import timezone
from .models import Topic, Debate
from accounts.models import User
from django.contrib.auth import get_user_model
from .views import index, topic
from .forms import DebateForm

# Create your tests here.

class ViewTestCase (TestCase):
    def setUp(self):
        tmod = User.objects.create_user(username="mod", email="test@test.com", password="test123")
        tmod.save()
        tuser = User.objects.create_user(username="user", email="test@test.com", password="test123")
        tuser.save()
        tuser2 = User.objects.create_user(username="user2", email="test2@test.com", password="test123")
        tuser2.save()
        tgmod = User.objects.create_user(username="gmod", email="gmod@test.com", password="test123", modstatus=1)
        test_topic = Topic.objects.create(name="test", private=False, owner=tmod, created_by=tmod)
        test_topic.moderators.set([tmod])
        test_topic.save()
        test_debate = Debate.objects.create(owner=tuser, topic=test_topic, question="Test debate")
        test_debate.save()

    def test_indexpage(self):
        found = resolve('/')
        self.assertEqual(found.func, index)
    def test_topicpage(self):
        found = resolve('/t/afw/')
        self.assertEqual(found.func, topic)
        response = self.client.get('/t/akvurov_u439j/')
        self.assertEqual(response.status_code, 404) #checks to see if an invalid topic url will return a 404 (NOT FOUND)
        response = self.client.get('/t/test/')
        self.assertEqual(response.status_code, 200) #checks to see if a valid topic url will return a 200 (OK)
        response = self.client.get('/t/test/')
        self.assertEqual(response.context['topic'].name, 'test') #checks to see if a valid topic url will pass the topic name
    def test_debateform(self):
        form_data = {
            'topic_name': test_topic.name,
            'question': 'testquestion1',
            'description': 'testdescription1',
        }
        form = DebateForm(data=form_data, user=tuser, edit=0)
        self.assertTrue(form.is_valid())
        

#todo: test debates page with wrong topic arg in url and see if it returns a 404
