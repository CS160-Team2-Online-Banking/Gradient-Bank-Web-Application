from django.shortcuts import render, redirect
from django.views import View
from api_requests.api_requests import *
from accounts.auth_helpers import *
from django.utils.decorators import method_decorator

from messenger import utils

class Landing(View):
    def get(self, request, *args, **kwargs):
        username = ""
        result = []
        auto_pay_list = []
        if request.user.is_authenticated and request.user.type == CustomUser.UserTypes.TYPE_CUSTOMER:
            username = request.user.username
            result = api_get_accounts(request)
            # auto payment list
            auto_pay_list = api_get_autopayment_details(request, None)
            if auto_pay_list:
                account_by_id = dict(map(lambda x: (x["pk"], x), result))
                for payment in auto_pay_list:
                    payment["from_account_no"] = account_by_id.get(payment["from_account"], None)
                    if payment["from_account_no"]:
                        payment["from_account_no"] = payment["from_account_no"]["account_number"]
            else:
                auto_pay_list = []
            if not result:
                result = []
        elif request.user.is_authenticated and request.user.type == CustomUser.UserTypes.TYPE_MANAGER:
            return redirect('/managerportal/landing')
        else:
            username = 'Guest'
        
        return render(request, 'landing/landing.html', {"account_list": result, 
                                                        "auto_list": auto_pay_list, 
                                                        "username": username})


landing = Landing.as_view()
