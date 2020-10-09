from django.contrib import admin
from .models import SampleDB # Import SampleDB from models.py

admin.site.register(SampleDB)  # Register the model for Admin Page
