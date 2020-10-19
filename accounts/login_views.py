from django.shortcuts import render
from django.views import View


class Login(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'account/login.html')


login = Login.as_view()
