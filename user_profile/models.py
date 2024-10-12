from django.conf import settings
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True,)
    phone = models.IntegerField(blank=True, null=True)
    dni = models.IntegerField(blank=True, null=True)
    address = models.CharField(blank=True, max_length=150, null=True)
    cp = models.IntegerField(blank=True, null=True)
    city = models.CharField(blank=True, max_length=150, null=True)
    country = models.CharField(blank=True, max_length=150, null=True)
    birthday = models.DateField(blank=True)

