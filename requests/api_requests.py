from urllib.request import *

from django.conf import settings
from datetime import datetime, timedelta
import jwt
origin = "http://127.0.0.1:8000"
API_PATH = "{origin}/api/".format(origin=origin)
EXPIRE_TIME = timedelta(minutes=5)

def attach_auth_token(user, request):
    userid = user.pk
    expiration = datetime.utcnow() + EXPIRE_TIME
    encrpyted_token = jwt.encode({"user_id": userid, "expires": expiration.isoformat()}, settings.JWT_SECRET,
                                 algorithm=settings.JWT_ALGO).decode('utf-8')

    request.add_header()
    pass

def add_json_body(request):
    request.add_header('Content-Type', 'application/json')


def api_get_accounts(user):
    pass


def api_get_account_details(user, account_no):
    pass


def api_setup_autopayment(user, to_account_no, to_account_routing, from_account_no, amount, start_date, end_date,
                          frequency):

    pass


def api_get_autopayments(user):
    pass


def api_get_autopayment_details(user, id):
    pass


def api_post_transfer(user, to_account_no, to_account_routing, from_account_no, amount):
    pass

