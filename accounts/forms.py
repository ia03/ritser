from django import forms
from .models import User
from captcha.fields import ReCaptchaField
from django.conf import settings
class SignupForm(forms.Form):
    captcha = ReCaptchaField(private_key=settings.GR_SIGNUPFORM, public_key='6LfKRk0UAAAAAAVkc0FNDHtLNyzwYwBiEUpVeDCe', error_messages={'required': 'Invalid ReCAPTCHA. Please try again.'})
    def signup(self, request, user):
        """ Required, or else it throws deprecation warnings """
        pass

class ProfileForm(forms.ModelForm):
    
    class Meta:
        model = User
        fields = ['bio']
        
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