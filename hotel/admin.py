from django.contrib import admin
from .models import Flat, Habitacion, Inquilino, ContratoAlquiler, Gasto, Inventario, Iteminventario

from .models import Habitacion, MultimediaHabitacion
from django.contrib import admin
from .models import Planta, EventoPlanta, ComentarioPlanta
from .models import Proveedor
from .models import IngresoPropiedad


@admin.register(IngresoPropiedad)
class IngresoPropiedadAdmin(admin.ModelAdmin):

    list_display = [
        "fecha",
        "propiedad",
        "concepto",
        "pagador",
        "importe",
    ]

    list_filter = [
        "propiedad",
        "fecha",
    ]

    search_fields = [
        "concepto",
        "pagador",
        "propiedad__nombre",
    ]

    date_hierarchy = "fecha"

    ordering = [
        "-fecha",
        "-fecha_creacion",
    ]


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

    exclude = [
        "image1",
        "image2",
        "image3",
        "image4",
    ]

    inlines = [
        MultimediaHabitacionInline,
    ]




class EventoPlantaInline(admin.TabularInline):
    model = EventoPlanta
    extra = 0


class ComentarioPlantaInline(admin.TabularInline):
    model = ComentarioPlanta
    extra = 0


@admin.register(Planta)
class PlantaAdmin(admin.ModelAdmin):

    list_display = [
        'nombre_completo',
        'habitacion',
        'piso',
        'ubicacion',
        'estado',
        'publica',
    ]

    list_filter = [
        'estado',
        'publica',
        'piso',
    ]

    search_fields = [
        'nombre',
        'especie',
        'descripcion',
    ]

    readonly_fields = [
        'slug',
        'creada',
        'actualizada',
    ]

    inlines = [
        EventoPlantaInline,
        ComentarioPlantaInline,
    ]


@admin.register(EventoPlanta)
class EventoPlantaAdmin(admin.ModelAdmin):

    list_display = [
        'planta',
        'tipo',
        'titulo',
        'fecha',
        'publico',
    ]

    list_filter = [
        'tipo',
        'publico',
    ]


@admin.register(ComentarioPlanta)
class ComentarioPlantaAdmin(admin.ModelAdmin):

    list_display = [
        'planta',
        'nombre',
        'aprobado',
        'creado',
    ]

    list_filter = [
        'aprobado',
    ]

    search_fields = [
        'nombre',
        'mensaje',
    ]


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):

    list_display = [
        "nombre",
        "pais",
        "activo",
    ]

    list_filter = [
        "pais",
        "activo",
    ]

    search_fields = [
        "nombre",
    ]

    ordering = [
        "pais",
        "nombre",
    ]