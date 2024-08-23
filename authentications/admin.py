from django.contrib import admin

#from . import models
from .models import *


# admin.site.register(models.UserModel)
# admin.site.register(models.UserProfile)

@admin.register(UserModel)
class UserModelAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'email', 'is_active', 'is_staff')
    search_fields = ('phone_number', 'email')
    list_filter = ('is_active', 'is_staff')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'address')
    search_fields = ('user__phone_number', 'first_name', 'last_name')