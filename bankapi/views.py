from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.conf import settings
import jwt
from bankapi.transfer.internal_process import InternalTransfer

from django.db.models.functions import Now
# Create your views here.

class TransferView(View):
    def get(self, request, id):
        data = {"id":id}
        return JsonResponse(data)

    def post(self, request):
        encoded_auth = request.headers['Authorization']
        decoded_auth = jwt.decode(encoded_auth, settings.JWT_SECRET, algorithms=settings.JWT_ALGO)
        data={}
        return JsonResponse(data)

class AuthView(View):
    def post(self, request): # grant authentication if the user entered the correct password and email

        return JsonResponse()