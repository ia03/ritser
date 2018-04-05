from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount

def DeleteUser(user, active, bannote=None):
    user.active = active
    user.is_active = False
    user.email = ""
    if bannote is not None:
        user.bannote = bannote
    user.save()
    EmailAddress.objects.filter(user=user).delete()
    SocialAccount.objects.filter(user=user).delete()