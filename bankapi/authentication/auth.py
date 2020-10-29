from django.conf import settings
import jwt

def decrypt_auth_token(request):
    auth_token = request.COOKIES.get('auth_token')
    decrypted_token = jwt.decode(auth_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGO])
    return decrypted_token

def decrypt_auth_token_str(str):
    decrypted_token = jwt.decode(str, settings.JWT_SECRET, algorithms=[settings.JWT_ALGO])
    return decrypted_token

def encrpyt_auth_token(userid, expiration):
    encrpyted_token = jwt.encode({"user_id": userid, "expires": expiration}, settings.JWT_SECRET, algorithm=settings.JWT_ALGO).decode('utf-8')
    return encrpyted_token
