from django.contrib import admin
from .models import Room, Booking, Price

# Register your models here.
class RoomAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'category', 'bed', 'capacity']

admin.site.register(Room, RoomAdmin)

class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'room', 'check_in', 'check_out']

admin.site.register(Booking, BookingAdmin)

class PriceAdmin(admin.ModelAdmin):
    list_display = ['price', 'date_price', 'room']
    list_filter = ['date_price', 'room',]

admin.site.register(Price, PriceAdmin)

