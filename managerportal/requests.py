from urllib.request import *
from urllib.error import *
from django.conf import settings
from datetime import datetime, timedelta
from decimal import *
import jwt
import json
from api_requests.api_requests import add_json_body
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


def attach_manager_token(user, manager, request):
    if user.is_authenticated:
        userid = user.id
        expiration = datetime.utcnow() + EXPIRE_TIME
        encrpyted_token = jwt.encode({"user_id": userid, "manager_id": manager.manager_id,
                                      "expires": expiration.isoformat()}, settings.JWT_SECRET,
                                     algorithm=settings.JWT_ALGO).decode('utf-8')
        request.add_header("Cookie", "auth_token={token}".format(token=encrpyted_token))
        return request
    else:
        raise ValueError("User object must be authenticated")


def api_post_account(user, manager, account_type):
    req = Request
    payload = {"data": {
            "account_type": account_type
    }}
    req = Request(url="{path}/accounts".format(path=API_PATH), method='POST')
    attach_manager_token(user, manager, req)
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


def api_get_data(user, manager, datatype, params):
    params_str=""
    if len(params):
        params_str = "?{params}".format(params=
                                        "&".join(list(map(
                                            lambda x: "{name}={value}".format(name=x[0], value=x[1]),
                                            params.items()))
                                            )
                                        )
    req = Request(url="{path}/reports/{datatype}{param_str}".format(path=API_PATH, datatype=datatype,
                                                                    params_str=params_str))
    attach_manager_token(user, manager, req)
    try:
        response = urlopen(req)
        if response.status < 300:
            data = json.loads(response.read())
            if data["success"]:
                return data["data"]
        return False
    except HTTPError as e:
        return False

