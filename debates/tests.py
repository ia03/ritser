from django.test import TestCase
from django.urls import resolve
from django.utils import timezone
from .models import Topic, Debate, Argument, RevisionData
from accounts.models import User
from django.contrib.auth import get_user_model
from .views import index, topic, debate
from .forms import DebateForm
from django.http import QueryDict
import os
import reversion

# Create your tests here.


class ViewTestCase (TestCase):
    def setUp(self):
        self.tmod = User.objects.create_user(
            username="mod", email="test@test.com", password="test123")
        self.tmod.save()
        self.test_topic = Topic.objects.create(
            name="test", private=False, owner=self.tmod, created_by=self.tmod)
        self.test_topic.moderators.set([self.tmod])
        self.test_topic.save()
        self.test_debate = Debate.objects.create(
            owner=self.tmod, topic=self.test_topic, question="Test debate")
        self.test_debate.save()
        self.test_argument = Argument.objects.create(
            owner=self.tmod,
            topic=self.test_topic,
            debate=self.test_debate,
            title='title',
            body='body')
        self.test_argument.save()
        self.test_argumenta = Argument.objects.create(
            owner=self.tmod,
            topic=self.test_topic,
            side=1,
            debate=self.test_debate,
            title='title',
            body='body')
        self.test_argumenta.save()

    def test_indexpage(self):
        found = resolve('/')
        self.assertEqual(found.func, index)

    def test_topicpage(self):
        found = resolve('/t/afw/')
        self.assertEqual(found.func, topic)

    def test_invalidtopic(self):
        response = self.client.get('/t/akvurov_u439j/')
        # checks to see if an invalid topic url will return a 404 (NOT FOUND)
        self.assertEqual(response.status_code, 404)

    def test_validtopic(self):
        response = self.client.get('/t/test/')
        # checks to see if a valid topic url will return a 200 (OK)
        self.assertEqual(response.status_code, 200)

    def test_topicnamepassed(self):
        response = self.client.get('/t/test/')
        # checks to see if a valid topic url will pass the topic name
        self.assertEqual(response.context['topic'].name, 'test')

    def test_debateslist(self):
        response = self.client.get('/t/test/')
        # checks to see if a valid topic url will pass the topic name
        self.assertEqual(response.context['debates'][0], self.test_debate)

    def test_debatepage(self):
        found = resolve('/t/test/%s/' % self.test_debate.id)
        self.assertEqual(found.func, debate)

    def test_debatepassed(self):
        response = self.client.get('/t/test/%s/' % self.test_debate.id)
        print(vars(response.context))
        self.assertEqual(response.context['debate'], self.test_debate)

    def test_argumentslist(self):
        response = self.client.get('/t/test/%s/' % self.test_debate.id)
        self.assertEqual(response.context['argumentsf'][0], self.test_argument)

    def test_argumentslista(self):
        response = self.client.get('/t/test/%s/' % self.test_debate.id)
        self.assertEqual(
            response.context['argumentsa'][0],
            self.test_argumenta)


class DebateFormTestCase (TestCase):
    def setUp(self):
        os.environ['RECAPTCHA_TESTING'] = 'True'
        self.tmod = User.objects.create_user(
            username="mod", email="test@test.com", password="test123")
        self.tmod.save()
        self.tuser = User.objects.create_user(
            username="user", email="test@test.com", password="test123")
        self.tuser.save()
        self.tuser2 = User.objects.create_user(
            username="user2", email="test2@test.com", password="test123")
        self.tuser2.save()
        self.tgmod = User.objects.create_user(
            username="gmod",
            email="gmod@test.com",
            password="test123",
            modstatus=1)
        self.test_topic = Topic.objects.create(
            name="test", private=False, owner=self.tmod, created_by=self.tmod)
        self.test_topic.moderators.set([self.tmod])
        self.test_topic.save()
        self.test_debate = Debate.objects.create(
            owner=self.tuser, topic=self.test_topic, question="Test debate")
        self.test_debate.save()

    def test_debateformadd(self):
        form_data = {
            'topic_name': self.test_topic.name,
            'question': 'testquestion1',
            'description': 'testdescription1',
            'g-recaptcha-response': 'PASSED',
        }
        self.test_topic.slvl = 1
        self.test_topic.save()
        self.tuser.approvedargs = 10
        self.tuser.save()
        form = DebateForm(data=form_data, user=self.tuser, edit=0)
        self.assertTrue(form.is_valid())

    def test_debateforminsaargs(self):
        form_data = {
            'topic_name': self.test_topic.name,
            'question': 'testquestion1',
            'description': 'testdescription1',
            'g-recaptcha-response': 'PASSED',
        }
        self.test_topic.slvl = 1
        self.test_topic.save()
        self.tuser.approvedargs = 0
        self.tuser.save()
        iform = DebateForm(data=form_data, user=self.tuser, edit=0)
        # assert that user does not have the required number of approved
        # arguments to post
        self.assertFalse(iform.is_valid())

    def test_debateedit(self):
        form_data = {
            'owner_name': self.tuser2.username,
            'question': 'testquestion1',
            'description': 'testdescription1',
            'g-recaptcha-response': 'PASSED',
        }
        debate = Debate.objects.create(
            question='test invalid debate edit',
            owner=self.tuser,
            topic=self.test_topic)
        form = DebateForm(form_data, instance=debate, user=self.tuser, edit=1)
        self.assertTrue(form.is_valid())

    def test_debateinvedit(self):
        form_data = {
            'owner_name': self.tuser.username,
            'question': 'testquestion1',
            'description': 'testdescription1',
            'g-recaptcha-response': 'PASSED',
        }
        debate = Debate.objects.create(
            question='test debate edit',
            owner=self.tuser2,
            topic=self.test_topic)
        form = DebateForm(form_data, instance=debate, user=self.tuser, edit=1)
        self.assertFalse(form.is_valid())

    def test_debatemodedit(self):
        form_data = {
            'owner_name': self.tuser.username,
            'question': 'testquestion1',
            'description': 'testdescription1',
            'g-recaptcha-response': 'PASSED',
        }
        debate = Debate.objects.create(
            question='test debate edit',
            owner=self.tuser2,
            topic=self.test_topic)
        form = DebateForm(form_data, instance=debate, user=self.tuser, edit=2)
        self.assertFalse(form.is_valid())

    def tearDown(self):
        os.environ['RECAPTCHA_TESTING'] = 'False'
