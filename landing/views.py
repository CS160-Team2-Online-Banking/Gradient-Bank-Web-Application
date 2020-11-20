from django.shortcuts import render
from django.views import View
from api_requests.api_requests import *
from messenger import utils

class Landing(View):
    def get(self, request, *args, **kwargs):
        username = ""
        result = []
        if request.user.is_authenticated:
            username = request.user.username

            result = api_get_accounts(request.user)
            if not result:
                result = []
        else:
            username = 'Guest'
        
        return render(request, 'landing/landing.html', {"account_list": result, "username": username})


landing = Landing.as_view()
