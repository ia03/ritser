from django import forms
from .models import User
from debates.models import Topic
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3
from django.conf import settings
from django.contrib.auth.hashers import check_password
from allauth.account.models import EmailAddress
from allauth.account.adapter import get_adapter
from allauth.account.utils import filter_users_by_email
from allauth.account import app_settings
from django.utils.translation import pgettext, ugettext, ugettext_lazy as _

consentemaillabel = 'I consent to any e-mails submitted being used for account recovery and an error message shown to new users when they try to sign up with any of them until I revoke this consent by deleting them.'


class SignupForm(forms.Form):
    gdprconsent = forms.BooleanField(required=False, label=consentemaillabel)
    tos = forms.BooleanField(
        error_messages={
            'required': 'You must agree to the terms.'})
    captcha = ReCaptchaField(
        widget=ReCaptchaV3,
        error_messages={'required': 'Invalid ReCAPTCHA. Please try again.'}
    )

    def signup(self, request, user):
        """ Required, or else it throws deprecation warnings """
        pass

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['email'] != '' and cleaned_data['gdprconsent'] == False:
            raise forms.ValidationError(
                'You have not checked the consent checkbox.')
        return cleaned_data


class ProfileForm(forms.ModelForm):
    stopicsf = forms.CharField(
        required=False,
        label='Subscribed Topics (type in a list of the topics\' names separated by spaces)')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        stopicns = []
        for topic in self.instance.stopics.all():
            stopicns.append(topic.name)
        self.fields['stopicsf'].initial = ' '.join(stopicns)

    def clean_stopicsf(self):
        data = self.cleaned_data.get('stopicsf')
        self.stopicnl = data.split()
        if len(set(self.stopicnl)) != len(self.stopicnl):
            forms.ValidationError(
                'List of subscribed topics may not contain duplicates.',
                code='stopicsduplicate',
                params={'stopicsl': self.stopicnl}
            )
        self.stopicsl = []
        for topicname in self.stopicnl:
            try:
                self.stopicsl.append(Topic.objects.get(name=topicname))
            except Topic.DoesNotExist:
                forms.ValidationError(
                    'Subscribed topic name not found.',
                    code='stopicnotfound',
                    params={'topicname': topicname}
                )
        return data

    class Meta:
        model = User
        fields = ['bio', 'stopicsf', 'timezone']


class AddEmailForm(forms.Form):
    gdprconsent = forms.BooleanField(label=consentemaillabel)
    captcha = ReCaptchaField(
        widget=ReCaptchaV3,
        error_messages={'required': 'Invalid ReCAPTCHA. Please try again.'}
    )
    email = forms.EmailField(
        label=_("E-mail"),
        required=True,
        widget=forms.TextInput(
            attrs={"type": "email",
                   "size": "30",
                   "placeholder": _('E-mail address')}))

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_email(self):
        value = self.cleaned_data["email"]
        value = get_adapter().clean_email(value)
        errors = {
            "this_account": _("This e-mail address is already associated"
                              " with this account."),
            "different_account": _("This e-mail address is already associated"
                                   " with another account."),
        }
        users = filter_users_by_email(value)
        on_this_account = [u for u in users if u.pk == self.user.pk]
        on_diff_account = [u for u in users if u.pk != self.user.pk]

        if on_this_account:
            raise forms.ValidationError(errors["this_account"])
        if on_diff_account and app_settings.UNIQUE_EMAIL:
            raise forms.ValidationError(errors["different_account"])
        return value

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['email'] != '' and cleaned_data['gdprconsent'] == False:
            raise forms.ValidationError(
                'You have not checked the consent checkbox.')
        return cleaned_data

    def save(self, request):
        return EmailAddress.objects.add_email(request,
                                              self.user,
                                              self.cleaned_data["email"],
                                              confirm=True)


class DeleteUserForm(forms.Form):
    confirmation = forms.BooleanField(
        label='Check this if you are absolutely sure you want to delete your account',
        error_messages={
            'required': 'You have not selected the confirmation checkbox.'})
    password = forms.CharField(
        widget=forms.PasswordInput, error_messages={
            'required': 'You must type in your password.'})

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def clean_password(self):
        data = self.cleaned_data['password']
        if not check_password(data, self.user.password):
            raise forms.ValidationError('The password inputted is incorrect.')
        return data



class SetStaffForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def clean_modstatus(self):
        data = self.cleaned_data['modstatus']
        ums = self.user.modstatus #editing user's mod status
        oms = self.instance.modstatus #original mod status
        em1 = 'You are not allowed to set this person\'s mod status that high.'
        em2 = 'This person\'s mod status level is too high for you to change.'
        if ums == User.modschoices.admin:
            if data != User.modschoices.gmod:
                raise forms.ValidationError(em1)
            if oms == User.modschoices.admin or (
                oms == User.modschoices.owner):
                    raise forms.ValidationError(em2)
        return data
    class Meta:
        model = User
        fields = [
            'modstatus']
