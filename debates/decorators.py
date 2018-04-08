from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Topic
from functools import wraps


def mod_required(topic=False):
    def methodwrap(function):
        @wraps(function)
        def wrap(request, *args, **kwargs):
            user = request.user
            if (not callable(topic)) and topic:
                topica = get_object_or_404(Topic, args[0])
                ismod = user.ismodof(topica)
            else:
                ismod = user.moderator_of.all().exists()
            if ismod or user.isgmod():
                return function(request, *args, **kwargs)
            else:
                raise PermissionDenied
        return login_required(wrap)
    if callable(topic):
        return methodwrap(topic)
    else:
        return methodwrap
def gmod_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        user = request.user
        if user.modstatus > 0:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrap