from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount

def DeleteUser(user, active):
    user.active = active
    user.is_active = False
    user.email = ""
    user.save()
    EmailAddress.objects.filter(user=user).delete()
    SocialAccount.objects.filter(user=user).delete()