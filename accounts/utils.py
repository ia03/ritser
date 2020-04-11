from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from django.utils import timezone
from django.shortcuts import get_object_or_404


def DeleteUser(user, active, bannote=None):
    user.active = active
    user.is_active = False
    user.email = ""
    if bannote is not None:
        user.bannote = bannote
    user.save()
    EmailAddress.objects.filter(user=user).delete()
    SocialAccount.objects.filter(user=user).delete()

def get_user_or_404(username):
    return get_object_or_404(User, username__iexact=username)
