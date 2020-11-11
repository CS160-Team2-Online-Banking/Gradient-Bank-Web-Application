from urllib.request import *
from urllib.error import *
from django.conf import settings
from datetime import datetime, timedelta
from decimal import *
import jwt
import json
origin = "http://127.0.0.1:8000"
API_PATH = "{origin}/api".format(origin=origin)
EXPIRE_TIME = timedelta(minutes=5)

'''
class settings:
    JWT_SECRET = "j*qV)m}9'NRYV:[\@T2]'QQux5:~Ynn.uMjBA2E\tP*[cd&MR;qWbq<MqP?kca?*"
    JWT_ALGO = 'HS256'
    BANK_ROUTING_NUMBER = 123456789


class DummyUser:
    is_authenticated = True
    id = 1
'''

def attach_auth_token(user, request):
    if user.is_authenticated:
        userid = user.id
        expiration = datetime.utcnow() + EXPIRE_TIME
        encrpyted_token = jwt.encode({"user_id": userid, "expires": expiration.isoformat()}, settings.JWT_SECRET,
                                     algorithm=settings.JWT_ALGO).decode('utf-8')
        request.add_header("Cookie", "auth_token={token}".format(token=encrpyted_token))
        return request
    else:
        raise ValueError("User object must be authenticated")


def add_json_body(request, data: dict):
    request.add_header('Content-Type', 'application/json')
    payload_text = str.encode(json.dumps(data))
    request.data = payload_text
    return request


def api_post_account(user, account_type):
    req = Request
    payload = {"data": {
            "account_type": account_type
    }}
    req = Request(url="{path}/accounts".format(path=API_PATH), method='POST')
    attach_auth_token(user, req)
    add_json_body(req, payload)
    try:
        response = urlopen(req)
        if response.status < 300:
            data = json.loads(response.read())
            if data["success"]:
                return True
        return False
    except HTTPError as e:
        return False


def api_get_accounts(user):
    req = Request(url="{path}/accounts/".format(path=API_PATH))
    attach_auth_token(user, req)
    try:
        response = urlopen(req)
        if response.status < 300:
            data = json.loads(response.read())
            if data["success"]:
                return data["data"]
        return False
    except HTTPError as e:
        return False


def api_get_account_details(user, account_no):
    req = Request(url="{path}/accounts/{id}".format(path=API_PATH, id=account_no))
    attach_auth_token(user, req)
    try:
        response = urlopen(req)
        if response.status < 300:
            data = json.loads(response.read())
            if data["success"]:
                return data["data"]
        return False
    except HTTPError as e:
        return False


def api_setup_autopayment(user, to_account_no, to_account_routing, from_account_no, amount, start_date, end_date,
                          frequency):
    req = Request(url="{path}/autopayments".format(path=API_PATH), method='POST')
    attach_auth_token(user, req)
    payload = {"data": {
        "to_account_no": to_account_no,
        "to_routing_no": to_account_routing,
        "from_account_no": from_account_no,
        "from_routing_no": settings.BANK_ROUTING_NUMBER,
        "transfer_amount": amount,
        "payment_schedule_data": {
            "payment_frequency": frequency,
            "start_date": start_date,
            "end_date": end_date
        }
    }}
    add_json_body(req, payload)
    try:
        response = urlopen(req)
        if response.status < 300:
            data = json.loads(response.read())
            if data["success"]:
                return True
        return False
    except HTTPError as e:
        return False



def api_get_autopayments(user):
    req = Request(url="{path}/autopayments/".format(path=API_PATH))
    attach_auth_token(user, req)
    try:
        response = urlopen(req)
        if response.status < 300:
            data = json.loads(response.read())
            if data["success"]:
                return data["data"]
        return False
    except HTTPError as e:
        return False


def api_get_autopayment_details(user, id):
    req = Request(url="{path}/autopayments/{id}".format(path=API_PATH, id=id))
    attach_auth_token(user, req)
    try:
        response = urlopen(req)
        if response.status < 300:
            data = json.loads(response.read())
            if data["success"]:
                return data["data"]
        return False
    except HTTPError as e:
        return False


def api_post_transfer(user, to_account_no, to_account_routing, from_account_no, amount):
    req = Request(url="{path}/transfers".format(path=API_PATH), method='POST')
    attach_auth_token(user, req)
    payload = {"data": {
        "to_account_no": to_account_no,
        "to_routing_no": to_account_routing,
        "from_account_no": from_account_no,
        "from_routing_no": settings.BANK_ROUTING_NUMBER,
        "amount": amount,
    }}
    add_json_body(req, payload)
    try:
        response = urlopen(req)
        if response.status < 300:
            data = json.loads(response.read())
            if data["success"]:
                return True
        return False
    except HTTPError as e:
        return False
