from django import forms
from .models import Debate, Topic
from accounts.models import User
from django.core.exceptions import ObjectDoesNotExist

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
        if self.edit == 0:
            self.fields['slvl'].required = False
            self.fields['slvl'].widget = forms.HiddenInput()
            self.fields['owner_name'].required = False
            self.fields['owner_name'].widget = forms.HiddenInput()
        elif self.edit == 1:
            self.fields['slvl'].required = False
            self.fields['slvl'].widget = forms.HiddenInput()
            self.fields['topic_name'].required = False
            self.fields['topic_name'].widget = forms.HiddenInput()

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
            cleaned_data['topic'] = topic
            cleaned_data['owner'] = owner
            cleaned_data['slvl'] = topic.debslvl
            if (topic.slvl == 1 and owner.approvedargs < 10):
                raise forms.ValidationError('You must have at least 10 approved arguments to post here.')
            elif (topic.slvl == 2) and not (owner.moderator_of.filter(id=cleaned_data['topic'].id) or owner.modstatus > 0):
                raise forms.ValidationError('You must be a moderator in order to post to this topic.')
        return cleaned_data
        
    class Meta:
        model = Debate
        fields = ['topic_name', 'owner_name', 'owner', 'topic', 'slvl', 'question', 'description']
        widgets = {
            'owner': forms.HiddenInput(),
            'topic': forms.HiddenInput(),
        }
