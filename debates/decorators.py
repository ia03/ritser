from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required

def mod_required(function):
    def wrap(request, *args, **kwargs):
        user = request.user
        if user.moderator_of.all().exists() or user.modstatus > 0:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return login_required(wrap)

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