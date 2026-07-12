from django.contrib import admin
from .models import Flat, Habitacion, Inquilino, ContratoAlquiler, Gasto

# Register your models here.
class AdminHabitacion(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'propiedad', 'disponible']

admin.site.register(Habitacion, AdminHabitacion)

class AdminInquilino(admin.ModelAdmin):
    list_display = ['id', 'nombre']

admin.site.register(Inquilino, AdminInquilino)

class AdminContratoAlquiler(admin.ModelAdmin):
    list_display = ['id', 'habitacion', 'inquilino', 'fecha_inicio', 'fecha_fin']

admin.site.register(ContratoAlquiler, AdminContratoAlquiler)

class RoomAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'category', 'capacity']

admin.site.register(Flat, RoomAdmin)

@admin.register(Gasto)
class GastoAdmin(admin.ModelAdmin):
    list_display = (
        "propiedad",
        "habitacion",
        "concepto",
        "categoria",
        "importe",
        "fecha",
        "pagado",
    )

    list_filter = (
        "propiedad",
        "categoria",
        "pagado",
        "fecha",
    )

    search_fields = (
        "concepto",
        "notas",
    )




