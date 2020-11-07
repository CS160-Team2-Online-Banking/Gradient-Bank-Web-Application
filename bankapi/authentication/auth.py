from django.conf import settings
from datetime import *
import jwt


def decrypt_auth_token(request):
    auth_token = request.COOKIES.get('auth_token')
    decrypted_token = jwt.decode(auth_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGO])
    # TODO: throw an exception if the expiration date has passed
    """
    current_time = datetime.utcnow()
    expire_date = datetime.strptime(decrypted_token["expires"])  # this parses iso format strings by default
    if current_time > expire_date:
        throw ValueError("the auth token specified has expired")
    """
    return decrypted_token


def decrypt_auth_token_str(str):
    decrypted_token = jwt.decode(str, settings.JWT_SECRET, algorithms=[settings.JWT_ALGO])
    # TODO: throw an exception if the expiration date has passed
    """
    current_time = datetime.utcnow()
    expire_date = datetime.strptime(decrypted_token["expires"])  # this parses iso format strings by default
    if current_time > expire_date:
        throw ValueError("the auth token specified has expired")
    """
    return decrypted_token


def encrpyt_auth_token(userid, expiration):
    encrpyted_token = jwt.encode({"user_id": userid, "expires": expiration}, settings.JWT_SECRET,
                                 algorithm=settings.JWT_ALGO).decode('utf-8')
    return encrpyted_token
