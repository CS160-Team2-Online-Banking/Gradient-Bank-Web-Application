from django.shortcuts import render
from django.views import View


class AtmList(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'atm/atm_list.html')


atm_list = AtmList.as_view()
