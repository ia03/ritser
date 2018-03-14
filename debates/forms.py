from django import forms
from .models import Debate, Topic
from accounts.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

class DebateForm(forms.ModelForm):
    topic_name = forms.CharField(max_length=30)
    owner_name = forms.CharField(max_length=30)
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        if 'edit' in kwargs:
            self.edit = kwargs.pop("edit")
        else:
            self.edit = 0
        super(DebateForm, self).__init__(*args, **kwargs)
        self.fields['owner'].required = False
        self.fields['topic'].required = False
        self.fields['question'].max_length = Debate._meta.get_field('question').max_length
        self.fields['created_on'].required = False
        self.fields['edited_on'].required = False
        self.fields['approved_on'].required = False
        self.fields['approvalstatus'].label = 'Approval Status'
        self.fields['slvl'].label = 'Security Level'
        self.fields['question'].error_messages = {'required': 'You must type in a question.'}
        self.fields['topic_name'].error_messages = {'required': 'You must specify the name of the topic the debate belongs in.'}
        self.fields['owner_name'].error_messages = {'required': 'You must specify the name of the user who will own the debate.'}
        if self.edit == 0:
            self.fields['slvl'].required = False
            self.fields['slvl'].widget = forms.HiddenInput()
            self.fields['owner_name'].required = False
            self.fields['owner_name'].widget = forms.HiddenInput()
            self.fields['approvalstatus'].required = False
            self.fields['approvalstatus'].widget = forms.HiddenInput()
        elif self.edit == 1:
            self.fields['slvl'].required = False
            self.fields['slvl'].widget = forms.HiddenInput()
            self.fields['topic_name'].required = False
            self.fields['topic_name'].widget = forms.HiddenInput()
            self.fields['approvalstatus'].required = False
            self.fields['approvalstatus'].widget = forms.HiddenInput()
            self.fields['owner_name'].initial = self.instance.owner.username
        else:
            self.fields['slvl'].error_messages = {'required': 'You must specify a security level for the debate.'}
            self.fields['approvalstatus'].error_messages = {'required': 'You must specify the approval status for the debate.'}
            self.fields['topic_name'].initial = self.instance.topic.name

    def clean_topic_name(self):
        data = self.cleaned_data['topic_name']
        if self.edit != 1:
            try:
                a = Topic.objects.get(name=data)
            except ObjectDoesNotExist:
                raise forms.ValidationError('Topic %(topic_name)s not found.', code='topicnotfound', params={'topic_name': data})
        return data
    def clean_topic(self):
        if self.edit == 1:
            return self.instance.topic
        else:
            return self.cleaned_data.get('topic')
    def clean_owner_name(self):
        data = self.cleaned_data['owner_name']
        if self.edit != 0:
            try:
                a = User.objects.get(username=data)
            except ObjectDoesNotExist:
                raise forms.ValidationError('User %(owner_name)s not found.', code='usernotfound', params={'owner_name': data})
        return data
    def clean_owner(self):
        if self.edit == 0:
            return self.user
        else:
            return self.cleaned_data.get('owner')
    def clean_created_on(self):
        if self.edit == 0:
            return timezone.now()
        else:
            return self.instance.created_on
    def clean_edited_on(self):
        return timezone.now()
    def clean_approvalstatus(self):
        if self.edit == 0:
            return 1
        elif self.edit == 1:
            return self.instance.approvalstatus
        elif self.edit == 2:
            data = self.cleaned_data.get('approvalstatus')
            if data not in [0, 1, 2]:
                raise forms.ValidationError('Invalid approval status setting %(approved_status), must be 0, 1, or 2.', code='invalidapprovalstatus', params={'approved_status': data})
            return data

    def clean_slvl(self): #If self.edit is 0, slvl is set in clean()
        if self.edit == 1:
            return self.instance.slvl
        elif self.edit == 2:
            data = self.cleaned_data.get('slvl')
            if data not in [0, 1, 2, 3]:
                raise forms.ValidationError('Invalid security level setting %(slvl), must be 0, 1, 2, or 3.', code='invalidslvl', params={'slvl': data})
            return data

    def clean(self):
        cleaned_data = super(DebateForm, self).clean()
        tname = cleaned_data.get('topic_name')
        owner_name = cleaned_data.get('owner_name')
        if (tname or self.edit == 1) and (owner_name or self.edit == 0):
            if self.edit != 1:
                topic = Topic.objects.get(name=tname)
            else:
                topic = self.instance.topic
            if self.edit != 0:
                owner = User.objects.get(username=owner_name)
            else:
                owner = cleaned_data.get('owner')
            if self.edit == 1 and self.user != self.instance.owner:
                raise forms.ValidationError('You do not have permission to edit this debate.')
            cleaned_data['topic'] = topic
            cleaned_data['owner'] = owner
            if self.edit == 0:
                cleaned_data['slvl'] = topic.debslvl
            if ((topic.slvl == 1 or topic.slvl == 2) and (owner.approvedargs < 10 and not (self.user.moderator_of.filter(id=topic.id) or self.user.modstatus > 0))):
                raise forms.ValidationError('You must have at least 10 approved arguments to post here.')
            elif (topic.slvl == 3) and not (self.user.moderator_of.filter(id=topic.id) or self.user.modstatus > 0):
                raise forms.ValidationError('You must be a moderator in order to post to this topic.')
            if (self.edit == 2 and self.instance.approvalstatus == 1 and cleaned_data.get('approvalstatus') != 1):
                cleaned_data['approved_on'] = timezone.now()
            elif self.edit == 0:
                cleaned_data['approved_on'] = None
            elif self.edit == 1:
                cleaned_data['approved_on'] = self.instance.approved_on
        return cleaned_data

    class Meta:
        model = Debate
        fields = ['topic_name', 'owner_name', 'owner', 'topic', 'slvl', 'question', 'description', 'approvalstatus', 'created_on', 'edited_on', 'approved_on']
        widgets = {
            'owner': forms.HiddenInput(),
            'topic': forms.HiddenInput(),
            'created_on': forms.HiddenInput(),
            'edited_on': forms.HiddenInput(),
            'approved_on': forms.HiddenInput(),
        }
