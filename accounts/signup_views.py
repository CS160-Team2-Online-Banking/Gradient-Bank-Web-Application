from django.shortcuts import render
from django.views import View


class SignUp(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'account/sign-up.html')


signup = SignUp.as_view()