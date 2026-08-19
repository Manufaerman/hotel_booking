from django.contrib import admin
from .models import Flat, Habitacion, Inquilino, ContratoAlquiler, Gasto, Inventario, Iteminventario

# Register your models here.







class AdminInquilino(admin.ModelAdmin):
    list_display = ['id', 'nombre']


admin.site.register(Inquilino, AdminInquilino)


class AdminContratoAlquiler(admin.ModelAdmin):
    list_display = ['id', 'habitacion', 'inquilino', 'fecha_inicio', 'fecha_fin']


admin.site.register(ContratoAlquiler, AdminContratoAlquiler)


class RoomAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'category', 'capacity', 'reparto_gastos']


admin.site.register(Flat, RoomAdmin)


class InventarioAdmin(admin.ModelAdmin):
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

from django.contrib import admin

from .models import Habitacion, MultimediaHabitacion


class MultimediaHabitacionInline(admin.TabularInline):
    model = MultimediaHabitacion
    extra = 1

    fields = [
        "imagen",
        "video",
        "titulo",
        "orden",
        "visible",
    ]

    ordering = ["orden"]


@admin.register(Habitacion)
class HabitacionAdmin(admin.ModelAdmin):
    list_display = [
        "nombre",
        "propiedad",
        "precio",
        "disponible",
        "grupo_cocina",
        "grupo_bano"
    ]

    list_filter = [
        "propiedad",
        "disponible",
    ]

    inlines = [
        MultimediaHabitacionInline,
    ]


