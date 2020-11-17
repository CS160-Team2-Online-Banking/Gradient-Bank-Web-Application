from django.shortcuts import render
from django.views import View
from api_requests.api_requests import *
from messenger import utils

class Landing(View):
    def get(self, request, *args, **kwargs):
        """
        We do 2 things here.
        1> sync 2 db
        2> assign bankapi token
        """
        username = ""
        result = []
        if request.user.is_authenticated:
            username = request.user.username
            # if user is not a customer -> add to customer
            if not utils.is_customer(request.user):
                added = utils.add_customer(request.user)
                if not added:
                    print('>>>>>>>>>>>>>>>>')
                    print(f'Fail to add {request.user.username} into Customer')
                    print('>>>>>>>>>>>>>>>>')
            # customer will contains user at this point
            token = utils.get_bankapi_token(request.user, 5)
            request = utils.add_bankapi_token(request, token)

            #TODO: Here is the old stuffs which gets the result from account
            # but when I try it, it keep giving me "connection refuse"
            # above(line 13:23) is adding user into customer
            # need to confirm on the following code later

            # result = api_get_accounts(request.user)
            # if not result:
            #     result = []
            
        else:
            username = 'Guest'
        
        return render(request, 'landing/landing.html', {"account_list": result, "username": username})


landing = Landing.as_view()
