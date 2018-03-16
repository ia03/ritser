from django import forms
from .models import Topic, Debate, Argument
from accounts.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

def disablefield(instance, *args):
    for arg in args:
        instance.fields[arg].required = False
        instance.fields[arg].widget = forms.HiddenInput()
def donotrequire(instance, *args):
    for arg in args:
        instance.fields[arg].required = False
def cleanownername(instance):
    data = instance.cleaned_data['owner_name']
    if instance.edit != 0:
        try:
            User.objects.get(username=data)
        except ObjectDoesNotExist:
            raise forms.ValidationError('User %(owner_name)s not found.', code='usernotfound', params={'owner_name': data})
    return data
def cleanowner(instance):
    if instance.edit == 0:
        return instance.user
    else:
        return instance.cleaned_data.get('owner')
def cleancreatedon(instance):
    if instance.edit == 0:
        return timezone.now()
    else:
        return instance.instance.created_on
def cleanapprovalstatus(instance):
    if instance.edit == 0:
        return 1
    elif instance.edit == 1:
        return instance.instance.approvalstatus
    elif instance.edit == 2:
        data = instance.cleaned_data.get('approvalstatus')
        if data not in [0, 1, 2]:
            raise forms.ValidationError('Invalid approval status setting %(approved_status), must be 0, 1, or 2.', code='invalidapprovalstatus', params={'approved_status': data})
        return data
def cleaneditedon(instance):
    return timezone.now()
def cleanmodnote(instance):
    if instance.edit == 0:
        return ""
    elif instance.edit == 1:
        return instance.instance.modnote
    elif instance.edit == 2:
        return instance.cleaned_data.get('modnote')
def setapprovedon(instance):
    cleaned_data = instance.cleaned_data
    if (instance.edit == 2 and instance.instance.approvalstatus == 1 and cleaned_data.get('approvalstatus') != 1):
        return timezone.now()
    elif instance.edit == 1:
        return instance.instance.approved_on
    elif instance.edit == 0:
        return None

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
        donotrequire(self, 'owner', 'topic', 'created_on', 'edited_on', 'approved_on')
        self.fields['approvalstatus'].label = 'Approval Status (0: Approved, 1: Unapproved, 2: Denied)'
        self.fields['slvl'].label = 'Security Level'
        self.fields['modnote'].label = 'Moderator Note'
        self.fields['question'].error_messages = {'required': 'You must type in a question.'}
        self.fields['topic_name'].error_messages = {'required': 'You must specify the name of the topic the debate will belong to.'}
        self.fields['owner_name'].error_messages = {'required': 'You must specify the name of the user who will own the debate.'}
        if self.edit == 0:
            disablefield(self, 'slvl', 'owner_name', 'approvalstatus', 'modnote')
        elif self.edit == 1:
            disablefield(self, 'slvl', 'topic_name', 'approvalstatus', 'modnote')
            self.fields['owner_name'].initial = self.instance.owner.username
        else:
            self.fields['slvl'].error_messages = {'required': 'You must specify a security level for the debate.'}
            self.fields['approvalstatus'].error_messages = {'required': 'You must specify the approval status for the debate.'}
            self.fields['topic_name'].initial = self.instance.topic_id
            self.fields['owner_name'].initial = self.instance.owner.username

    def clean_topic_name(self):
        data = self.cleaned_data['topic_name']
        if self.edit != 1:
            try:
                Topic.objects.get(name=data)
            except ObjectDoesNotExist:
                raise forms.ValidationError('Topic %(topic_name)s not found.', code='topicnotfound', params={'topic_name': data})
        return data
    def clean_topic(self):
        if self.edit == 1:
            return self.instance.topic
        else:
            return self.cleaned_data.get('topic')
    def clean_owner_name(self):
        return cleanownername(self)
    def clean_owner(self):
        return cleanowner(self)
    def clean_created_on(self):
        return cleancreatedon(self)
    def clean_edited_on(self):
        return cleaneditedon(self)
    def clean_approvalstatus(self):
        return cleanapprovalstatus(self)
    def clean_modnote(self):
        return cleanmodnote(self)
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
            if ((topic.slvl == 1 or topic.slvl == 2) and (owner.approvedargs < 10 and not self.user.ismod(topic))):
                raise forms.ValidationError('You must have at least 10 approved arguments to post to a topic with a security level of 1 or 2.')
            elif (topic.slvl == 3) and not self.user.ismod(topic):
                raise forms.ValidationError('You must be a moderator in order to post to this topic.')
            cleaned_data['approved_on'] = setapprovedon(self)

        return cleaned_data

    class Meta:
        model = Debate
        fields = ['topic_name', 'owner_name', 'owner', 'topic', 'slvl', 'question', 'description', 'approvalstatus', 'created_on', 'edited_on', 'approved_on', 'modnote']
        widgets = {
            'owner': forms.HiddenInput(),
            'topic': forms.HiddenInput(),
            'created_on': forms.HiddenInput(),
            'edited_on': forms.HiddenInput(),
            'approved_on': forms.HiddenInput(),
        }


class ArgumentForm(forms.ModelForm):
    owner_name = forms.CharField(max_length=30)
    debate_id = forms.IntegerField()
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        if 'edit' in kwargs:
            self.edit = kwargs.pop("edit")
        else:
            self.edit = 0
        super(ArgumentForm, self).__init__(*args, **kwargs)
        donotrequire(self, 'owner', 'topic', 'debate', 'created_on', 'edited_on')
        self.fields['approvalstatus'].label = 'Approval Status'
        self.fields['modnote'].label = 'Moderator Note (can be blank)'
        self.fields['side'].label = 'Side (0=For, 1=Against)'
        self.fields['approvalstatus'].label = 'Approval Status (0: Approved, 1: Unapproved, 2: Denied)'
        self.fields['debate_id'].label = 'Debate ID (comes after the topic name in the URL)'
        self.fields['order'].label = 'Order (the greater this is, the higher this argument will be)'
        self.fields['title'].error_messages = {'required': 'You must type in a title.'}
        self.fields['body'].error_messages = {'required': 'You must type in a body.'}
        self.fields['debate_id'].error_messages = {'required': 'You must specify the ID of the debate this argument will belong to.'}
        self.fields['owner_name'].error_messages = {'required': 'You must specify the name of the user who will own the argument.'}
        self.fields['side'].error_messages = {'required': 'You must specify a side for the argument.'}
        if self.edit == 0:
            disablefield(self, 'owner_name', 'order', 'approvalstatus', 'modnote')
        elif self.edit == 1:
            disablefield(self, 'debate_id', 'approvalstatus', 'modnote')
            self.fields['order'].widget.attrs['readonly'] = True
            self.fields['owner_name'].initial = self.instance.owner.username
        else:
            self.fields['approvalstatus'].error_messages = {'required': 'You must specify the approval status for the argument.'}
            self.fields['order'].error_messages = {'required': 'You must specify an order/priority number for the argument.'}
            self.fields['debate_id'].initial = self.instance.debate_id
            self.fields['owner_name'].initial = self.instance.owner.username
    
    def clean_debate_id(self):
        data = self.cleaned_data['debate_id']
        if self.edit != 1:
            try:
                Debate.objects.get(id=data)
            except ObjectDoesNotExist:
                raise forms.ValidationError('Debate %(debate_id)s not found.', code='debatenotfound', params={'debate_id': data})
        return data
    def clean_debate(self):
        if self.edit == 1:
            return self.instance.debate
        else:
            return self.cleaned_data.get('debate')
    def clean_owner_name(self):
        return cleanownername(self)
    def clean_owner(self):
        return cleanowner(self)
    def clean_created_on(self):
        return cleancreatedon(self)
    def clean_edited_on(self):
        return cleaneditedon(self)
    def clean_approvalstatus(self):
        return cleanapprovalstatus(self)
    def clean_order(self):
        if self.edit == 0:
            return 0
        elif self.edit == 1:
            return self.instance.order
        elif self.edit == 2:
            return self.cleaned_data.get('order')
    def clean_modnote(self):
        return cleanmodnote(self)
    def clean_side(self):
        data = self.cleaned_data.get('side')
        if data not in [0, 1]:
            raise forms.ValidationError('Invalid side setting %(side), must be 0 or 1.', code='invalidside', params={'side': data})
        return data
    def clean(self):
        cleaned_data = super(ArgumentForm, self).clean()
        did = cleaned_data.get('debate_id')
        owner_name = cleaned_data.get('owner_name')
        if (did or self.edit == 1) and (owner_name or self.edit == 0):
            if self.edit != 1:
                debate = Debate.objects.get(id=did)
            else:
                debate = self.instance.debate
            topic = debate.topic
            if self.edit != 0:
                owner = User.objects.get(username=owner_name)
            else:
                owner = cleaned_data.get('owner')
            if self.edit == 1 and self.user != self.instance.owner:
                raise forms.ValidationError('You do not have permission to edit this debate.')
            cleaned_data['debate'] = debate
            cleaned_data['topic'] = topic
            cleaned_data['owner'] = owner
            if debate.slvl == 2 and (owner.approvedargs < 20 and not self.user.ismod(topic)):
                raise forms.ValidationError('You must have at least 20 approved arguments to post to a debate with a security level of 2.')
            cleaned_data['approved_on'] = setapprovedon(self)
        return cleaned_data
        
    class Meta:
        model = Argument
        fields = ['debate_id', 'owner_name', 'owner', 'topic', 'debate', 'approvalstatus', 'order', 'side', 'title', 'body', 'modnote', 'created_on', 'edited_on']
        widgets = {
            'owner': forms.HiddenInput(),
            'topic': forms.HiddenInput(),
            'debate': forms.HiddenInput(),
            'created_on': forms.HiddenInput(),
            'edited_on': forms.HiddenInput(),
        }