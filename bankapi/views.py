from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.db.models.functions import Now
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

from bankapi.transaction.transaction import TransactionProcess
from bankapi.transfer.exchange_processor import *
from bankapi.authentication.auth import *
from bankapi.transfer.logging import *
from bankapi.autopayment.autopayment import AutopaymentBuilder


@method_decorator(csrf_exempt, name='dispatch')  # django requires all post requests to include a CSRF token by default
class TransferView(View):
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
        result = ExchangeProcessor.start_exchange(request_info, auth_token)
        print(result)
        if result["success"]:
            log_event(request, entry_type=EventTypes.TRANSFER_CREATE_REQUEST, associated_item=result["data"]["transfer_id"])
            return JsonResponse({"success": True, "data": request_info}, status=200)
        return JsonResponse({"success": False, "msg": "Error: transfer could not be processed"}, status=500)


@method_decorator(csrf_exempt, name='dispatch')  # django requires all post requests to include a CSRF token by default
class AutoPaymentView(View):
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
            return JsonResponse({"success": True, "data": {"owner_id": result[0], "autopayment_id": result[1]}},
                                status=200)

    @staticmethod
    def try_set(key, src, dict, conv):
        if key in src:
            dict[key] = conv(src[key])

    def put(self, request):
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
            autopayment_id = int(data["autopayment_id"])
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
            return JsonResponse({"success": True, "data": {"owner_id": result[0], "autopayment_id": result[1]}},
                                status=200)


@method_decorator(csrf_exempt, name='dispatch')  # django requires all post requests to include a CSRF token by default
class TransactionView(View):
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


'''
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
            print("accepted")
            return response
        else:
            return JsonResponse({"success": False, "msg": "Error: No password or username provided"}, status=400)
'''