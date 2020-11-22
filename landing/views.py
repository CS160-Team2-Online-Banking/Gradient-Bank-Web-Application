from django.shortcuts import render
from django.views import View
from api_requests.api_requests import *
from messenger import utils

class Landing(View):
    def get(self, request, *args, **kwargs):
        username = ""
        result = []
        auto_pay_list = []
        if request.user.is_authenticated:
            username = request.user.username
            result = api_get_accounts(request)
            # auto payment list
            auto_pay_list = api_get_autopayment_details(request, None)
            print('auto_pay_list', auto_pay_list)

            if not result:
                result = []
        else:
            username = 'Guest'
        
        return render(request, 'landing/landing.html', {"account_list": result, 
                                                        "auto_list": auto_pay_list, 
                                                        "username": username})


landing = Landing.as_view()
