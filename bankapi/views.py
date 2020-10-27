from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from bankapi.authentication.auth import decrypt_auth_token, encrpyt_auth_token
from bankapi.utils.network_utils import get_requestor_ip, get_utc_now_str
from bankapi.transfer.internal_process import InternalTransfer


from django.db.models.functions import Now
# Create your views here.

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
        print(json_data)
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
        InternalTransfer(request_info).queue_transfer(auth_token)  # attempt to queue the transfer
        return JsonResponse(request_info)


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