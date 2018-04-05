from django.utils import timezone
from django.contrib.auth import logout

class UserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        if request.user.is_authenticated:
            timezone.activate(request.user.timezone)
            if not request.user.is_active:
                logout(request.user)
        else:
            timezone.deactivate()
        return self.get_response(request)
