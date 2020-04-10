from django import forms
from .models import Topic, Debate, Argument, Report
from accounts.models import User
from django.utils import timezone
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3
from django.conf import settings
from .utils import (
    chkarg,
    chkdeb,
    chktop,
    chkusr,
    disablefield,
    donotrequire,
    cleanownername,
    cleanowner,
    cleancreatedon,
    cleanapprovalstatus,
    cleaneditedon,
    cleanmodnote,
    setapprovedon,
    cleandslvl)

USERNAMEMAXLEN = 27

class DebateForm(forms.ModelForm):
    topic_name = forms.CharField(
        max_length=30, error_messages={
            'required': 'You must specify the name of the topic the debate will belong to.'})
    owner_name = forms.CharField(
        error_messages={
            'required': 'You must specify the name of the user who will own the debate.'})
    captcha = ReCaptchaField(
        widget=ReCaptchaV3,
        error_messages={
            'required': 'Invalid ReCAPTCHA. Please try again.'})

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        if 'edit' in kwargs:
            self.edit = kwargs.pop("edit")
        else:
            self.edit = 0
        super().__init__(*args, **kwargs)
        donotrequire(
            self,
            'owner',
            'topic',
            'created_on',
            'edited_on',
            'approved_on')
        self.fields['modnote'].label = 'Moderator note'
        self.fields['question'].error_messages = {
            'required': 'You must type in a question.'}
        if self.edit == 0:
            disablefield(
                self,
                'slvl',
                'owner_name',
                'approvalstatus',
                'modnote')
        elif self.edit == 1:
            disablefield(
                self,
                'slvl',
                'topic_name',
                'approvalstatus',
                'modnote')
            self.fields['owner_name'].initial = self.instance.owner.get_username()
        else:
            self.fields['slvl'].error_messages = {
                'required': 'You must specify a security level for the debate.'}
            self.fields['approvalstatus'].error_messages = {
                'required': 'You must specify the approval status for the debate.'}
            self.fields['topic_name'].initial = self.instance.topic_id
            self.fields['owner_name'].initial = self.instance.owner.get_username()

    def clean_topic_name(self):
        data = self.cleaned_data['topic_name']
        if self.edit != 1:
            chktop(data)
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

    def clean_slvl(self):  # If self.edit is 0, slvl is set in clean()
        if self.edit == 1:
            return self.instance.slvl
        elif self.edit == 2:
            data = self.cleaned_data.get('slvl')
            cleandslvl(data)
            return data

    def clean(self):
        cleaned_data = super().clean()
        tname = cleaned_data.get('topic_name')
        owner_name = cleaned_data.get('owner_name')
        if (tname or self.edit == 1) and (owner_name or self.edit == 0):
            if self.edit == 1:
                topic = self.instance.topic
            else:
                topic = Topic.objects.get(name=tname)
            if self.edit == 0:
                owner = cleaned_data.get('owner')
                if self.user.ismodof(topic):
                    cleaned_data['approvalstatus'] = 0
            else:
                owner = User.objects.get(username=owner_name)
            if (not self.user.hasperm()) or (self.edit ==
                                             1 and self.user != self.instance.owner):
                raise forms.ValidationError(
                    'You do not have permission to perform this action.')
            cleaned_data['topic'] = topic
            cleaned_data['owner'] = owner
            if self.edit == 0:
                cleaned_data['slvl'] = topic.debslvl
            # see able_to_submit()
            if ((topic.slvl == 1 or topic.slvl == 2) and (owner.get_approvedargs() < 10 and not self.user.ismodof(
                    topic)) and (self.edit == 0 or owner != self.user)):  # add subscriber status here
                raise forms.ValidationError(
                    'You must have at least 10 approved arguments to post to a topic with a security level of 1 or 2.')
            elif (topic.slvl == 3) and not self.user.ismodof(topic):
                raise forms.ValidationError(
                    'You must be a moderator in order to post to or edit in this topic.')
            cleaned_data['approved_on'] = setapprovedon(self)

        return cleaned_data

    class Meta:
        model = Debate
        fields = [
            'topic_name',
            'owner_name',
            'owner',
            'topic',
            'slvl',
            'question',
            'description',
            'approvalstatus',
            'created_on',
            'edited_on',
            'approved_on',
            'modnote']
        widgets = {
            'owner': forms.HiddenInput(),
            'topic': forms.HiddenInput(),
            'created_on': forms.HiddenInput(),
            'edited_on': forms.HiddenInput(),
            'approved_on': forms.HiddenInput(),
        }


class ArgumentForm(forms.ModelForm):
    owner_name = forms.CharField(
        error_messages={
            'required': 'You must specify the name of the user who will own the argument.'})
    debate_id = forms.IntegerField(
        label='Debate ID (comes after the topic name in the URL)', error_messages={
            'required': 'You must specify the ID of the debate this argument will belong to.'})
    captcha = ReCaptchaField(
        widget=ReCaptchaV3,
        error_messages={
            'required': 'Invalid ReCAPTCHA. Please try again.'})

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        if 'edit' in kwargs:
            self.edit = kwargs.pop("edit")
        else:
            self.edit = 0
        super().__init__(*args, **kwargs)
        donotrequire(
            self,
            'owner',
            'topic',
            'debate',
            'created_on',
            'edited_on')
        self.fields['modnote'].label = 'Moderator note (can be blank)'
        self.fields['order'].label = 'Order (the greater this is, the higher this argument will be ranked)'
        self.fields['title'].error_messages = {
            'required': 'You must type in a title.'}
        self.fields['body'].error_messages = {
            'required': 'You must type in a body.'}
        self.fields['side'].error_messages = {
            'required': 'You must specify a side for the argument.'}
        if self.edit == 0:
            disablefield(
                self,
                'owner_name',
                'order',
                'approvalstatus',
                'modnote')
        elif self.edit == 1:
            disablefield(self, 'debate_id', 'approvalstatus', 'modnote')
            self.fields['order'].widget.attrs['readonly'] = True
            self.fields['owner_name'].initial = self.instance.owner.get_username()
        else:
            self.fields['approvalstatus'].error_messages = {
                'required': 'You must specify the approval status for the argument.'}
            self.fields['order'].error_messages = {
                'required': 'You must specify an order/priority number for the argument.'}
            self.fields['debate_id'].initial = self.instance.debate_id
            self.fields['owner_name'].initial = self.instance.owner.get_username()

    def clean_debate_id(self):
        data = self.cleaned_data['debate_id']
        if self.edit != 1:
            chkdeb(data)
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
            raise forms.ValidationError(
                'Invalid side setting %(side)s, must be 0 or 1.',
                code='invalidside',
                params={
                    'side': data})
        return data

    def clean(self):
        cleaned_data = super().clean()
        did = cleaned_data.get('debate_id')
        owner_name = cleaned_data.get('owner_name')
        if (did or self.edit == 1) and (owner_name or self.edit == 0):
            if self.edit == 1:
                debate = self.instance.debate
            else:
                debate = Debate.objects.get(id=did)
            topic = debate.topic
            if self.edit == 0:
                owner = cleaned_data.get('owner')
                if self.user.ismodof(debate.topic):
                    cleaned_data['approvalstatus'] = 0
            else:
                owner = User.objects.get(username=owner_name)
            if (not self.user.hasperm()) or (
                self.edit == 1 and self.user != self.instance.owner):
                raise forms.ValidationError(
                    'You do not have permission to perform this action.')
            cleaned_data['debate'] = debate
            cleaned_data['topic'] = topic
            cleaned_data['owner'] = owner
            if (
                debate.slvl == 2 or debate.slvl == 3) and (
                owner.get_approvedargs() < 20 and not self.user.ismodof(topic) and (
                    self.edit == 0 or owner != self.user)):  # add subscriber status here
                raise forms.ValidationError(
                    'You must have at least 20 approved arguments to post to a debate with a security level of 2 or 3.')
            if (debate.slvl == 4) and not self.user.ismodof(topic):
                raise forms.ValidationError(
                    'You must be a moderator to post to a debate with a security level of 4.')
            cleaned_data['approved_on'] = setapprovedon(self)
        return cleaned_data

    class Meta:
        model = Argument
        fields = [
            'debate_id',
            'owner_name',
            'owner',
            'topic',
            'debate',
            'approvalstatus',
            'order',
            'side',
            'title',
            'body',
            'modnote',
            'created_on',
            'edited_on']
        widgets = {
            'owner': forms.HiddenInput(),
            'topic': forms.HiddenInput(),
            'debate': forms.HiddenInput(),
            'created_on': forms.HiddenInput(),
            'edited_on': forms.HiddenInput(),
        }


class TopicForm(forms.ModelForm):
    modsf = forms.CharField(
        required=False,
        label='Moderators (a space-separated list of their names)',
        error_messages={
            'required': 'You must input the moderators\' names.'})
    captcha = ReCaptchaField(
        widget=ReCaptchaV3,
        error_messages={
            'required': 'Invalid ReCAPTCHA. Please try again.'})
    owner_name = forms.CharField(error_messages={
        'required': 'You must specify the name of the user who will own the topic.'})

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        if 'edit' in kwargs:
            self.edit = kwargs.pop("edit")
        else:
            self.edit = 0
        self.modsl = []
        super().__init__(*args, **kwargs)
        donotrequire(
            self,
            'owner',
            'modsf',
            'created_on',
            'created_by',
            'edited_on')
        self.fields['name'].error_messages = {
            'required': 'You must type in a name.'}
        self.fields['description'].error_messages = {
            'required': 'You must type in a description.'}
        self.fields['slvl'].error_messages = {
            'required': 'You must specify a security level for the topic.'}
        self.fields['debslvl'].error_messages = {
            'required': 'You must specify a default debate security level for the topic.'}
        if self.edit == 0:
            disablefield(self, 'owner_name')
        elif self.edit == 1:
            disablefield(self, 'owner_name', 'name', 'modsf')
            self.fields['owner_name'].initial = self.instance.owner.get_username()
        else:
            disablefield(self, 'name')
            self.fields['owner_name'].initial = self.instance.owner.get_username()
            modns = []
            for mod in self.instance.moderators.all():
                modns.append(mod.get_username())
            self.fields['modsf'].initial = ' '.join(modns)

    def clean_name(self):
        data = self.cleaned_data['name']
        if self.edit != 0:
            return self.instance.name
        else:
            return data

    def clean_owner_name(self):
        data = self.cleaned_data['owner_name']
        if self.edit != 0 and self.edit != 1:
            owner = chkusr(data)
            if owner.active == 1 or owner.active == 3:
                raise forms.ValidationError(
                    'User %(owner_name)s can not be set as the owner.',
                    code='userinactive',
                    params={
                        'owner_name': data})
        return data

    def clean_owner(self):
        return cleanowner(self)

    def clean_created_on(self):
        return cleancreatedon(self)

    def clean_created_by(self):
        if self.edit == 0:
            return self.user
        else:
            return self.instance.created_by

    def clean_edited_on(self):
        return cleaneditedon(self)

    def clean_modsf(self):
        data = self.cleaned_data.get('modsf')
        self.modnl = data.split()
        if len(set(self.modnl)) != len(self.modnl):
            raise forms.ValidationError(
                'List of moderators may not contain duplicates.',
                code='modsduplicate',
                params={
                    'modnl': self.modnl})
        for modname in self.modnl:
            try:
                mod = User.objects.get(username=modname)
            except User.DoesNotExist:
                raise forms.ValidationError(
                    'Moderator %(modname)s not found.',
                    code='modnotfound',
                    params={
                        'modname': modname})
            if mod.active == 1 or mod.active == 3:
                raise forms.ValidationError(
                    'User %(modname)s can not be set as a moderator.',
                    code='userinactive',
                    params={
                        'modname': modname})
            self.modsl.append(mod)
        return data

    def clean_slvl(self):
        data = self.cleaned_data.get('slvl')
        if data not in [0, 1, 2, 3]:
            raise forms.ValidationError(
                'Invalid security level setting %(slvl)s, must be 0, 1, 2, or 3.',
                code='invalidslvl',
                params={
                    'slvl': data})
        return data

    def clean_debslvl(self):
        data = self.cleaned_data.get('debslvl')
        if data not in [0, 1, 2, 3, 4]:
            raise forms.ValidationError(
                'Invalid default debate security level setting %(debslvl)s, must be 0, 1, 2, 3, or 4.',
                code='invaliddebslvl',
                params={
                    'debslvl': data})
        return data

    def clean(self):
        cleaned_data = super().clean()
        owner_name = cleaned_data.get('owner_name')
        if owner_name or self.edit == 0 or self.edit == 1:
            if self.edit == 0:
                owner = cleaned_data.get('owner')
            elif self.edit == 1:
                owner = self.instance.owner
            else:
                owner = User.objects.get(username=owner_name)
            if (not self.user.hasperm()) or (self.edit ==
                                             1 and (not self.user.ismodof(self.instance))):
                raise forms.ValidationError(
                    'You do not have permission to perform this action.')
            cleaned_data['owner'] = owner
            if self.edit != 1 and owner.get_approvedargs() < 20 and not self.user.isgmod(
            ) and (self.edit == 0 or owner != self.user):  # add subscriber status here
                raise forms.ValidationError(
                    'You must have at least 20 approved arguments to own a topic.')
            if self.edit != 1 and owner.topics_owned.all().count() >= 5 and not self.user.isgmod(
            ) and (self.edit == 0 or owner != self.user):  # add subscriber status here
                raise forms.ValidationError(
                    'You can only own a maximum of 5 topics.')
            if owner in self.modsl:
                raise forms.ValidationError(
                    'Owner must not be one of the moderators.')
        return cleaned_data

    class Meta:
        model = Topic
        fields = [
            'owner_name',
            'owner',
            'name',
            'title',
            'modsf',
            'slvl',
            'debslvl',
            'description',
            'created_on',
            'created_by',
            'edited_on']
        widgets = {
            'owner': forms.HiddenInput(),
            'created_on': forms.HiddenInput(),
            'created_by': forms.HiddenInput(),
            'edited_on': forms.HiddenInput(),
        }


class BanForm(forms.Form):
    username = forms.CharField(
        max_length=USERNAMEMAXLEN,
        error_messages={
            'required': 'You must input the chosen user\'s username.'})
    terminate = forms.BooleanField(required=False, label='Terminate')
    bandate = forms.DateField(
        label='Suspended until (MM/DD/YYYY)',
        required=False)
    bannote = forms.CharField(
        widget=forms.Textarea,
        required=False,
        max_length=10000,
        label='Ban note (You can use markdown.)')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

    def clean_username(self):
        data = self.cleaned_data['username']
        user = chkusr(data)
        if not user.is_active:
            raise forms.ValidationError(
                'User %(username)s can not be suspended/terminated.',
                code='usernotactive',
                params={
                    'username': data})
        if user.modstatus >= self.user.modstatus:
            raise forms.ValidationError(
                'You do not have permission to suspend/terminate %(username)s.',
                code='userismod',
                params={
                    'username': data})
        return data

    def clean_bandate(self):
        data = self.cleaned_data['bandate']
        if data is not None:
            if data < timezone.now().date():
                raise forms.ValidationError(
                    'The date the user is suspended until may not be in the past.')
        return data

    def clean(self):
        cleaned_data = super().clean()
        if 'bandate' in cleaned_data:
            if (not cleaned_data.get('terminate')
                ) and cleaned_data.get('bandate') is None:
                raise forms.ValidationError('You must input a date.')


class UnsuspendForm(forms.Form):
    username = forms.CharField(
        max_length=USERNAMEMAXLEN,
        error_messages={
            'required': 'You must input the username of the chosen user.'})

    def clean_username(self):
        data = self.cleaned_data['username']
        user = chkusr(data)
        if user.active != 2:
            raise forms.ValidationError(
                'User %(username)s is not suspended.',
                code='usernotsuspended',
                params={
                    'username': data})
        return data


pmchoices = (
    ('1', 'Argument'),
    ('2', 'Debate'),
)


class DeleteForm(forms.Form):
    mtype = forms.ChoiceField(
        widget=forms.RadioSelect(),
        choices=pmchoices,
        label='Type of post',
        error_messages={
            'required': 'You must specify the type of post to delete.'})
    idno = forms.IntegerField(
        label='ID',
        error_messages={
            'required': 'You must specify the ID of the post to delete.'})

    def clean(self):
        cleaned_data = super().clean()
        mtype = cleaned_data['mtype']
        idno = cleaned_data['idno']
        if mtype == '1':
            argument = chkarg(idno)
            self.post = argument
        elif mtype == '2':

            debate = chkdeb(idno)
            self.post = debate
        return cleaned_data


mmchoices = (
    ('1', 'Debate'),
    ('2', 'Topic'),
)


class MoveForm(forms.Form):
    mtype = forms.ChoiceField(
        widget=forms.RadioSelect(),
        choices=mmchoices,
        label='Type of container',
        error_messages={
            'required': 'You must specify the type of container post.'})
    fid = forms.CharField(label='ID/Name of first debate/topic')
    sid = forms.CharField(label='ID/Name of second debate/topic')

    def clean(self):
        cleaned_data = super().clean()
        mtype = cleaned_data['mtype']
        fid = cleaned_data['fid']
        sid = cleaned_data['sid']
        if mtype == '1':
            debate = chkdeb(fid)
            debate2 = chkdeb(sid)
            self.post = debate
            self.post2 = debate2
        elif mtype == '2':
            topic = chktop(fid)
            topic2 = chktop(sid)
            self.post = topic
            self.post2 = topic2
        return cleaned_data


class UpdateSlvlForm(forms.Form):
    tname = forms.CharField(label='Topic name')
    slvl = forms.IntegerField(label='Security level')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

    def clean_tname(self):
        data = self.cleaned_data['tname']
        topic = chktop(data)
        if not self.user.ismodof(topic):
            raise forms.ValidationError(
                'You are not a moderator of topic %(tname)s.',
                code='notmodoftopic',
                params={
                    'tname': data})
        self.topic = topic
        return data

    def clean_slvl(self):
        data = self.cleaned_data['slvl']
        cleandslvl(data)
        return data

class ReportForm(forms.ModelForm):
    captcha = ReCaptchaField(
        widget=ReCaptchaV3,
        error_messages={
            'required': 'Invalid ReCAPTCHA. Please try again.'})
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content_type'].label = 'Type of thing reported'
        self.fields['object_id'].label = 'ID/Name'
        self.fields['content_type'].choices = [
            (choice[0], choice[1].capitalize()) for choice in
            self.fields['content_type'].choices]

    def clean(self):
        cleaned_data = super().clean()
        ctype = cleaned_data['content_type'].model
        objid = cleaned_data['object_id']
        if(ctype == 'argument'):
            self.obj = chkarg(objid)
        elif(ctype == 'debate'):
            self.obj = chkdeb(objid)
        elif(ctype == 'topic'):
            self.obj = chktop(objid)
        elif(ctype == 'user'):
            self.obj = chkusr(objid)
        return cleaned_data

    class Meta:
        model = Report
        fields = [
            'rule',
            'description',
            'content_type',
            'object_id',
            ]
