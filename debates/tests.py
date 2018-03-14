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
        self.tmod = User.objects.create_user(username="mod", email="test@test.com", password="test123")
        self.tmod.save()
        self.tuser = User.objects.create_user(username="user", email="test@test.com", password="test123")
        self.tuser.save()
        self.tuser2 = User.objects.create_user(username="user2", email="test2@test.com", password="test123")
        self.tuser2.save()
        self.tgmod = User.objects.create_user(username="gmod", email="gmod@test.com", password="test123", modstatus=1)
        self.test_topic = Topic.objects.create(name="test", private=False, owner=self.tmod, created_by=self.tmod)
        self.test_topic.moderators.set([self.tmod])
        self.test_topic.save()
        self.test_debate = Debate.objects.create(owner=self.tuser, topic=self.test_topic, question="Test debate")
        self.test_debate.save()

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
        self.test_topic.slvl = 1
        self.test_topic.save()
        form_data = {
            'topic_name': self.test_topic.name,
            'question': 'testquestion1',
            'description': 'testdescription1',
        }
        iform = DebateForm(data=form_data, user=self.tuser, edit=0)
        self.assertFalse(iform.is_valid()) #assert that user does not have the required number of approved arguments to post
        self.tuser.approvedargs = 10
        self.tuser.save()
        form = DebateForm(data=form_data, user=self.tuser, edit=0)
        self.assertTrue(form.is_valid())
        debate = form.save()
        form_data = {
            'question': 'testquestion1',
            'description': 'testdescription1',
        }
        eform = DebateForm(instance=debate, user=self.tuser2, edit=1) #assert that user does not have perm. to edit it
        self.assertFalse(eform.is_valid())
        eform2 = DebateForm(instance=debate, user=self.tuser, edit=1) #assert that user does have perm. to edit it
        self.assertTrue(eform2.is_valid())
        debate = eform2.save()
        eform3 = DebateForm(instance=debate, user=self.tmod, edit=2) #asserting that mod has perm to edit it
        self.assertTrue(eform3.is_valid())
        eform3 = DebateForm(instance=debate, user=self.tgmod, edit=2) #asserting that gmod has perm to edit it
        self.assertTrue(eform3.is_valid())
        
#todo: test debates page with wrong topic arg in url and see if it returns a 404
