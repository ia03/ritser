from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from debates.models import Topic
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
                ismod = user.ismod()
            if ismod:
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
        if request.user.isgmod():
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrap


def admin_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.isadmin():
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrap
