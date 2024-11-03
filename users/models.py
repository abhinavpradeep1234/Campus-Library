from django.db import models

# Create a Custom model  to explore more features rather than User
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    ROLE = (("ADMIN", "ADMIN"),)
    role = models.CharField(max_length=20, choices=ROLE, null=True, blank=True)
    Confirm_password = models.CharField(max_length=15)
    image = models.ImageField(upload_to="new_library", default="static/image/logo.png")


class Notification(models.Model):
    username = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    notification = models.TextField()
    time = models.DateTimeField(auto_now=True)
    is_mark = models.BooleanField(default=False)
    
