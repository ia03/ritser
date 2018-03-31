from django.utils import timezone

class TimeZoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        if request.user.is_authenticated:
            timezone.activate(request.user.timezone)
        else:
            timezone.deactivate()
        return self.get_response(request)