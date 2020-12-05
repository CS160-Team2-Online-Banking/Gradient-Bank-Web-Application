from django.shortcuts import render
from django.views import View
from api_requests.api_requests import *
from django.shortcuts import redirect
from accounts.auth_helpers import *
from django.utils.decorators import method_decorator
from django.contrib import messages


@method_decorator(customer_login_required, name='dispatch')
class ViewAutopaymentDetails(View):
    def get(self, request, autopayment_id):
        if request.user.is_authenticated:
            result = api_get_autopayment_details(request, autopayment_id)

            if not result or not len(result):
                return render(request, 'feature_access_message.html', {"title": "Auopayment Details",
                                                                       "message": "payment could not be found"})
            return render(request, 'autopayment/details.html', {"payment": result[0],
                                                                "action": f'/autopayment/delete/{autopayment_id}'})
        else:
            return render(request, 'feature_access_message.html', {"title": "Auopayment Details",
                                                                   "message": "Please Login before viewing this payment"})


@method_decorator(customer_login_required, name='dispatch')
class AutopaymentDelete(View):
    def post(self, request, autopayment_id):
        if request.user.is_authenticated:
            result = api_delete_autopayment(request, autopayment_id)

            if result:
                messages.success(request, f'Auto payment {autopayment_id} has been deleted.')
            else:
                messages.error(request, f'Fail to delete auto payment {autopayment_id}.')
            return redirect(to="/landing/")


AutopaymentDelete = AutopaymentDelete.as_view()
AutopaymentDetails = ViewAutopaymentDetails.as_view()
