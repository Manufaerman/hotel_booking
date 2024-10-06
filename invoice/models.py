from django.db import models

# Create your models here.
class Invoice(models.Model):
    name = models.CharField(max_length=300),
    address = models.CharField(max_length=300),
