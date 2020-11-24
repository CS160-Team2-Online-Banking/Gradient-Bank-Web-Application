from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.db.models.functions import Now
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

from bankapi.transaction.transaction import TransactionProcess
from functools import update_wrapper
from bankapi.transfer.exchange_processor import *
from bankapi.authentication.auth import *
from bankapi.logging.logging import log_event, create_event
from bankapi.account.account_process import AccountProcess
from bankapi.autopayment.autopayment import AutopaymentBuilder
from django.utils.decorators import classonlymethod
from django.shortcuts import render, redirect
from bankapi.reports.reports import *
from django.contrib import messages
from .forms import *
import traceback


def returns_json_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            traceback.print_exc()
            return JsonResponse({"success": False, "msg": "Error: request could not be processed"}, status=500)

    return wrapper


class APIView(View):
    restful_access_names = ["get", "put", "patch", "delete"]

    @classonlymethod
    def as_access_view(cls, **initkwargs):
        """ Modified version of the as_view() method that generates handlers that only support RESTful operations"""
        # Code is similar to that found in https://github.com/django/django/blob/master/django/views/generic/base.py#L31

        # error handlers take directly from django.views.generic.base.as_view():
        for key in initkwargs:
            if key in cls.http_method_names:
                raise TypeError(
                    'The method name %s is not accepted as a keyword argument '
                    'to %s().' % (key, cls.__name__)
                )
            if not hasattr(cls, key):
                raise TypeError("%s() received an invalid keyword %r. as_view "
                                "only accepts arguments that are already "
                                "attributes of the class." % (cls.__name__, key))

        def view(request, *args, **kwargs):
            self = cls(**initkwargs)
            if hasattr(self, 'get') and not hasattr(self, 'head'):
                self.head = self.get
            self.request = request
            self.args = args
            self.kwargs = kwargs
            return self.access_dispatcher(request, *args, **kwargs)

        # more code to handle view intialization taken from django.views.generic.base.as_view()
        view.view_class = cls
        view.view_initkwargs = initkwargs

        update_wrapper(view, cls, updated=())
        update_wrapper(view, cls.dispatch, assigned=())
        return view

    @classonlymethod
    def as_post_view(cls, **initkwargs):

        for key in initkwargs:
            if key in cls.http_method_names:
                raise TypeError(
                    'The method name %s is not accepted as a keyword argument '
                    'to %s().' % (key, cls.__name__)
                )
            if not hasattr(cls, key):
                raise TypeError("%s() received an invalid keyword %r. as_view "
                                "only accepts arguments that are already "
                                "attributes of the class." % (cls.__name__, key))

        def view(request, *args, **kwargs):
            self = cls(**initkwargs)
            self.request = request
            self.args = args
            self.kwargs = kwargs
            if request.method.lower() == "post":
                handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed
            return handler(request, *args, **kwargs)

        view.view_class = cls
        view.view_initkwargs = initkwargs

        update_wrapper(view, cls, updated=())
        update_wrapper(view, cls.dispatch, assigned=())

        return view

    @classonlymethod
    def as_delete_view(cls, **initkwargs):
        """nothing but delete"""

        for key in initkwargs:
            if key in cls.http_method_names:
                raise TypeError(
                    'The method name %s is not accepted as a keyword argument '
                    'to %s().' % (key, cls.__name__)
                )
            if not hasattr(cls, key):
                raise TypeError("%s() received an invalid keyword %r. as_view "
                                "only accepts arguments that are already "
                                "attributes of the class." % (cls.__name__, key))

        def view(request, *args, **kwargs):
            self = cls(**initkwargs)
            self.request = request
            self.args = args
            self.kwargs = kwargs
            if request.method.lower() == "delete":
                handler = getattr(self, request.method.lower(),
                                  self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed
            return handler(request, *args, **kwargs)

        view.view_class = cls
        view.view_initkwargs = initkwargs

        update_wrapper(view, cls, updated=())
        update_wrapper(view, cls.dispatch, assigned=())

        return view

    def access_dispatcher(self, request, *args, **kwargs):
        if request.method.lower() in self.restful_access_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)


@method_decorator(csrf_exempt, name='dispatch')  # django requires all post requests to include a CSRF token by default
class TransferView(APIView):
    @returns_json_error
    def post(self, request):
        try:
            auth_token = decrypt_auth_token(request)
            json_data = json.loads(request.body)
        except json.decoder.JSONDecodeError:
            return JsonResponse({"success": False, "msg": "Error: JSON could not be parsed"}, status=400)

        if 'data' not in json_data:
            return JsonResponse({"success": False, "msg": "Error: Badly formatted body"}, status=400)

        data = json_data["data"]

        try:
            to_account_no = int(data["to_account_no"])
            to_routing_no = int(data["to_routing_no"])
            from_account_no = int(data["from_account_no"])
            from_routing_no = int(data["from_routing_no"])
            amount = data["amount"]
        except KeyError:
            return JsonResponse({"success": False, "msg": "Error: Body is missing parameters"}, status=400)
        except ValueError:
            return JsonResponse({"success": False, "msg": "Error: Invalid parameter type"}, status=400)

        request_info = {
            "from_routing_no": from_routing_no,
            "from_account_no": from_account_no,
            "to_routing_no": to_routing_no,
            "to_account_no": to_account_no,
            "amount": Decimal(amount),
        }
        event = create_event(request, auth_token, event_type=EventTypes.REQUEST_TRANSFER, data_id=None)
        result = ExchangeProcessor.start_exchange(request_info, auth_token, event)
        if result["success"]:
            return JsonResponse({"success": True, "data": result["data"]}, status=200)
        return JsonResponse({"success": False, "msg": "Error: transfer could not be processed"}, status=500)


@method_decorator(csrf_exempt, name='dispatch')  # django requires all post requests to include a CSRF token by default
class AutoPaymentView(APIView):
    """process HTTP action for auto payment"""

    @returns_json_error
    def post(self, request):
        try:
            auth_token = decrypt_auth_token(request)
            json_data = json.loads(request.body)
        except json.decoder.JSONDecodeError:
            return JsonResponse({"success": False, "msg": "Error: JSON could not be parsed"}, status=400)

        if 'data' not in json_data:
            return JsonResponse({"success": False, "msg": "Error: Badly formatted body"}, status=400)

        data = json_data["data"]
        try:

            to_account_no = int(data["to_account_no"])
            to_routing_no = int(data["to_routing_no"])
            from_account_no = int(data["from_account_no"])
            from_routing_no = int(data["from_routing_no"])

            transfer_amount = Decimal(data["transfer_amount"])
            payment_schedule_data = {
                "payment_frequency": data["payment_schedule_data"]["payment_frequency"],
                "start_date": data["payment_schedule_data"]["start_date"],
                "end_date": data["payment_schedule_data"]["end_date"],
            }
        except KeyError:
            return JsonResponse({"success": False, "msg": "Error: Body is missing parameters"}, status=400)
        except ValueError:
            return JsonResponse({"success": False, "msg": "Error: Invalid parameter type"}, status=400)

        payment_data = {
            "payment_schedule_data": payment_schedule_data,
            "from_routing_no": from_routing_no,
            "from_account_no": from_account_no,
            "to_routing_no": to_routing_no,
            "to_account_no": to_account_no,
            "transfer_amount": transfer_amount,
        }

        result = AutopaymentBuilder.build_autopayment(auth_token, payment_data)

        if result is None:
            return JsonResponse({"success": False, "msg": "Error: Server failed to process request"}, status=500)
        else:
            log_event(request, auth_token, event_type=EventTypes.SETUP_AUTOPAYMENT,
                      data_id=result[1])
            return JsonResponse({"success": True, "data": {"owner_id": result[0], "autopayment_id": result[1]}},
                                status=200)

    @staticmethod
    def try_set(key, src, dict, conv):
        if key in src:
            dict[key] = conv(src[key])

    @returns_json_error
    def put(self, request, autopayment_id):
        try:
            auth_token = decrypt_auth_token(request)
            json_data = json.loads(request.body)
        except json.decoder.JSONDecodeError:
            return JsonResponse({"success": False, "msg": "Error: JSON could not be parsed"}, status=400)

        if 'data' not in json_data:
            return JsonResponse({"success": False, "msg": "Error: Badly formatted body"}, status=400)
        data = json_data["data"]

        payment_data = dict()
        try:
            payment_data["autopayment_id"] = autopayment_id
            self.try_set("to_account_no", data, payment_data, int)
            self.try_set("to_routing_no", data, payment_data, int)
            self.try_set("from_account_no", data, payment_data, int)
            self.try_set("from_routing_no", data, payment_data, int)
            self.try_set("transfer_amount", data, payment_data, Decimal)
            if "payment_schedule_data" in data:
                payment_schedule_data = data["payment_schedule_data"]
                payment_schedule_deltas = dict()
                self.try_set("payment_frequency", payment_schedule_data, payment_schedule_deltas, str)
                self.try_set("start_date", payment_schedule_data, payment_schedule_deltas, str)
                self.try_set("end_date", payment_schedule_data, payment_schedule_deltas, str)
                payment_data["payment_schedule_data"] = payment_schedule_deltas
        except KeyError:
            return JsonResponse({"success": False, "msg": "Error: Body is missing parameters"}, status=400)
        except ValueError:
            return JsonResponse({"success": False, "msg": "Error: Invalid parameter type"}, status=400)

        result = AutopaymentBuilder.modify_autopayment(auth_token, payment_data)

        if result is None:
            return JsonResponse({"success": False, "msg": "Error: Server failed to process request"}, status=500)
        else:
            log_event(request, auth_token, event_type=EventTypes.EDIT_AUTOPAYMENT,
                      data_id=result[1])
            return JsonResponse({"success": True, "data": {"owner_id": result[0], "autopayment_id": result[1]}},
                                status=200)

    @returns_json_error
    def delete(self, request, autopayment_id):
        try:
            auth_token = decrypt_auth_token(request)
        except json.decoder.JSONDecodeError:
            return JsonResponse({"success": False, "msg": "Error: JSON could not be parsed"}, status=400)

        result = AutopaymentBuilder.cancel_autopayment(auth_token, autopayment_id)

        if result is None:
            return JsonResponse({"success": False, "msg": "Error: Server failed to process request"}, status=500)
        else:
            log_event(request, auth_token, event_type=EventTypes.CANCEL_AUTOPAYMENT)
            return JsonResponse({"success": True}, status=200)

    @returns_json_error
    def get(self, request, autopayment_id=None):
        """Get auto payment object
        """
        try:
            auth_token = decrypt_auth_token(request)
        except json.decoder.JSONDecodeError:
            return JsonResponse({"success": False, "msg": "Error: JSON could not be parsed"}, status=400)

        result = AutopaymentBuilder.get_autopayment(auth_token, autopayment_id)
        if result is None:
            return JsonResponse({"success": False, "msg": "Error: Server failed to process request"}, status=500)
        else:
            return JsonResponse({"success": True, "data": result}, status=200)


@method_decorator(csrf_exempt, name='dispatch')  # django requires all post requests to include a CSRF token by default
class TransactionView(View):
    @returns_json_error
    def post(self, request):
        try:
            auth_token = decrypt_auth_token_str(request.headers.get("authorization"))
            json_data = json.loads(request.body)
        except json.decoder.JSONDecodeError:
            return JsonResponse({"success": False, "msg": "Error: JSON could not be parsed"}, status=400)

        if 'data' not in json_data:
            return JsonResponse({"success": False, "msg": "Error: Badly formatted body"}, status=400)

        data = json_data["data"]
        try:
            transaction_data = {
                "card_account_number": data["card_account_number"],
                "merchant_id": data["card_account_number"],
                "card_network_id": data["card_network_id"],
                "amount": data["amount"],
                "time_stamp": data["time_stamp"]
            }
        except KeyError:
            return JsonResponse({"success": False, "msg": "Error: Body is missing parameters"}, status=400)
        except ValueError:
            return JsonResponse({"success": False, "msg": "Error: Invalid parameter type"}, status=400)

        transaction_handler = TransactionProcess(transaction_data)
        result = transaction_handler.queue_transaction(auth_token)

        if result is None:
            return JsonResponse({"success": False, "msg": "Error: server failed to process request"}, status=500)
        else:
            return JsonResponse({"success": True})


class ATMProcessorView(View):
    def get(self, request):
        form = ATMForm()
        return render(request, 'base_form.html', {"form": form, "form_title": "ATM Withdraw",
                                                  "action": "/api/atm"})

    @transaction.atomic(using='bank_data')
    def post(self, request):
        form = ATMForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
        else:
            messages.info(request, "One or more of the entered fields in invalid")
            return render(request, 'base_form.html', {"form": form, "form_title": "ATM Withdraw",
                                               "action": "/api/atm"})

        username = data["bank_username"]
        pin = data["bank_pin"]
        account_number = data["account_no"]
        amount = data["amount"]


        user = CustomUser.objects.filter(username=username).first()
        if user is None:
            messages.info(request, "Username or Pin is Invalid")
            return render(request, 'base_form.html', {"form": form, "form_title": "ATM Withdraw",
                                                      "action": "/api/atm"})

        customer_user = CustomerUser.objects.filter(pk=user.pk).first()
        if customer_user is None:
            messages.info(request, "Username or Pin is Invalid")
            return render(request, 'base_form.html', {"form": form, "form_title": "ATM Withdraw",
                                                      "action": "/api/atm"})

        bank_customer = Customer.objects.filter(pk=customer_user.pk).first()
        if bank_customer is None:
            messages.info(request, "Username or Pin is Invalid")
            return render(request, 'base_form.html', {"form": form, "form_title": "ATM Withdraw",
                                                      "action": "/api/atm"})

        if bank_customer.customer_pin == pin:
            account = Accounts.objects.filter(owner_id=bank_customer.pk, account_number=account_number).first()
            if account is None:
                messages.info(request, "Account Number is Invalid")
                return render(request, 'base_form.html', {"form": form, "form_title": "ATM Withdraw",
                                                          "action": "/api/atm"})

            if account.balance >= amount:
                ex = ExchangeHistory(to_account_no=000000000000,
                                     from_account_no=account.account_number,
                                     to_routing_no=000000000,
                                     from_routing_no=settings.BANK_ROUTING_NUMBER,
                                     amount=amount,
                                     posted=Now(),
                                     finished=Now(),
                                     atm_id=1,
                                     type=ExchangeHistory.ExchangeTypes.WITHDRAWAL,
                                     status=ExchangeHistory.ExchangeHistoryStatus.FINISHED)

                account.balance = account.balance - amount
                log_event(request, {"user_id": bank_customer.pk}, EventTypes.WITHDRAW_MONEY, ex.pk)
                ex.save()
                account.save()
                return redirect(to="/landing")
        else:
            messages.info(request, "Username or Pin is Invalid")
            return render(request, 'base_form.html', {"form": form, "form_title": "ATM Withdraw",
                                                      "action": "/api/atm"})




@method_decorator(csrf_exempt, name='dispatch')  # django requires all post requests to include a CSRF token by default
class AccountView(APIView):
    @returns_json_error
    def get(self, request, account_no=None):
        """ View method for retrieving account information """
        # Note: for each account, you should also retrieve the associated transfers to it
        # this way, people can see what the history of transactions are for the account
        # you can use ExchangeProcessor.get_exchange_history to do this
        try:
            auth_token = decrypt_auth_token(request)
        except json.decoder.JSONDecodeError:
            return JsonResponse({"success": False, "msg": "Error: JSON could not be parsed"}, status=400)

        result = AccountProcess.account_lookup(auth_token, account_no)
        if not result["success"]:
            return JsonResponse({"success": False, "msg": "Error: Server failed to process request"}, status=500)
        else:
            return JsonResponse({"success": True, "data": result["data"]}, status=200)

    @returns_json_error
    def post(self, request):
        """ View method for creating (opening) a new bank account """
        try:
            auth_token = decrypt_auth_token(request)
            json_data = json.loads(request.body)
        except json.decoder.JSONDecodeError:
            return JsonResponse({"success": False, "msg": "Error: JSON could not be parsed"}, status=400)

        if 'data' not in json_data:
            return JsonResponse({"success": False, "msg": "Error: Badly formatted body"}, status=400)

        data = json_data["data"]
        #user_id = auth_token
        try:
            account_data = {
                #"account_id": data["account_id"],
                #"balance": 0,
                #"account_number": new_account_number,
                "account_type": data["account_type"]
                #"owner": user_id
            }
        except KeyError:
            return JsonResponse({"success": False, "msg": "Error: Body is missing parameters"}, status=400)
        except ValueError:
            return JsonResponse({"success": False, "msg": "Error: Invalid parameter type"}, status=400)
        result = AccountProcess.account_add(auth_token, account_data)
        if result["success"]:
            log_event(request, auth_token, EventTypes.CREATE_ACCOUNT, result["data"]["account_id"])
            return JsonResponse({"success": True, "data": result["data"]}, status=200)
        return JsonResponse({"success": False, "msg": "Error: Server failed to process request"}, status=500)
        #pass

    def delete(self, request, account_no=None):
        """ View method for creating (opening) a new bank account """
        try:
            auth_token = decrypt_auth_token(request)
            json_data = json.loads(request.body)
        except json.decoder.JSONDecodeError:
            return JsonResponse({"success": False, "msg": "Error: JSON could not be parsed"}, status=400)

        if 'data' not in json_data:
            return JsonResponse({"success": False, "msg": "Error: Badly formatted body"}, status=400)

        data = json_data["data"]
        # user_id = auth_token
        try:
            account_data = {
                "account_number": data["account_number"],
                # "owner": user_id
            }
        except KeyError:
            return JsonResponse({"success": False, "msg": "Error: Body is missing parameters"}, status=400)
        except ValueError:
            return JsonResponse({"success": False, "msg": "Error: Invalid parameter type"}, status=400)

        result = AccountProcess.close_account(auth_token, account_data)

        if result["success"]:
            log_event(request, auth_token, EventTypes.CLOSE_ACCOUNT, result["data"]["account_id"])
            return JsonResponse({"success": True}, status=200)
        else:
            return JsonResponse({"success": False, "msg": "Error: Server failed to process request"}, status=500)


@method_decorator(csrf_exempt, name='dispatch')  # django requires all post requests to include a CSRF token by default
class ReportView(View):
    @returns_json_error
    def get(self, request, datatype):
        try:
            auth_token = decrypt_auth_token(request)
        except json.decoder.JSONDecodeError:
            return JsonResponse({"success": False, "msg": "Error: JSON could not be parsed"}, status=400)

        manager_id = auth_token.get("manager_id", None)
        if manager_id is None:
            return JsonResponse({"success": False, "msg": "Error: Access Denied"}, status=400)

        executor = dispatch_report(datatype)
        result = executor(auth_token, **request.GET.dict())
        return JsonResponse(result, status=200)

        # select our query parameter

"""
# This class is depricated and should be deleted
@method_decorator(csrf_exempt, name='dispatch')  # django requires all post requests to include a CSRF token by default
class AuthView(View):
    def post(self, request):  # grant authentication if the user entered the correct password and email
        try:
            json_data = json.loads(request.body)
        except json.decoder.JSONDecodeError:
            return JsonResponse({"success": False, "msg": "Error: JSON could not be parsed"}, status=400)

        if "password" in json_data and "username" in json_data:
            # this is NOT  meant to be a production ready security token provider, this is a debug provider

            encrpyted_token = encrpyt_auth_token(1, 2)

            json_data = {"success": True}
            response = JsonResponse(json_data)
            response.set_cookie(key='auth_token', value=encrpyted_token)
            return response
        else:
            return JsonResponse({"success": False, "msg": "Error: No password or username provided"}, status=400)
"""