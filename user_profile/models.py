from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True,)
    phone = models.IntegerField(blank=True, null=True)
    dni = models.IntegerField(blank=True, null=True)
    address = models.CharField(blank=True, max_length=150, null=True)
    cp = models.IntegerField(blank=True, null=True)
    city = models.CharField(blank=True, max_length=150, null=True)
    country = models.CharField(blank=True, max_length=150, null=True)
    birthday = models.DateField(blank=True,null=True)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            UserProfile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.UserProfile.save()

