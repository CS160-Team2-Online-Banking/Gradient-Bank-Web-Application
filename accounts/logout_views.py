from django.shortcuts import render
from django.views import View


class LogOut(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'account/logout.html')


logout = LogOut.as_view()
