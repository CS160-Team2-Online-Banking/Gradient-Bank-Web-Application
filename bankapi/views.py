from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

from bankapi.models import TransferTypes
from bankapi.transaction.transaction import TransactionProcess
from bankapi.authentication.auth import *
from bankapi.utils.network_utils import get_requestor_ip, get_utc_now_str
from bankapi.transfer.internal_process import InternalTransfer
from bankapi.transfer.external_process import ExternalTransfer
from bankapi.autopayment.autopayment import AutopaymentBuilder
from bankapi.account.internal_process import InternalAccount
from bankapi.account.external_process import ExternalAccount


@method_decorator(csrf_exempt, name='dispatch')  # django requires all post requests to include a CSRF token by default
class TransferView(View):
    def get(self, request):
        return JsonResponse({})

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
            to_account_id = int(data["to_account_id"])
            from_account_id = int(data["from_account_id"])
            amount = data["amount"]
        except KeyError:
            return JsonResponse({"success": False, "msg": "Error: Body is missing parameters"}, status=400)
        except ValueError:
            return JsonResponse({"success": False, "msg": "Error: Invalid parameter type"}, status=400)

        request_info = {
            "to_account_id": to_account_id,
            "from_account_id": from_account_id,
            "amount": amount,
            "event_info": {
                "request_ip4": "",
                "request_ip6": "",
                "request_time": get_utc_now_str()
            }
        }

        # attempt to queue the transfer
        if "transfer_type" in data:
            transfer_type = data["transfer_type"]
            if transfer_type == TransferTypes.U_TO_U or transfer_type == TransferTypes.A_TO_A:
                InternalTransfer(request_info).queue_transfer(auth_token)
            elif transfer_type == TransferTypes.EXTERN:
                ExternalTransfer(request_info).queue_transfer(auth_token)
        else:
            InternalTransfer(request_info).queue_transfer(auth_token)

        return JsonResponse({"success": True, "data": request_info}, status=200)

@method_decorator(csrf_exempt, name='dispatch')  # django requires all post requests to include a CSRF token by default
class AutoPaymentView(View):
    def get(self):
        pass

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
            to_account_id = int(data["to_account_id"])
            from_account_id = int(data["from_account_id"])
            transfer_amount = data["transfer_amount"]
            transfer_type = data["transfer_type"]
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
            "from_account_id": from_account_id,
            "to_account_id": to_account_id,
            "transfer_amount": transfer_amount,
            "transfer_type": transfer_type
        }

        result = AutopaymentBuilder.build_autopayment(auth_token, payment_data)

        if result is None:
            return JsonResponse({"success": False, "msg": "Error: Server failed to process request"}, status=500)
        else:
            return JsonResponse({"success": True, "data":{"owner_id": result[0], "autopayment_id": result[1]}}, status=200)



@method_decorator(csrf_exempt, name='dispatch')  # django requires all post requests to include a CSRF token by default
class TransactionView(View):
    def get(self):
        pass

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
            print("accepted")
            return response
        else:
            return JsonResponse({"success": False, "msg": "Error: No password or username provided"}, status=400)