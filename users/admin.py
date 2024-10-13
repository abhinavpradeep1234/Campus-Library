from django.contrib import admin

# Register your models here.
from .models import CustomUser,Notification

admin.site.register(CustomUser)
admin.site.register(Notification)
