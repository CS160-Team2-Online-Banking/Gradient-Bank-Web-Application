from django.shortcuts import render
from django.views import View
from api_requests.api_requests import *

class Landing(View):
    def get(self, request, *args, **kwargs):
        result = []
        if request.user.is_authenticated:
            result = api_get_accounts(request.user)
            if not result:
                result = []
        return render(request, 'landing/landing.html', {"account_list": result})


landing = Landing.as_view()
