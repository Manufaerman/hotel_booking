from django.contrib import admin
from .models import Room, Booking, Price, Day

# Register your models here.
admin.site.register(Room)

admin.site.register(Booking)

admin.site.register(Price)

admin.site.register(Day)