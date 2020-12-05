from django.shortcuts import render
from django.views import View
from accounts.auth_helpers import *
from django.utils.decorators import method_decorator


@method_decorator(customer_login_required, name='dispatch')
class AtmList(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'atm/atm_list.html')


atm_list = AtmList.as_view()
