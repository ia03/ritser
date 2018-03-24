from allauth.account.adapter import DefaultAccountAdapter
from django.http import HttpResponseRedirect
from django.urls import reverse

class DefaultAccountAdapter(DefaultAccountAdapter):
    def respond_user_inactive(self, request, user):
        request.session['useriaid'] = user.id
        return HttpResponseRedirect(
            reverse('account_inactive'))