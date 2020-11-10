from django.shortcuts import render
from django.views import View
from api_requests.api_requests import *

class Landing(View):
    def get(self, request, *args, **kwargs):
        result = api_get_accounts(request.user)
        print(result)
        return render(request, 'landing/landing.html')


landing = Landing.as_view()
