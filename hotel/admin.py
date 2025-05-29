from django.contrib import admin
from .models import Room, Booking, Habitacion, Inquilino, ContratoAlquiler

# Register your models here.
class AdminHabitacion(admin.ModelAdmin):
    list_display = ['id', 'nombre']

admin.site.register(Habitacion, AdminHabitacion)

class AdminInquilino(admin.ModelAdmin):
    list_display = ['id', 'nombre']

admin.site.register(Inquilino, AdminInquilino)

class AdminContratoAlquiler(admin.ModelAdmin):
    list_display = ['id', 'habitacion', 'inquilino', 'fecha_inicio', 'fecha_fin']

admin.site.register(ContratoAlquiler, AdminContratoAlquiler)

class RoomAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'category', 'bed', 'capacity']

admin.site.register(Room, RoomAdmin)

class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'room', 'check_in', 'check_out']

admin.site.register(Booking, BookingAdmin)



