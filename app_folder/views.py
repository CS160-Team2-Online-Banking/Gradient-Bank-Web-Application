from django.shortcuts import render
from django.views import View

class SampleView(View):
    def get(self, request, *args, **kwargs):
        context = {
            'message_from_backend': 'Hello World!',
        }

        return render(request, 'app_folder/top_page.html', context)
top_page = SampleView.as_view()
