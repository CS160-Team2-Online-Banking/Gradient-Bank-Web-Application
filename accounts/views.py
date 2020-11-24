from django.shortcuts import render
from django.views import View
from django.http import Http404, HttpResponseForbidden
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib.auth import login, logout
from django.contrib import messages
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
            return redirect("/managerportal/landing")
        return render(self.request, "registration/login.html",
                      {"form": form, "error": "The Username or Password you entered is incorrect"})


class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomerUser
    form_class = CustomerUserChangeForm
    template_name = 'accounts/customeruser_edit_form.html'
    success_url = '/landing'

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        queryset = queryset.filter(pk=self.request.user)  # return only the objects associated with the logged in user

        try:
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404("No such user exists")
        return obj

    def form_valid(self, form):
        user = self.request.user
        if CustomerUser.objects.filter(pk=user.pk).exists():
            form.save()
            messages.info(self.request, "You're account information has been successfully updated")
        return redirect(to="/landing")


class CustomerCloseView(View):
    def post(self, request):
        user = request.user
        if user.is_authenticated and Customer.objects.filter(pk=user.pk).exists():
            user = CustomUser.objects.filter(pk=user.pk).first()
            if user is not None:
                user.is_active = False  # we do soft account closes
                cust_data = Customer.objects.filter(pk=user.pk).first()
                cust_data.closed = True
                user.save()
                cust_data.save()
                logout(request)
                messages.info(request, "Your account has been closed. You will no longer be able to login/access the information in it")
                return redirect(to="/landing")
        return HttpResponseForbidden()


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
        return redirect('/managerportal/landing')


class CustomerSignUp(CreateView):
    model = CustomerUser
    form_class = CustomerUserCreationForm

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.register_user()
        login(self.request, user)
        return redirect('/landing')

class EditCustomerInfo(View):
    def get(self, request):
        pass

    def post(self, request):
        pass


signup = CustomerSignUp.as_view()
