from django.contrib import admin

# Register your models here.
from .models import CustomUser, BankManagerUser, CustomerUser


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username')


admin.site.register(CustomUser, CustomUserAdmin)

