from django import forms
from .models import Debate, Topic
from accounts.models import User
from django.core.exceptions import ObjectDoesNotExist

class DebateForm(forms.ModelForm):
    topic_name = forms.CharField(max_length=30)
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super(DebateForm, self).__init__(*args, **kwargs)
        self.fields['owner'].required = False
        self.fields['topic'].required = False
        self.fields['slvl'].required = False
        
    def clean_topic_name(self):
        data = self.cleaned_data['topic_name']
        try:
            a = Topic.objects.get(name=data)
        except ObjectDoesNotExist:
            raise forms.ValidationError('Topic %(topic_name)s not found.', code='topicnotfound', params={'topic_name': data})
        return data
    def clean_owner(self):
        return self.user
    def clean(self):
        cleaned_data = super(DebateForm, self).clean()
        tname = cleaned_data.get('topic_name')
        owner = cleaned_data.get('owner')
        print(cleaned_data)
        if tname:
            topic = Topic.objects.get(name=tname)
            cleaned_data['topic'] = topic
            cleaned_data['slvl'] = topic.debslvl
            if (topic.slvl == 1 and owner.approvedargs < 10):
                raise forms.ValidationError('You must have at least 10 approved arguments to post here.')
            elif (topic.slvl == 2) and not (owner.moderator_of.filter(id=cleaned_data['topic'].id) or owner.modstatus > 0):
                raise forms.ValidationError('You must be a moderator in order to post to this topic.')
        return cleaned_data
    class Meta:
        model = Debate
        fields = ['topic_name', 'owner', 'topic', 'slvl', 'question', 'description']
        widgets = {
            'owner': forms.HiddenInput(),
            'topic': forms.HiddenInput(),
            'slvl': forms.HiddenInput(),
        }
