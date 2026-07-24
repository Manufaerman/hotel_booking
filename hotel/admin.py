from django.contrib import admin
from .models import Flat, Habitacion, Inquilino, ContratoAlquiler, Gasto, Inventario, Iteminventario

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


class  InventarioAdmin(admin.ModelAdmin):
    list_display = ['habitacion', 'item', 'cantidad', 'observaciones']


admin.site.register(Inventario, InventarioAdmin)


class ItemAdmin(admin.ModelAdmin):
    list_display = ['nombre']


admin.site.register(Iteminventario, ItemAdmin)


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




