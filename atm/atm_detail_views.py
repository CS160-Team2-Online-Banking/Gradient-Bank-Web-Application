from django.shortcuts import render
from django.views import View


class AtmDetail(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'atm/atm_detail.html')


atm_detail = AtmDetail.as_view()
