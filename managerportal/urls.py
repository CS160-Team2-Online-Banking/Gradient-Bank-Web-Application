from django.urls import path
from  .views import *

app_name = 'managerportal'
urlpatterns = [
    path("landing", LandingView.as_view(), name="managerlanding")
]
