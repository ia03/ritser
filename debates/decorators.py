from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Topic


def mod_required(topic=False):
    def methodwrap(function):
        def wrap(request, *args, **kwargs):
            user = request.user
            if topic:
                topica = get_object_or_404(Topic, args[0])
                ismod = user.ismodof(topica)
            else:
                ismod = user.moderator_of.all().exists()
            if ismod or user.isgmod():
                return function(request, *args, **kwargs)
            else:
                raise PermissionDenied
        wrap.__doc__ = function.__doc__
        wrap.__name__ = function.__name__
        return login_required(wrap)
    return methodwrap
def gmod_required(function):
    def wrap(request, *args, **kwargs):
        user = request.user
        if user.modstatus > 0:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return login_required(wrap)