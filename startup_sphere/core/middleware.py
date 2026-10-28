from django.conf import settings
from django.contrib.auth import get_user_model, login

class AutoLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.DEBUG and '_as_user' in request.GET:
            User = get_user_model()
            try:
                user = User.objects.get(username=request.GET['_as_user'])
                request.user = user
                login(request, user)
            except Exception as e:
                pass
        return self.get_response(request)
