from django import forms
from .models import User
from debates.models import Topic
from captcha.fields import ReCaptchaField
from django.conf import settings
from django.contrib.auth.hashers import check_password
from allauth.account.models import EmailAddress
from allauth.account.adapter import get_adapter
from allauth.account.utils import filter_users_by_email
from allauth.account import app_settings
from django.utils.translation import pgettext, ugettext, ugettext_lazy as _



class SignupForm(forms.Form):
    captcha = ReCaptchaField(private_key=settings.GR_SIGNUPFORM, public_key='6LfKRk0UAAAAAAVkc0FNDHtLNyzwYwBiEUpVeDCe', error_messages={'required': 'Invalid ReCAPTCHA. Please try again.'})
    def signup(self, request, user):
        """ Required, or else it throws deprecation warnings """
        pass

class ProfileForm(forms.ModelForm):
    stopicsf = forms.CharField(required=False, label='Subscribed Topics (a space-separated list of their names)')
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
            forms.ValidationError('List of subscribed topics may not contain duplicates.', code='stopicsduplicate', params={'stopicsl': self.stopicnl})
        self.stopicsl = []
        for topicname in self.stopicnl:
            try:
                self.stopicsl.append(Topic.objects.get(name=topicname))
            except Topic.DoesNotExist:
                forms.ValidationError('Subscribed topic name not found.', code='stopicnotfound', params={'topicname': topicname})
        return data
    class Meta:
        model = User
        fields = ['bio', 'stopicsf', 'timezone']
class AddEmailForm(forms.Form):
    captcha = ReCaptchaField(private_key=settings.GR_ADDEMAILFORM, public_key='6Lc71U4UAAAAALLVIW91zfM37xT_8DSYvCdyXA7M', error_messages={'required': 'Invalid ReCAPTCHA. Please try again.'})
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

    def save(self, request):
        return EmailAddress.objects.add_email(request,
                                              self.user,
                                              self.cleaned_data["email"],
                                              confirm=True)
                                              
class DeleteUserForm(forms.Form):
    confirmation = forms.BooleanField(label='Check this if you are absolutely sure you want to delete your account', error_messages = {'required': 'You have not selected the confirmation checkbox.'})
    password = forms.CharField(widget=forms.PasswordInput, error_messages = {'required': 'You must type in your password.'})
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(DeleteUserForm, self).__init__(*args, **kwargs)
    def clean_password(self):
        data = self.cleaned_data['password']
        if not check_password(data, self.user.password):
            raise forms.ValidationError('The password inputted is incorrect.')
        return data
'''
class UserCreationForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """
    error_messages = {
        'password_mismatch': "The two password fields didn't match.",
    }
    email = forms.EmailField()
    password1 = forms.CharField(label="Password",
        widget=forms.PasswordInput)
    password2 = forms.CharField(label="Password confirmation",
        widget=forms.PasswordInput,
        help_text="Enter the same password as above, for verification.")

    class Meta:
        model = User
        fields = ['username', 'email',]

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()

        return user
'''