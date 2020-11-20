from django.shortcuts import render
from django.views import View
from django.views.generic import CreateView
from django.shortcuts import redirect
from django.contrib.auth import login
from .forms import *
from .models import *

class SignUp(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'account/signup.html')


class ManagerSignUp(CreateView):
    model = BankManagerUser
    form_class = BankManagerUserCreationForm

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.register_user()
        login(self.request, user)
        return redirect('landing')


class CustomerSignUp(CreateView):
    model = CustomerUser
    form_class = CustomerUserCreationForm

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.register_user()
        login(self.request, user)
        return redirect('landing')


signup = CustomerSignUp.as_view()
