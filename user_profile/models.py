from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True,)
    telefono = models.IntegerField(blank=True, null=True)
    dni = models.IntegerField(blank=True, null=True)
    direccion = models.CharField(blank=True, max_length=150, null=True)
    cp = models.IntegerField(blank=True, null=True)
    ciudad = models.CharField(blank=True, max_length=150, null=True)
    pais = models.CharField(blank=True, max_length=150, null=True)
    cumpleaños = models.DateField(blank=True,null=True)




