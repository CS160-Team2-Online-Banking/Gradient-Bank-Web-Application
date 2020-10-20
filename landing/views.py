from django.shortcuts import render
from django.views import View


class Landing(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'landing/landing.html')


landing = Landing.as_view()
