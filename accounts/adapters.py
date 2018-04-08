from allauth.account.adapter import DefaultAccountAdapter
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.timezone import now, make_aware
from datetime import timedelta, datetime
from collections import OrderedDict


class LimitedSizeDict(OrderedDict):
    def __init__(self, *args, **kwds):
        self.size_limit = kwds.pop("limit", None)
        OrderedDict.__init__(self, *args, **kwds)
        self._check_size_limit()

    def __setitem__(self, key, value):
        OrderedDict.__setitem__(self, key, value)
        self._check_size_limit()

    def _check_size_limit(self):
        if self.size_limit is not None:
            while len(self) > self.size_limit:
                self.popitem(last=False)


class DefaultAccountAdapter(DefaultAccountAdapter):
    emails = LimitedSizeDict(limit=1500)

    def send_mail(self, template_prefix, email, context):
        if DefaultAccountAdapter.emails.get(email, make_aware(datetime.min)) < (
                now() - timedelta(seconds=300)):  # rate limiting, 5 mins per email
            msg = self.render_mail(template_prefix, email, context)
            msg.send()
            DefaultAccountAdapter.emails[email] = now()

    def respond_user_inactive(self, request, user):
        request.session['useriaid'] = user.id
        return HttpResponseRedirect(
            reverse('account_inactive'))
