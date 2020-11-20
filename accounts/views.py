from django.shortcuts import render
from django.views import View
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.contrib.auth import login, logout
from .forms import *
from .models import *

class LogOut(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('/landing')

class SignInView(View):
    def get(self, request):
        return render(request, "accounts/login_redirect.html")


class EmployerSignIn(LoginView):
    def form_valid(self, form):
        user = form.get_user()

        if BankManagerUser.objects.filter(pk=user.pk).exists():
            login(self.request, user)
            return redirect("/landing")
        return render(self.request, "registration/login.html",
                      {"form": form, "error": "The Username or Password you entered is incorrect"})


class CustomerSignIn(LoginView):
    def form_valid(self, form):
        user = form.get_user()

        if CustomerUser.objects.filter(pk=user.pk).exists():
            login(self.request, user)
            return redirect("/landing")
        return render(self.request, "registration/login.html",
                      {"form": form, "error": "The Username or Password you entered is incorrect"})


class ManagerSignUp(CreateView):
    model = BankManagerUser
    form_class = BankManagerUserCreationForm

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.register_user()
        login(self.request, user)
        return redirect('/landing')


class CustomerSignUp(CreateView):
    model = CustomerUser
    form_class = CustomerUserCreationForm

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.register_user()
        login(self.request, user)
        return redirect('/landing')


signup = CustomerSignUp.as_view()
