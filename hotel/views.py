import calendar
from datetime import  date
from decimal import Decimal, ROUND_HALF_UP
from urllib.parse import quote
from django.utils.http import url_has_allowed_host_and_scheme
from django.db.models import Count
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Exists, OuterRef, Sum, Prefetch, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView
from django.http import HttpResponseRedirect
from pathlib import Path
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from django.db.models import Q, Sum
from django.utils import timezone
from .services.cotizaciones import aplicar_conversion_gasto, CotizacionNoDisponible
from .forms import (
    AvalContratoForm,
    ContratoAlquilerForm,
    CrearProcesoFormalizacionForm,
    InquilinoForm, GastoForm, CompletarGastoPendienteForm, EditarGastoRecurrenteForm, ProyectoForm, IngresoPropiedadForm
)

from .models import (
    AvalContrato,
    ContratoAlquiler,
    Flat,
    Gasto,
    Habitacion,
    Inquilino,
    ProcesoFormalizacion,
    Visit,
    Planta,
    EventoPlanta,
    ComentarioPlanta,
    MultimediaHabitacion,
    GastoRecurrente, GastoPendiente, Proyecto, Proveedor, IngresoPropiedad
)

from .services.contrato_pdf import generar_contrato_pdf
from .services.gastos_recurrentes import generar_gastos_de_recurrente, generar_gastos_recurrentes
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from django.contrib.staticfiles import finders
from django.http import FileResponse, Http404


def service_worker(request):
    ruta = finders.find(
        "hotel/service-worker.js"
    )

    if not ruta:
        raise Http404(
            "No se encontró el service worker."
        )

    response = FileResponse(
        open(ruta, "rb"),
        content_type="application/javascript",
    )

    response["Service-Worker-Allowed"] = "/"
    response["Cache-Control"] = "no-cache"

    return response


@login_required
def proveedores_por_pais(request):
    pais = request.GET.get(
        "pais",
        "",
    ).strip().upper()

    if pais not in {
        "ES",
        "AR",
    }:
        return JsonResponse(
            {
                "proveedores": [],
            }
        )

    proveedores = list(
        Proveedor.objects
        .filter(
            pais=pais,
            activo=True,
        )
        .order_by("nombre")
        .values(
            "id",
            "nombre",
        )
    )

    return JsonResponse(
        {
            "proveedores": proveedores,
        }
    )

def finalizar_contrato(request, id):
    contrato = get_object_or_404(ContratoAlquiler, id=id)
    if request.method == 'POST':
        contrato.finalizar()
        messages.success(request, 'Contrato finalizado correctamente')

    return redirect('hotel:contratos')


def eliminar_contrato(request, id):
    contrato = get_object_or_404(ContratoAlquiler, id=id)
    if request.method == 'POST':
        contrato.delete()
        messages.success(request, 'Contrato eliminado correctamente.')
        return redirect('hotel:contratos')

    return render(request, 'hotel/confirmar_eliminar_contrato.html', {'contrato': contrato})


def modificar_contrato(request, id):
    contrato = get_object_or_404(
        ContratoAlquiler.objects.select_related(
            "habitacion",
            "habitacion__propiedad",
        ),
        pk=id,
    )

    if request.method == "POST":
        propiedad_id = request.POST.get(
            "propiedad"
        )

        form = ContratoAlquilerForm(
            request.POST,
            instance=contrato,
            propiedad_id=propiedad_id,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Contrato modificado correctamente.",
            )

            return redirect(
                "hotel:contratos"
            )

    else:
        propiedad_id = (
            contrato.habitacion.propiedad_id
        )

        form = ContratoAlquilerForm(
            instance=contrato,
            propiedad_id=propiedad_id,
            habitacion_id=(
                contrato.habitacion_id
            ),
        )

    return render(
        request,
        "modificar.html",
        {
            "form": form,
            "contrato": contrato,
        },
    )


def modificar_inquilino(request, id, contrato_id,):
    contrato = get_object_or_404(
        ContratoAlquiler,
        pk=contrato_id,
    )

    inquilino = get_object_or_404(
        Inquilino,
        pk=id,
    )

    if request.method == "POST":
        form = InquilinoForm(
            request.POST,
            instance=inquilino,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Inquilino modificado correctamente.",
            )

            return redirect(
                "hotel:contratos"
            )

    else:
        form = InquilinoForm(
            instance=inquilino,
        )

    return render(
        request,
        "modificar_inquilino.html",
        {
            "form": form,
            "contrato": contrato,
            "inquilino": inquilino,
        },
    )


def home(request):
    flats = Flat.objects.all()

    todas_las_habitaciones = (
        Habitacion.objects
        .select_related("propiedad")
        .prefetch_related("contratos")
        .order_by("propiedad__nombre", "nombre")
    )

    habitaciones_disponibles = (
        todas_las_habitaciones
        .filter(disponible=True)
        .exclude(contratos__activo=True)
        .distinct()
    )

    return render(
        request,
        "home.html",
        {
            "flat": flats,

            # Carrusel inferior: todas
            "habitaciones": todas_las_habitaciones,

            # Carrusel superior: solamente libres
            "habitaciones_disponibles": habitaciones_disponibles,
        },
    )


# =========================================================
# GALERÍA DE HABITACIÓN
# =========================================================

def habitacion_galeria(request, id):
    habitacion = get_object_or_404(
        Habitacion.objects
        .select_related(
            "propiedad",
        )
        .prefetch_related(
            "plantas",
            "propiedad__plantas",
        ),
        pk=id,
    )

    multimedia = (
        habitacion.galeria
        .filter(visible=True)
        .order_by("orden", "pk")
    )

    plantas_habitacion = (
        habitacion.plantas
        .filter(
            estado="activa",
            publica=True,
        )
    )

    plantas_compartidas = (
        habitacion.propiedad.plantas
        .filter(
            estado="activa",
            publica=True,
        )
        if habitacion.propiedad
        else Planta.objects.none()
    )

    return render(
        request,
        "habitacion_galeria.html",
        {
            "habitacion": habitacion,
            "multimedia": multimedia,
            "plantas_habitacion": plantas_habitacion,
            "plantas_compartidas": plantas_compartidas,
        },
    )


# =========================================================
# DETALLE PÚBLICO DE LA PLANTA
# =========================================================

class PlantaDetailView(DetailView):
    model = Planta
    template_name = "hotel/plantas/planta_detail.html"
    context_object_name = "planta"

    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        eventos_publicos = EventoPlanta.objects.filter(
            publico=True,
        ).order_by("-fecha", "-creado")

        comentarios_aprobados = ComentarioPlanta.objects.filter(
            aprobado=True,
        ).order_by("-creado")

        return (
            Planta.objects
            .filter(publica=True)
            .select_related(
                "habitacion",
                "habitacion__propiedad",
                "piso",
            )
            .prefetch_related(
                Prefetch(
                    "eventos",
                    queryset=eventos_publicos,
                ),
                Prefetch(
                    "comentarios",
                    queryset=comentarios_aprobados,
                ),
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        planta = self.object

        residente_actual_publico = None
        inicio_convivencia = None

        if planta.habitacion_id:
            contrato_actual = self.obtener_contrato_actual(
                planta.habitacion_id
            )

            if contrato_actual:
                residente_actual_publico = (
                    self.obtener_nombre_publico(
                        contrato_actual.inquilino
                    )
                )

                inicio_convivencia = (
                    contrato_actual.fecha_inicio
                )

        context.update(
            {
                "residente_actual_publico":
                    residente_actual_publico,

                "inicio_convivencia":
                    inicio_convivencia,
            }
        )

        return context

    @staticmethod
    def obtener_contrato_actual(habitacion_id):
        hoy = timezone.localdate()

        return (
            ContratoAlquiler.objects
            .filter(
                habitacion_id=habitacion_id,
                fecha_inicio__lte=hoy,
            )
            .filter(
                Q(fecha_fin__isnull=True) |
                Q(fecha_fin__gte=hoy)
            )
            .select_related("inquilino")
            .order_by("-fecha_inicio")
            .first()
        )

    @staticmethod
    def obtener_nombre_publico(inquilino):
        """
        Obtiene únicamente la primera palabra del nombre completo.
        Nunca muestra los apellidos.
        """
        if not inquilino:
            return None

        nombre_completo = (inquilino.nombre or "").strip()

        if not nombre_completo:
            return None

        return nombre_completo.split(maxsplit=1)[0]

def habitaciones_all(request):
    habitaciones = (
        Habitacion.objects
        .select_related("propiedad")
        .prefetch_related("contratos")
        .order_by("propiedad__nombre", "nombre")
    )

    habitaciones_tolima = habitaciones.filter(
        propiedad__nombre__icontains="Tolima",
    )

    habitaciones_barichara = habitaciones.filter(
        propiedad__nombre__icontains="Barichara",
    )

    habitaciones_haro = habitaciones.filter(
        propiedad__nombre__icontains="Haro",
    )

    return render(
        request,
        "habitaciones_all.html",
        {
            "habitaciones_tolima": habitaciones_tolima,
            "habitaciones_barichara": habitaciones_barichara,
            "habitaciones_haro": habitaciones_haro,
        },
    )

def flat_detail(request, id):
    piso = get_object_or_404(
        Flat,
        pk=id,
    )

    habitaciones = (
        Habitacion.objects
        .filter(propiedad=piso)
        .prefetch_related("contratos")
        .order_by("nombre")
    )

    habitaciones_disponibles = (
        habitaciones
        .filter(disponible=True)
        .exclude(contratos__activo=True)
        .distinct()
        .count()
    )

    return render(
        request,
        "flat.html",
        {
            "piso": piso,
            "habitaciones": habitaciones,
            "habitaciones_disponibles": habitaciones_disponibles,
        },
    )

def visitas_view(request):
    periodo = request.GET.get(
        "periodo",
        "30",
    )

    pais_seleccionado = request.GET.get(
        "pais",
        "",
    )

    region_seleccionada = request.GET.get(
        "region",
        "",
    )

    bot_regex = (
        r"bot|crawler|spider|slurp|bingpreview|"
        r"facebookexternalhit|whatsapp|telegrambot|"
        r"discordbot|linkedinbot|twitterbot|"
        r"googlebot|bingbot|yandex|baiduspider|"
        r"duckduckbot|semrush|ahrefs|mj12bot|"
        r"dotbot|petalbot|bytespider|uptimerobot|"
        r"headlesschrome|phantomjs|selenium|"
        r"python-requests|python-urllib|curl|wget"
    )

    visitas = (
        Visit.objects
        .exclude(
            user_agent__iregex=bot_regex
        )
        .exclude(
            path__startswith="/admin/"
        )
        .exclude(
            path__startswith="/static/"
        )
        .exclude(
            path__startswith="/dashboard/"
        )
        .exclude(
            path__startswith=(
                "/habitaciones_dashboard/"
            )
        )
        .exclude(
            path__startswith="/formalizacion/"
        )
        .order_by("-timestamp")
    )

    if periodo in {
        "1",
        "7",
        "30",
        "90",
    }:
        fecha_desde = (
            timezone.now()
            - timedelta(
                days=int(periodo)
            )
        )

        visitas = visitas.filter(
            timestamp__gte=fecha_desde
        )

    if pais_seleccionado:
        visitas = visitas.filter(
            country=pais_seleccionado
        )

    if region_seleccionada:
        visitas = visitas.filter(
            region=region_seleccionada
        )

    total_paginas = visitas.count()

    visitantes_unicos = (
        visitas
        .values("ip")
        .distinct()
        .count()
    )

    paises = (
        visitas
        .exclude(country__isnull=True)
        .exclude(country="")
        .values(
            "country",
            "country_code",
        )
        .annotate(
            total=Count("id"),
            visitantes=Count(
                "ip",
                distinct=True,
            ),
        )
        .order_by("-visitantes")[:12]
    )

    regiones = (
        visitas
        .exclude(region__isnull=True)
        .exclude(region="")
        .values(
            "region",
            "country",
        )
        .annotate(
            total=Count("id"),
            visitantes=Count(
                "ip",
                distinct=True,
            ),
        )
        .order_by("-visitantes")[:12]
    )

    ciudades = (
        visitas
        .exclude(city__isnull=True)
        .exclude(city="")
        .values(
            "city",
            "region",
            "country",
        )
        .annotate(
            total=Count("id"),
            visitantes=Count(
                "ip",
                distinct=True,
            ),
        )
        .order_by("-visitantes")[:12]
    )

    opciones_paises = (
        Visit.objects
        .exclude(country__isnull=True)
        .exclude(country="")
        .values_list(
            "country",
            flat=True,
        )
        .distinct()
        .order_by("country")
    )

    opciones_regiones = (
        Visit.objects
        .exclude(region__isnull=True)
        .exclude(region="")
    )

    if pais_seleccionado:
        opciones_regiones = (
            opciones_regiones.filter(
                country=pais_seleccionado
            )
        )

    opciones_regiones = (
        opciones_regiones
        .values_list(
            "region",
            flat=True,
        )
        .distinct()
        .order_by("region")
    )

    return render(
        request,
        "visitas.html",
        {
            "visitas": visitas[:100],
            "total_paginas": total_paginas,
            "visitantes_unicos": (
                visitantes_unicos
            ),
            "paises": paises,
            "regiones": regiones,
            "ciudades": ciudades,
            "opciones_paises": (
                opciones_paises
            ),
            "opciones_regiones": (
                opciones_regiones
            ),
            "periodo": periodo,
            "pais_seleccionado": (
                pais_seleccionado
            ),
            "region_seleccionada": (
                region_seleccionada
            ),
        },
    )

""" for the charts using jquery and js"""

def chart_data(request):
    hoy = timezone.localdate()
    inicio_mes_actual = hoy.replace(day=1)
    final_mes_actual = (
        inicio_mes_actual
        + relativedelta(months=1)
        - timedelta(days=1)
    )

    propiedades = (
        Flat.objects
        .all()
        .order_by("nombre")
    )

    # =====================================================
    # INGRESOS ACTUALES POR PROPIEDAD
    # =====================================================

    labels_propiedades = []
    ingresos_por_propiedad = []
    gastos_por_propiedad = []

    gastos_actuales = (
        Gasto.objects
        .filter(
            fecha__gte=inicio_mes_actual,
            fecha__lte=final_mes_actual,
            anulado=False,
            pais="ES",
        )
    )

    for propiedad in propiedades:
        labels_propiedades.append(
            propiedad.nombre
        )

        ingresos = (
            ContratoAlquiler.objects
            .filter(
                activo=True,
                habitacion__propiedad=propiedad,
            )
            .aggregate(
                total=Sum("precio_mensual"),
            )
            .get("total")
            or 0
        )
        ingresos_temporales = (
                IngresoPropiedad.objects
                .filter(
                    propiedad=propiedad,
                    fecha__gte=inicio_mes_actual,
                    fecha__lte=final_mes_actual,
                )
                .aggregate(
                    total=Sum("importe"),
                )
                .get("total")
                or 0
        )

        ingresos_totales_propiedad = (
                ingresos
                + ingresos_temporales
        )

        gastos = (
            gastos_actuales
            .filter(propiedad=propiedad)
            .aggregate(
                total=Sum("importe"),
            )
            .get("total")
            or 0
        )

        ingresos_por_propiedad.append(
            float(
                ingresos_totales_propiedad
            )
        )

        gastos_por_propiedad.append(
            float(gastos)
        )

    # =====================================================
    # INGRESOS Y GASTOS DE LOS ÚLTIMOS SEIS MESES
    # =====================================================

    meses_cortos = [
        "Ene",
        "Feb",
        "Mar",
        "Abr",
        "May",
        "Jun",
        "Jul",
        "Ago",
        "Sep",
        "Oct",
        "Nov",
        "Dic",
    ]

    labels_meses = []
    facturacion_mensual = []
    gastos_mensuales = []
    resultado_mensual = []

    for desplazamiento in range(5, -1, -1):
        inicio_mes = (
            inicio_mes_actual
            - relativedelta(
                months=desplazamiento,
            )
        )

        final_mes = (
            inicio_mes
            + relativedelta(months=1)
            - timedelta(days=1)
        )

        # Contratos que estuvieron vigentes durante ese mes.
        es_mes_actual = (
                inicio_mes.year == hoy.year
                and inicio_mes.month == hoy.month
        )

        if es_mes_actual:
            # Para el mes actual, el estado activo es la fuente
            # utilizada también por el KPI del dashboard.
            contratos_del_mes = (
                ContratoAlquiler.objects
                .filter(activo=True)
            )
        else:
            # Para meses históricos usamos las fechas del contrato.
            contratos_del_mes = (
                ContratoAlquiler.objects
                .filter(
                    fecha_inicio__lte=final_mes,
                )
                .filter(
                    Q(fecha_fin__isnull=True)
                    | Q(fecha_fin__gte=inicio_mes)
                )
            )

        ingresos_mes = (
                contratos_del_mes
                .aggregate(
                    total=Sum("precio_mensual"),
                )
                .get("total")
                or 0
        )
        ingresos_temporales_mes = (
                IngresoPropiedad.objects
                .filter(
                    fecha__gte=inicio_mes,
                    fecha__lte=final_mes,
                )
                .aggregate(
                    total=Sum("importe"),
                )
                .get("total")
                or 0
        )

        ingresos_mes = (
                ingresos_mes
                + ingresos_temporales_mes
        )

        gastos_mes = (
            Gasto.objects
            .filter(
                fecha__gte=inicio_mes,
                fecha__lte=final_mes,
                anulado=False,
                pais="ES",
            )
            .aggregate(
                total=Sum("importe"),
            )
            .get("total")
            or 0
        )

        labels_meses.append(
            meses_cortos[inicio_mes.month - 1]
        )

        facturacion_mensual.append(
            float(ingresos_mes)
        )

        gastos_mensuales.append(
            float(gastos_mes)
        )

        resultado_mensual.append(
            float(
                ingresos_mes - gastos_mes
            )
        )

    # =====================================================
    # GASTOS DEL MES POR CATEGORÍA
    # =====================================================

    gastos_agrupados = (
        gastos_actuales
        .values("categoria")
        .annotate(
            total=Sum("importe"),
        )
        .order_by("-total")
    )

    nombres_categorias = dict(
        Gasto.CATEGORIAS
    )

    categorias_labels = []
    categorias_valores = []

    for grupo in gastos_agrupados:
        categoria = grupo["categoria"]

        categorias_labels.append(
            nombres_categorias.get(
                categoria,
                categoria.replace(
                    "_",
                    " ",
                ).title(),
            )
        )

        categorias_valores.append(
            float(
                grupo["total"] or 0
            )
        )

    # =====================================================
    # RESUMEN DEL MES ACTUAL
    # =====================================================

    ingresos_mes_actual = sum(
        ingresos_por_propiedad
    )

    gastos_mes_actual = float(
        gastos_actuales
        .aggregate(
            total=Sum("importe"),
        )
        .get("total")
        or 0
    )

    resultado_mes_actual = (
        ingresos_mes_actual
        - gastos_mes_actual
    )

    porcentaje_gastos = (
        round(
            (
                gastos_mes_actual
                / ingresos_mes_actual
            )
            * 100,
            1,
        )
        if ingresos_mes_actual
        else 0
    )

    # =====================================================
    # RESPUESTA
    # =====================================================

    return JsonResponse(
        {
            "labels": labels_propiedades,

            # Compatibilidad con el gráfico existente.
            "datos": ingresos_por_propiedad,

            "ingresos_por_propiedad": (
                ingresos_por_propiedad
            ),
            "gastos_por_propiedad": (
                gastos_por_propiedad
            ),

            "labels_meses": labels_meses,
            "facturacion_mensual": (
                facturacion_mensual
            ),
            "gastos_mensuales": (
                gastos_mensuales
            ),
            "resultado_mensual": (
                resultado_mensual
            ),

            "categorias_labels": (
                categorias_labels
            ),
            "categorias_valores": (
                categorias_valores
            ),

            "ingresos_mes_actual": (
                ingresos_mes_actual
            ),
            "gastos_mes": gastos_mes_actual,
            "resultado_mes_actual": (
                resultado_mes_actual
            ),
            "porcentaje_gastos": (
                porcentaje_gastos
            ),
        }
    )

""" I will use jquery and js in order to display the bookings, show in the modals information and change the bookings"""

@login_required
def dashboard(request):
    hoy = timezone.localdate()
    limite_vencimiento = hoy + timedelta(days=30)

    rooms = Flat.objects.all()

    # En este CRM, activo=True determina si el contrato
    # está actualmente en vigor.
    contratos_activos = (
        ContratoAlquiler.objects
        .filter(activo=True)
        .select_related(
            "habitacion",
            "habitacion__propiedad",
            "inquilino",
        )
    )

    habitaciones_totales = (
        Habitacion.objects.count()
    )

    ocupadas = (
        contratos_activos
        .values("habitacion_id")
        .distinct()
        .count()
    )

    disponibles = max(
        habitaciones_totales - ocupadas,
        0,
    )

    porcentaje_ocupacion = (
        round(
            ocupadas
            / habitaciones_totales
            * 100,
            1,
        )
        if habitaciones_totales
        else 0
    )

    facturacion_contratos = (
            contratos_activos
            .aggregate(
                total=Sum("precio_mensual"),
            )
            .get("total")
            or Decimal("0.00")
    )

    ingresos_puntuales_mes = (
            IngresoPropiedad.objects
            .filter(
                fecha__year=hoy.year,
                fecha__month=hoy.month,
            )
            .aggregate(
                total=Sum("importe"),
            )
            .get("total")
            or Decimal("0.00")
    )

    facturacion_mensual = (
            facturacion_contratos
            + ingresos_puntuales_mes
    )
    gastos_del_mes = (
            Gasto.objects
            .filter(
                fecha__year=hoy.year,
                fecha__month=hoy.month,
                anulado=False,
                pais="ES",
            )
            .aggregate(
                total=Sum("importe"),
            )
            .get("total")
            or Decimal("0.00")
    )

    resultado_neto = (
            facturacion_mensual
            - gastos_del_mes
    )

    porcentaje_gastos = (
        round(
            float(
                gastos_del_mes
                / facturacion_mensual
                * 100
            ),
            1,
        )
        if facturacion_mensual
        else 0
    )

    facturacion_potencial = (
        Habitacion.objects
        .aggregate(
            total=Sum("precio"),
        )
        .get("total")
        or Decimal("0.00")
    )

    contratos_por_vencer = (
        contratos_activos
        .filter(
            fecha_fin__isnull=False,
            fecha_fin__gte=hoy,
            fecha_fin__lte=limite_vencimiento,
        )
        .count()
    )

    return render(
        request,
        "dashboard.html",
        {
            "rooms": rooms,
            "mes_actual": (
                hoy.strftime("%B %Y")
                .capitalize()
            ),
            "habitaciones_totales": habitaciones_totales,
            "ocupadas": ocupadas,
            "disponibles": disponibles,
            "porcentaje_ocupacion": porcentaje_ocupacion,
            "facturacion_mensual": facturacion_mensual,
            "facturacion_potencial": facturacion_potencial,
            "contratos_por_vencer": contratos_por_vencer,
            "gastos_del_mes": gastos_del_mes,
            "resultado_neto": resultado_neto,
            "porcentaje_gastos": porcentaje_gastos,
            "facturacion_contratos": facturacion_contratos,
            "ingresos_puntuales_mes": ingresos_puntuales_mes,
            "facturacion_mensual": facturacion_mensual,
        },
    )

def habitaciones(request, id):
    habitacion = get_object_or_404(
        Habitacion.objects
        .select_related(
            "propiedad",
        )
        .prefetch_related(
            Prefetch(
                "galeria",
                queryset=(
                    MultimediaHabitacion.objects
                    .filter(visible=True)
                    .order_by("orden", "pk")
                ),
                to_attr="multimedia_visible",
            ),
        ),
        pk=id,
    )

    return render(
        request,
        "habitacion.html",
        {
            "habitacion": habitacion,
            "multimedia": (
                habitacion.multimedia_visible
            ),
        },
    )


def habitaciones_dashboard(request):
    propiedad_id = request.GET.get(
        "propiedad",
        "",
    )

    estado = request.GET.get(
        "estado",
        "",
    )

    contratos_activos = (
        ContratoAlquiler.objects
        .filter(
            habitacion_id=OuterRef("pk"),
            activo=True,
        )
    )

    procesos_activos = (
        ProcesoFormalizacion.objects
        .filter(
            habitacion_id=OuterRef("pk"),
            estado__in=[
                ProcesoFormalizacion.Estado.PENDIENTE,
                ProcesoFormalizacion.Estado.INICIADO,
            ],
        )
    )

    habitaciones_base = (
        Habitacion.objects
        .select_related("propiedad")
        .annotate(
            tiene_contrato_activo=Exists(
                contratos_activos
            ),
            tiene_proceso_activo=Exists(
                procesos_activos
            ),
        )
        .order_by(
            "propiedad__nombre",
            "nombre",
        )
    )

    # Guardamos todas las habitaciones antes de aplicar filtros.
    # Así el resumen general no cambia cuando filtramos la pantalla.
    todas_las_habitaciones = list(
        habitaciones_base
    )

    habitaciones = habitaciones_base

    if propiedad_id:
        habitaciones = habitaciones.filter(
            propiedad_id=propiedad_id,
        )

    if estado == "ocupadas":
        habitaciones = habitaciones.filter(
            tiene_contrato_activo=True,
        )

    elif estado == "formalizacion":
        habitaciones = habitaciones.filter(
            tiene_contrato_activo=False,
            tiene_proceso_activo=True,
        )

    elif estado == "libres":
        habitaciones = habitaciones.filter(
            tiene_contrato_activo=False,
            tiene_proceso_activo=False,
        )

    propiedades = (
        Flat.objects
        .all()
        .order_by("nombre")
    )

    resumen_propiedades = []

    total_habitaciones = 0
    ocupadas = 0
    libres = 0
    en_formalizacion = 0

    for propiedad in propiedades:
        habitaciones_propiedad = [
            habitacion
            for habitacion in todas_las_habitaciones
            if habitacion.propiedad_id == propiedad.pk
        ]

        total_propiedad = len(
            habitaciones_propiedad
        )

        ocupadas_propiedad = sum(
            1
            for habitacion in habitaciones_propiedad
            if habitacion.tiene_contrato_activo
        )

        formalizacion_propiedad = sum(
            1
            for habitacion in habitaciones_propiedad
            if (
                not habitacion.tiene_contrato_activo
                and habitacion.tiene_proceso_activo
            )
        )

        libres_propiedad = sum(
            1
            for habitacion in habitaciones_propiedad
            if (
                not habitacion.tiene_contrato_activo
                and not habitacion.tiene_proceso_activo
            )
        )

        resumen_propiedades.append(
            {
                "id": propiedad.pk,
                "nombre": propiedad.nombre,
                "total_habitaciones": total_propiedad,
                "ocupadas": ocupadas_propiedad,
                "en_formalizacion": (
                    formalizacion_propiedad
                ),
                "libres": libres_propiedad,
            }
        )

        total_habitaciones += total_propiedad
        ocupadas += ocupadas_propiedad
        en_formalizacion += (
            formalizacion_propiedad
        )
        libres += libres_propiedad

    ingresos_actuales = (
        ContratoAlquiler.objects
        .filter(
            activo=True,
        )
        .aggregate(
            total=Sum("precio_mensual")
        )["total"]
        or 0
    )

    habitaciones_libres = (
        habitaciones_base
        .filter(
            tiene_contrato_activo=False,
            tiene_proceso_activo=False,
        )
    )

    dinero_no_entrando = (
        habitaciones_libres
        .aggregate(
            total=Sum("precio")
        )["total"]
        or 0
    )

    return render(
        request,
        "habitaciones_dashboard.html",
        {
            "habitaciones": habitaciones,
            "propiedades": propiedades,
            "propiedad_seleccionada": (
                str(propiedad_id)
            ),
            "estado_seleccionado": estado,
            "total_habitaciones": (
                total_habitaciones
            ),
            "ocupadas": ocupadas,
            "libres": libres,
            "en_formalizacion": en_formalizacion,
            "ingresos_actuales": (
                ingresos_actuales
            ),
            "dinero_no_entrando": (
                dinero_no_entrando
            ),
            "resumen_propiedades": (
                resumen_propiedades
            ),
        },
    )

def contratos(request):
    propiedad_id = request.GET.get("propiedad", "")
    estado_seleccionado = request.GET.get("estado", "")

    contratos_queryset = (
        ContratoAlquiler.objects
        .filter(activo=True)
        .select_related(
            "habitacion",
            "habitacion__propiedad",
            "inquilino",
        )
        .order_by(
            "fecha_fin",
            "habitacion__propiedad__nombre",
            "habitacion__nombre",
        )
    )

    if propiedad_id:
        contratos_queryset = contratos_queryset.filter(
            habitacion__propiedad_id=propiedad_id
        )

    hoy = timezone.localdate()
    contratos_preparados = []

    for contrato in contratos_queryset:
        fecha_inicio = contrato.fecha_inicio
        fecha_fin_inicial = contrato.fecha_fin

        contrato.dias_restantes = None
        contrato.porcentaje_transcurrido = 0
        contrato.es_renovado = False
        contrato.renovacion_vencida = False
        contrato.fecha_final_visual = fecha_fin_inicial

        if fecha_inicio and fecha_fin_inicial:

            # La renovación comienza cuando termina
            # el plazo inicial del contrato.
            if hoy > fecha_fin_inicial:
                contrato.es_renovado = True

                inicio_periodo = fecha_fin_inicial

                fin_periodo = (
                    fecha_fin_inicial
                    + relativedelta(months=3)
                )

                contrato.fecha_final_visual = fin_periodo

            else:
                inicio_periodo = fecha_inicio
                fin_periodo = fecha_fin_inicial

            dias_totales = max(
                (fin_periodo - inicio_periodo).days,
                1,
            )

            dias_transcurridos = max(
                (hoy - inicio_periodo).days,
                0,
            )

            contrato.dias_restantes = (
                fin_periodo - hoy
            ).days

            contrato.porcentaje_transcurrido = min(
                max(
                    round(
                        dias_transcurridos
                        / dias_totales
                        * 100
                    ),
                    0,
                ),
                100,
            )

            contrato.renovacion_vencida = (
                contrato.es_renovado
                and contrato.dias_restantes < 0
            )

        # Estados y colores durante la renovación trimestral.
        if contrato.es_renovado:

            if contrato.renovacion_vencida:
                contrato.estado_visual = "por_terminar"
                contrato.estado_visual_label = (
                    "Renovación vencida"
                )

            elif contrato.porcentaje_transcurrido <= 33:
                contrato.estado_visual = "renovado"
                contrato.estado_visual_label = "Renovado"

            elif contrato.porcentaje_transcurrido <= 66:
                contrato.estado_visual = "en_curso"
                contrato.estado_visual_label = (
                    "Renovación en curso"
                )

            else:
                contrato.estado_visual = "por_terminar"
                contrato.estado_visual_label = "Por renovar"

        # Estados y colores del periodo inicial.
        else:

            if (
                contrato.dias_restantes is not None
                and contrato.dias_restantes <= 45
            ):
                contrato.estado_visual = "por_terminar"
                contrato.estado_visual_label = "Por terminar"

            elif contrato.porcentaje_transcurrido <= 25:
                contrato.estado_visual = "nuevo"
                contrato.estado_visual_label = "Nuevo"

            else:
                contrato.estado_visual = "en_curso"
                contrato.estado_visual_label = "En curso"

        coincide_estado = (
            not estado_seleccionado
            or contrato.estado_visual
            == estado_seleccionado
            or (
                estado_seleccionado == "renovado"
                and contrato.es_renovado
            )
        )

        if coincide_estado:
            contratos_preparados.append(contrato)

    propiedades = Flat.objects.order_by("nombre")

    return render(
        request,
        "contratos.html",
        {
            "contratos": contratos_preparados,
            "propiedades": propiedades,
            "propiedad_id": propiedad_id,
            "estado_seleccionado": estado_seleccionado,
        },
    )

class NewContractView(LoginRequiredMixin, View,):
    template_name = "newcontract.html"

    def get(self, request):
        propiedad_id = request.GET.get(
            "propiedad"
        )

        habitacion_id = request.GET.get(
            "habitacion"
        )

        modo = request.GET.get(
            "modo",
            "directo",
        )

        if modo not in {
            "directo",
            "existente",
        }:
            modo = "directo"

        if habitacion_id:
            habitacion = get_object_or_404(
                Habitacion.objects.select_related(
                    "propiedad",
                ),
                pk=habitacion_id,
            )

            propiedad_id = (
                habitacion.propiedad_id
            )

        inquilino_form = InquilinoForm()

        contrato_form = ContratoAlquilerForm(
            propiedad_id=propiedad_id,
            habitacion_id=habitacion_id,
        )

        aval_form = AvalContratoForm(
            prefix="aval",
        )

        return render(
            request,
            self.template_name,
            {
                "inquilino_form": inquilino_form,
                "contrato_form": contrato_form,
                "aval_form": aval_form,
                "propiedades": (
                    Flat.objects
                    .all()
                    .order_by("nombre")
                ),
                "propiedad_id": (
                    int(propiedad_id)
                    if propiedad_id
                    else None
                ),
                "habitacion_id": (
                    int(habitacion_id)
                    if habitacion_id
                    else None
                ),
                "tiene_aval": False,
                "modo": modo,
            },
        )

    @transaction.atomic
    def post(self, request):
        propiedad_id = request.POST.get(
            "propiedad"
        )

        habitacion_id = request.POST.get(
            "habitacion"
        )

        modo = request.POST.get(
            "modo",
            "directo",
        )

        if modo not in {
            "directo",
            "existente",
        }:
            modo = "directo"

        tiene_aval = (
            request.POST.get("tiene_aval")
            == "on"
        )

        inquilino_form = InquilinoForm(
            request.POST,
        )

        contrato_form = ContratoAlquilerForm(
            request.POST,
            propiedad_id=propiedad_id,
            habitacion_id=habitacion_id,
        )

        aval_form = AvalContratoForm(
            request.POST,
            prefix="aval",
        )

        inquilino_valido = (
            inquilino_form.is_valid()
        )

        contrato_valido = (
            contrato_form.is_valid()
        )

        aval_valido = (
            not tiene_aval
            or aval_form.is_valid()
        )

        if (
            inquilino_valido
            and contrato_valido
            and aval_valido
        ):
            inquilino = inquilino_form.save()

            contrato = contrato_form.save(
                commit=False,
            )

            contrato.inquilino = inquilino
            contrato.activo = True
            contrato.save()

            if tiene_aval:
                aval = aval_form.save(
                    commit=False,
                )

                aval.contrato = contrato
                aval.save()

            if modo == "existente":
                messages.success(
                    request,
                    "Alquiler existente registrado. "
                    "La habitación ya figura como ocupada.",
                )

                return redirect(
                    "hotel:habitaciones_dashboard"
                )

            messages.success(
                request,
                "Contrato creado correctamente.",
            )

            return redirect(
                "hotel:contrato_pdf",
                contrato_id=contrato.pk,
            )

        return render(
            request,
            self.template_name,
            {
                "inquilino_form": inquilino_form,
                "contrato_form": contrato_form,
                "aval_form": aval_form,
                "propiedades": (
                    Flat.objects
                    .all()
                    .order_by("nombre")
                ),
                "propiedad_id": (
                    int(propiedad_id)
                    if propiedad_id
                    else None
                ),
                "habitacion_id": (
                    int(habitacion_id)
                    if habitacion_id
                    else None
                ),
                "tiene_aval": tiene_aval,
                "modo": modo,
            },
        )

def contrato_pdf(request, contrato_id):
    contrato = get_object_or_404(
        ContratoAlquiler,
        pk=contrato_id,
    )

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'inline; filename="contrato_{contrato.pk}.pdf"'
    )

    return generar_contrato_pdf(
        request,
        response,
        contrato,
    )


def contacto(request):
    return render(
        request,
        "contacto.html",
    )


def calcular_renta_proporcional(precio_mensual, fecha_inicio):
    """
    Calcula la renta desde el día de entrada hasta el último día
    del mismo mes, incluyendo el día de entrada.
    """
    dias_del_mes = calendar.monthrange(
        fecha_inicio.year,
        fecha_inicio.month,
    )[1]

    dias_a_cobrar = dias_del_mes - fecha_inicio.day + 1

    importe = (
        Decimal(precio_mensual)
        / Decimal(dias_del_mes)
        * Decimal(dias_a_cobrar)
    )

    return importe.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )


def construir_borrador_contrato(proceso):
    """
    Construye un ContratoAlquiler sin guardarlo en la base de datos.
    Se utiliza exclusivamente para generar el PDF provisional.
    """
    fecha_fin = (
        proceso.fecha_inicio_contrato
        + relativedelta(months=proceso.duracion_meses)
        - timedelta(days=1)
    )

    return ContratoAlquiler(
        inquilino=proceso.inquilino,
        habitacion=proceso.habitacion,
        fecha_inicio=proceso.fecha_inicio_contrato,
        fecha_fin=fecha_fin,
        precio_mensual=proceso.precio_mensual,
        fianza=proceso.fianza,
        activo=False,
    )


class DetalleProcesoFormalizacionView(
    LoginRequiredMixin,
    DetailView,
):
    template_name = "hotel/detalle_proceso_formalizacion.html"
    context_object_name = "proceso"

    def get_queryset(self):
        return ProcesoFormalizacion.objects.select_related(
            "habitacion",
            "habitacion__propiedad",
            "inquilino",
            "contrato",
        )

    def get_object(self, queryset=None):
        proceso = super().get_object(queryset)

        proceso.actualizar_estado()
        proceso.refresh_from_db()

        return proceso

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        proceso = self.object
        telefono = ""

        if proceso.inquilino:
            telefono = (
                proceso.inquilino.telefono_whatsapp
            )

        enlace_publico = self.request.build_absolute_uri(
            reverse(
                "hotel:formalizacion_publica",
                kwargs={
                    "token": proceso.token,
                },
            )
        )

        mensaje = (
            f"Hola {proceso.inquilino.nombre}, "
            f"te enviamos el enlace de By Colección "
            f"para revisar y completar la formalización "
            f"del alquiler de {proceso.habitacion.nombre}: "
            f"{enlace_publico}"
        )

        if telefono:
            context["whatsapp_url"] = (
                f"https://wa.me/{telefono}"
                f"?text={quote(mensaje)}"
            )
        else:
            context["whatsapp_url"] = None

        context["formalizacion_url"] = (
            enlace_publico
        )

        return context


class FormalizacionPublicaView(View):
    """
    Página pública que recibe el futuro inquilino.

    No contiene formularios y no crea contratos. Únicamente muestra
    el estado, las condiciones y el botón de descarga.
    """
    template_name = "hotel/formalizacion_publica.html"
    template_no_disponible = (
        "hotel/formalizacion_no_disponible.html"
    )

    def get(self, request, token):
        proceso = get_object_or_404(
            ProcesoFormalizacion.objects.select_related(
                "habitacion",
                "habitacion__propiedad",
                "inquilino",
                "contrato",
            ),
            token=token,
        )

        proceso.actualizar_estado()
        proceso.refresh_from_db()

        if proceso.estado in {
            ProcesoFormalizacion.Estado.CANCELADO,
            ProcesoFormalizacion.Estado.CADUCADO,
        }:
            return render(
                request,
                self.template_no_disponible,
                {
                    "proceso": proceso,
                },
                status=410,
            )

        return render(
            request,
            self.template_name,
            {
                "proceso": proceso,
            },
        )





class CancelarProcesoFormalizacionView(
    LoginRequiredMixin,
    View,
):
    """
    Cancela un proceso que no se ha completado.

    No crea ni elimina ContratoAlquiler.
    """

    @transaction.atomic
    def post(self, request, pk):
        proceso = get_object_or_404(
            ProcesoFormalizacion.objects.select_for_update(),
            pk=pk,
        )

        estados_cancelables = {
            ProcesoFormalizacion.Estado.PENDIENTE,
            ProcesoFormalizacion.Estado.INICIADO,
        }

        if proceso.estado not in estados_cancelables:
            messages.warning(
                request,
                "Este proceso ya no puede cancelarse.",
            )
            return redirect(
                "hotel:detalle_proceso_formalizacion",
                pk=proceso.pk,
            )

        proceso.estado = ProcesoFormalizacion.Estado.CANCELADO
        proceso.save(update_fields=["estado"])

        messages.success(
            request,
            "Proceso de formalización cancelado correctamente.",
        )

        return redirect("hotel:habitaciones_dashboard")


class CrearProcesoFormalizacionView(
    LoginRequiredMixin,
    View,
):
    """
    Crea el inquilino y el proceso de formalización.

    Si existe avalista, sus datos se guardan provisionalmente
    en ProcesoFormalizacion. AvalContrato no se crea hasta que
    el proceso queda formalizado.
    """

    template_name = (
        "hotel/crear_proceso_formalizacion.html"
    )

    def obtener_habitacion(
        self,
        request,
        habitacion_id,
    ):
        habitacion = get_object_or_404(
            Habitacion,
            pk=habitacion_id,
        )

        if habitacion.contrato_activo:
            messages.error(
                request,
                (
                    "Primero debes finalizar el contrato "
                    "activo de esta habitación."
                ),
            )
            return None

        if habitacion.proceso_formalizacion_activo:
            messages.info(
                request,
                (
                    "Esta habitación ya tiene un proceso "
                    "de formalización activo."
                ),
            )
            return None

        return habitacion

    def get(
        self,
        request,
        habitacion_id,
    ):
        habitacion = self.obtener_habitacion(
            request,
            habitacion_id,
        )

        if habitacion is None:
            return redirect(
                "hotel:habitaciones_dashboard"
            )

        inquilino_form = InquilinoForm(
            prefix="inquilino",
        )

        proceso_form = CrearProcesoFormalizacionForm(
            prefix="proceso",
            initial={
                "precio_mensual": habitacion.precio,
                "fianza": habitacion.precio,
                "duracion_meses": 6,
                "tipo_primera_renta": (
                    ProcesoFormalizacion
                    .TipoPrimeraRenta
                    .PROPORCIONAL
                ),
            },
        )

        aval_form = AvalContratoForm(
            prefix="aval",
        )

        return render(
            request,
            self.template_name,
            {
                "habitacion": habitacion,
                "inquilino_form": inquilino_form,
                "proceso_form": proceso_form,
                "aval_form": aval_form,
                "tiene_aval": False,
            },
        )

    @transaction.atomic
    def post(
        self,
        request,
        habitacion_id,
    ):
        habitacion = self.obtener_habitacion(
            request,
            habitacion_id,
        )

        if habitacion is None:
            return redirect(
                "hotel:habitaciones_dashboard"
            )

        tiene_aval = (
            request.POST.get("tiene_aval") == "on"
        )

        inquilino_form = InquilinoForm(
            request.POST,
            prefix="inquilino",
        )

        proceso_form = CrearProcesoFormalizacionForm(
            request.POST,
            prefix="proceso",
        )

        aval_form = AvalContratoForm(
            request.POST,
            prefix="aval",
        )

        inquilino_valido = (
            inquilino_form.is_valid()
        )

        proceso_valido = (
            proceso_form.is_valid()
        )

        aval_valido = True

        if tiene_aval:
            aval_valido = aval_form.is_valid()

        if not (
            inquilino_valido
            and proceso_valido
            and aval_valido
        ):
            messages.error(
                request,
                (
                    "Oye, faltan datos o hay algún campo "
                    "incorrecto. Revisa los campos señalados."
                ),
            )

            return render(
                request,
                self.template_name,
                {
                    "habitacion": habitacion,
                    "inquilino_form": inquilino_form,
                    "proceso_form": proceso_form,
                    "aval_form": aval_form,
                    "tiene_aval": tiene_aval,
                },
            )

        inquilino = inquilino_form.save()

        proceso = proceso_form.save(
            commit=False
        )

        proceso.habitacion = habitacion
        proceso.inquilino = inquilino
        proceso.estado = (
            ProcesoFormalizacion.Estado.PENDIENTE
        )

        proceso.fecha_limite = (
            timezone.now()
            + timedelta(days=7)
        )

        proceso.tiene_aval = tiene_aval

        if tiene_aval:
            proceso.aval_nombre_completo = (
                aval_form.cleaned_data[
                    "nombre_completo"
                ]
            )

            proceso.aval_dni_nie = (
                aval_form.cleaned_data[
                    "dni_nie"
                ]
            )

            proceso.aval_domicilio = (
                aval_form.cleaned_data[
                    "domicilio"
                ]
            )

        else:
            proceso.aval_nombre_completo = ""
            proceso.aval_dni_nie = ""
            proceso.aval_domicilio = ""

        if (
            proceso.tipo_primera_renta
            == ProcesoFormalizacion
            .TipoPrimeraRenta
            .MES_COMPLETO
        ):
            proceso.importe_primera_renta = (
                proceso.precio_mensual
            )

        else:
            proceso.importe_primera_renta = (
                calcular_renta_proporcional(
                    precio_mensual=(
                        proceso.precio_mensual
                    ),
                    fecha_inicio=(
                        proceso.fecha_inicio_contrato
                    ),
                )
            )

        proceso.save()

        messages.success(
            request,
            (
                "Proceso creado. Ya puedes enviar "
                "el enlace al futuro inquilino."
            ),
        )

        return redirect(
            "hotel:detalle_proceso_formalizacion",
            pk=proceso.pk,
        )


class DescargarContratoFormalizacionView(View):
    """
    Genera el PDF provisional utilizando los datos del proceso.

    No crea ni guarda ContratoAlquiler.
    Al realizar la primera descarga comienza el plazo de 24 horas.
    """

    @transaction.atomic
    def get(self, request, token):
        proceso = get_object_or_404(
            ProcesoFormalizacion.objects.select_for_update().select_related(
                "habitacion",
                "habitacion__propiedad",
                "inquilino",
            ),
            token=token,
        )

        proceso.actualizar_estado()
        proceso.refresh_from_db()

        estados_permitidos = {
            ProcesoFormalizacion.Estado.PENDIENTE,
            ProcesoFormalizacion.Estado.INICIADO,
        }

        if proceso.estado not in estados_permitidos:
            return render(
                request,
                "hotel/formalizacion_no_disponible.html",
                {
                    "proceso": proceso,
                    "motivo": (
                        "Este proceso ya no permite descargar "
                        "el contrato."
                    ),
                },
                status=410,
            )

        if proceso.inquilino is None:
            return render(
                request,
                "hotel/formalizacion_no_disponible.html",
                {
                    "proceso": proceso,
                    "motivo": (
                        "El proceso no tiene un futuro "
                        "inquilino asociado."
                    ),
                },
                status=400,
            )

        ahora = timezone.now()

        if not proceso.contrato_descargado:
            proceso.contrato_descargado = True
            proceso.fecha_descarga = ahora
            proceso.fecha_inicio = ahora
            proceso.fecha_limite = ahora + timedelta(hours=24)
            proceso.estado = ProcesoFormalizacion.Estado.INICIADO

            proceso.save(
                update_fields=[
                    "contrato_descargado",
                    "fecha_descarga",
                    "fecha_inicio",
                    "fecha_limite",
                    "estado",
                ]
            )

        borrador = construir_borrador_contrato(proceso)

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = (
            "attachment; "
            f'filename="contrato_formalizacion_{proceso.pk}.pdf"'
        )

        return generar_contrato_pdf(
            request,
            response,
            borrador,
        )


class EliminarProcesoFormalizacionView(LoginRequiredMixin, View):

    def post(self, request, pk):
        proceso = get_object_or_404(
            ProcesoFormalizacion.objects.select_related(
                "habitacion",
                "contrato",
            ),
            pk=pk,
        )

        if proceso.estado == ProcesoFormalizacion.Estado.FORMALIZADO:
            messages.error(
                request,
                "No puedes eliminar un proceso ya formalizado.",
            )
            return redirect(
                "hotel:detalle_proceso_formalizacion",
                pk=proceso.pk,
            )

        if proceso.contrato_id:
            messages.error(
                request,
                "No puedes eliminar este proceso porque tiene un contrato asociado.",
            )
            return redirect(
                "hotel:detalle_proceso_formalizacion",
                pk=proceso.pk,
            )

        habitacion_nombre = (
            proceso.habitacion.nombre
            if proceso.habitacion
            else "la habitación"
        )

        proceso.delete()

        messages.success(
            request,
            f"El proceso de {habitacion_nombre} se ha eliminado definitivamente.",
        )

        return redirect("hotel:habitaciones_dashboard")


class EditarProcesoFormalizacionView(
    LoginRequiredMixin,
    View,
):
    """
    Permite modificar los datos del inquilino y las condiciones
    de un proceso que todavía no se ha formalizado.
    """

    template_name = (
        "hotel/editar_proceso_formalizacion.html"
    )

    estados_editables = {
        ProcesoFormalizacion.Estado.PENDIENTE,
        ProcesoFormalizacion.Estado.INICIADO,
    }

    def obtener_proceso(self, request, pk):
        proceso = get_object_or_404(
            ProcesoFormalizacion.objects.select_related(
                "habitacion",
                "habitacion__propiedad",
                "inquilino",
                "contrato",
            ),
            pk=pk,
        )

        proceso.actualizar_estado()
        proceso.refresh_from_db()

        if proceso.estado not in self.estados_editables:
            messages.error(
                request,
                (
                    "Este proceso ya no puede modificarse porque "
                    "está cancelado, caducado o formalizado."
                ),
            )
            return None

        if proceso.inquilino_id is None:
            messages.error(
                request,
                "El proceso no tiene un inquilino asociado.",
            )
            return None

        return proceso

    def get(self, request, pk):
        proceso = self.obtener_proceso(
            request,
            pk,
        )

        if proceso is None:
            return redirect(
                "hotel:detalle_proceso_formalizacion",
                pk=pk,
            )

        inquilino_form = InquilinoForm(
            instance=proceso.inquilino,
            prefix="inquilino",
        )

        proceso_form = CrearProcesoFormalizacionForm(
            instance=proceso,
            prefix="proceso",
        )

        return render(
            request,
            self.template_name,
            {
                "proceso": proceso,
                "habitacion": proceso.habitacion,
                "inquilino_form": inquilino_form,
                "proceso_form": proceso_form,
            },
        )

    @transaction.atomic
    def post(self, request, pk):
        proceso = get_object_or_404(
            ProcesoFormalizacion.objects
            .select_for_update()
            .select_related(
                "habitacion",
                "habitacion__propiedad",
                "inquilino",
                "contrato",
            ),
            pk=pk,
        )

        proceso.actualizar_estado()
        proceso.refresh_from_db()

        if proceso.estado not in self.estados_editables:
            messages.error(
                request,
                "Este proceso ya no puede modificarse.",
            )
            return redirect(
                "hotel:detalle_proceso_formalizacion",
                pk=proceso.pk,
            )

        if proceso.inquilino_id is None:
            messages.error(
                request,
                "El proceso no tiene un inquilino asociado.",
            )
            return redirect(
                "hotel:detalle_proceso_formalizacion",
                pk=proceso.pk,
            )

        inquilino_form = InquilinoForm(
            request.POST,
            instance=proceso.inquilino,
            prefix="inquilino",
        )

        proceso_form = CrearProcesoFormalizacionForm(
            request.POST,
            instance=proceso,
            prefix="proceso",
        )

        inquilino_valido = inquilino_form.is_valid()
        proceso_valido = proceso_form.is_valid()

        if not (
            inquilino_valido
            and proceso_valido
        ):
            return render(
                request,
                self.template_name,
                {
                    "proceso": proceso,
                    "habitacion": proceso.habitacion,
                    "inquilino_form": inquilino_form,
                    "proceso_form": proceso_form,
                },
            )

        hubo_cambios = (
            inquilino_form.has_changed()
            or proceso_form.has_changed()
        )

        documento_descargado_antes = (
            proceso.contrato_descargado
        )

        inquilino_form.save()

        proceso = proceso_form.save(
            commit=False
        )

        if (
            proceso.tipo_primera_renta
            == ProcesoFormalizacion
            .TipoPrimeraRenta
            .MES_COMPLETO
        ):
            proceso.importe_primera_renta = (
                proceso.precio_mensual
            )

        else:
            proceso.importe_primera_renta = (
                calcular_renta_proporcional(
                    precio_mensual=(
                        proceso.precio_mensual
                    ),
                    fecha_inicio=(
                        proceso.fecha_inicio_contrato
                    ),
                )
            )

        if hubo_cambios and documento_descargado_antes:
            proceso.contrato_descargado = False
            proceso.fecha_descarga = None

        proceso.save()

        if hubo_cambios and documento_descargado_antes:
            messages.warning(
                request,
                (
                    "Los datos se actualizaron. El candidato "
                    "deberá descargar nuevamente el documento "
                    "corregido."
                ),
            )

        elif hubo_cambios:
            messages.success(
                request,
                "Proceso actualizado correctamente.",
            )

        else:
            messages.info(
                request,
                "No se realizaron cambios.",
            )

        return redirect(
            "hotel:detalle_proceso_formalizacion",
            pk=proceso.pk,
        )

class ConfirmarFormalizacionView(
    LoginRequiredMixin,
    View,
):
    """
    Confirma la recepción del documento firmado y los pagos.

    Crea ContratoAlquiler y, cuando corresponda,
    crea también AvalContrato.
    """

    @transaction.atomic
    def post(self, request, pk):
        proceso = get_object_or_404(
            ProcesoFormalizacion.objects
            .select_for_update()
            .select_related(
                "habitacion",
                "inquilino",
                "contrato",
            ),
            pk=pk,
        )

        estados_formalizables = {
            ProcesoFormalizacion.Estado.PENDIENTE,
            ProcesoFormalizacion.Estado.INICIADO,
        }

        if proceso.estado not in estados_formalizables:
            messages.warning(
                request,
                (
                    "Este proceso ya no puede "
                    "formalizarse."
                ),
            )
            return redirect(
                "hotel:detalle_proceso_formalizacion",
                pk=proceso.pk,
            )

        if proceso.contrato_id:
            messages.info(
                request,
                (
                    "Este proceso ya tiene un "
                    "contrato asociado."
                ),
            )
            return redirect(
                "hotel:detalle_proceso_formalizacion",
                pk=proceso.pk,
            )

        if proceso.inquilino is None:
            messages.error(
                request,
                (
                    "El proceso no tiene un "
                    "inquilino asociado."
                ),
            )
            return redirect(
                "hotel:detalle_proceso_formalizacion",
                pk=proceso.pk,
            )

        if proceso.habitacion is None:
            messages.error(
                request,
                (
                    "El proceso no tiene una "
                    "habitación asociada."
                ),
            )
            return redirect(
                "hotel:detalle_proceso_formalizacion",
                pk=proceso.pk,
            )

        if proceso.habitacion.contrato_activo:
            messages.error(
                request,
                (
                    "La habitación ya tiene otro "
                    "contrato activo."
                ),
            )
            return redirect(
                "hotel:detalle_proceso_formalizacion",
                pk=proceso.pk,
            )

        if not proceso.fecha_inicio_contrato:
            messages.error(
                request,
                (
                    "El proceso no tiene una "
                    "fecha de inicio."
                ),
            )
            return redirect(
                "hotel:detalle_proceso_formalizacion",
                pk=proceso.pk,
            )

        if not proceso.duracion_meses:
            messages.error(
                request,
                (
                    "El proceso no tiene una "
                    "duración válida."
                ),
            )
            return redirect(
                "hotel:detalle_proceso_formalizacion",
                pk=proceso.pk,
            )

        if proceso.precio_mensual is None:
            messages.error(
                request,
                (
                    "El proceso no tiene un "
                    "precio mensual."
                ),
            )
            return redirect(
                "hotel:detalle_proceso_formalizacion",
                pk=proceso.pk,
            )

        if proceso.fianza is None:
            messages.error(
                request,
                (
                    "El proceso no tiene una "
                    "fianza definida."
                ),
            )
            return redirect(
                "hotel:detalle_proceso_formalizacion",
                pk=proceso.pk,
            )

        if proceso.tiene_aval and (
            not proceso.aval_nombre_completo
            or not proceso.aval_dni_nie
        ):
            messages.error(
                request,
                (
                    "El proceso indica que existe un avalista, "
                    "pero sus datos están incompletos."
                ),
            )
            return redirect(
                "hotel:detalle_proceso_formalizacion",
                pk=proceso.pk,
            )

        fecha_fin = (
            proceso.fecha_inicio_contrato
            + relativedelta(
                months=proceso.duracion_meses
            )
            - timedelta(days=1)
        )

        contrato = ContratoAlquiler.objects.create(
            inquilino=proceso.inquilino,
            habitacion=proceso.habitacion,
            fecha_inicio=(
                proceso.fecha_inicio_contrato
            ),
            fecha_fin=fecha_fin,
            precio_mensual=(
                proceso.precio_mensual
            ),
            fianza=proceso.fianza,
            activo=True,
        )

        if proceso.tiene_aval:
            AvalContrato.objects.create(
                contrato=contrato,
                nombre_completo=(
                    proceso.aval_nombre_completo
                ),
                dni_nie=(
                    proceso.aval_dni_nie
                ),
                domicilio=(
                    proceso.aval_domicilio
                ),
            )

        ahora = timezone.now()

        proceso.contrato = contrato
        proceso.contrato_firmado_recibido = True
        proceso.fecha_contrato_firmado = ahora
        proceso.fianza_recibida = True
        proceso.renta_recibida = True
        proceso.estado = (
            ProcesoFormalizacion.Estado.FORMALIZADO
        )
        proceso.fecha_formalizacion = ahora

        proceso.save(
            update_fields=[
                "contrato",
                "contrato_firmado_recibido",
                "fecha_contrato_firmado",
                "fianza_recibida",
                "renta_recibida",
                "estado",
                "fecha_formalizacion",
            ]
        )

        messages.success(
            request,
            (
                "Proceso formalizado y contrato "
                "creado correctamente."
            ),
        )

        return redirect(
            "hotel:habitaciones_dashboard"
        )

# =========================================================
# PANEL DE GASTOS
# =========================================================


class GastosDashboardView(
    LoginRequiredMixin,
    View,
):
    template_name = "hotel/gastos/dashboard.html"

    PAISES_VALIDOS = {
        "ES",
        "AR",
    }

    COLORES_CATEGORIAS = {
        "suministros": "#72a5a1",
        "internet": "#5f9298",
        "prestamos": "#b08b62",
        "hipoteca": "#b08b62",
        "comunidad": "#c9a7ad",
        "impuestos": "#745f6d",
        "mantenimiento": "#a7b8a1",
        "reparacion": "#d18b72",
        "mobiliario": "#927783",
        "equipamiento": "#d4ae62",
        "limpieza": "#8ebeb9",
        "gestion": "#4b2938",
        "gestoria": "#4b2938",
        "desplazamiento": "#b8967d",
        "software": "#768aa5",
        "marketing": "#d29cac",
        "seguros": "#7b9a74",
        "otros": "#aaa0a4",
    }

    NOMBRES_TRIMESTRES = {
        1: "Primer trimestre",
        2: "Segundo trimestre",
        3: "Tercer trimestre",
        4: "Cuarto trimestre",
    }

    DIVISORES_FRECUENCIA = {
        "mensual": Decimal("1"),
        "bimestral": Decimal("2"),
        "trimestral": Decimal("3"),
        "semestral": Decimal("6"),
        "anual": Decimal("12"),
    }

    MESES_FRECUENCIA = {
        "mensual": 1,
        "bimestral": 2,
        "trimestral": 3,
        "semestral": 6,
        "anual": 12,
    }

    def get(self, request):
        generar_gastos_recurrentes()

        hoy = timezone.localdate()

        # =====================================================
        # PAÍS Y MONEDA
        # =====================================================

        pais_actual = (
            request.GET.get(
                "pais",
                "ES",
            )
            .strip()
            .upper()
        )

        if pais_actual not in self.PAISES_VALIDOS:
            pais_actual = "ES"

        es_argentina = pais_actual == "AR"
        es_espana = pais_actual == "ES"

        campo_importe = (
            "importe_usd"
            if es_argentina
            else "importe"
        )

        codigo_moneda = (
            "USD"
            if es_argentina
            else "EUR"
        )

        simbolo_moneda = (
            "US$"
            if es_argentina
            else "€"
        )

        # =====================================================
        # PROYECTO ARGENTINO
        # =====================================================

        proyectos_disponibles = (
            Proyecto.objects
            .filter(
                pais=pais_actual,
                activo=True,
            )
            .order_by("nombre")
        )

        proyecto_actual = None
        proyecto_seleccionado = ""

        if es_argentina:
            proyecto_actual = (
                self.obtener_proyecto(
                    proyectos_disponibles,
                    request.GET.get(
                        "proyecto",
                        "",
                    ),
                )
            )

            if proyecto_actual:
                proyecto_seleccionado = str(
                    proyecto_actual.pk
                )

        # =====================================================
        # FILTROS
        # =====================================================

        mes_recibido = request.GET.get(
            "mes"
        )

        periodo_explicito = bool(
            mes_recibido
        )

        mes_seleccionado = (
            mes_recibido
            or f"{hoy.year}-{hoy.month:02d}"
        )

        propiedad_seleccionada = (
            request.GET.get(
                "propiedad",
                "",
            )
            if es_espana
            else ""
        )

        categoria_seleccionada = (
            request.GET.get(
                "categoria",
                "",
            )
        )

        tipo_seleccionado = (
            request.GET.get(
                "tipo",
                "",
            )
        )

        ambito_seleccionado = (
            request.GET.get(
                "ambito",
                "",
            )
        )

        estado_seleccionado = (
            request.GET.get(
                "estado",
                "",
            )
        )

        vista_listado = (
            request.GET.get(
                "vista_listado",
                "ultimos",
            )
        )

        year, month, mes_seleccionado = (
            self.obtener_periodo(
                mes_seleccionado,
                hoy,
            )
        )

        if hoy.month == 1:
            anio_anterior = hoy.year - 1
            mes_anterior = 12

        else:
            anio_anterior = hoy.year
            mes_anterior = hoy.month - 1

        trimestre_actual = (
            ((hoy.month - 1) // 3) + 1
        )

        gestoria_anio = self.obtener_entero(
            request.GET.get(
                "gestoria_anio"
            ),
            hoy.year,
        )

        gestoria_trimestre = (
            self.obtener_entero(
                request.GET.get(
                    "gestoria_trimestre"
                ),
                trimestre_actual,
            )
        )

        if gestoria_trimestre not in {
            1,
            2,
            3,
            4,
        }:
            gestoria_trimestre = (
                trimestre_actual
            )

        meses_trimestre = (
            self.obtener_meses_trimestre(
                gestoria_trimestre
            )
        )

        # =====================================================
        # QUERYSET DEL PAÍS
        # =====================================================

        gastos_sin_filtros = (
            Gasto.objects
            .filter(
                anulado=False,
                pais=pais_actual,
            )
            .select_related(
                "propiedad",
                "habitacion",
                "proyecto",
                "gasto_recurrente",
            )
        )

        if es_argentina:
            if proyecto_actual:
                gastos_sin_filtros = (
                    gastos_sin_filtros
                    .filter(
                        proyecto=proyecto_actual,
                    )
                )
            else:
                gastos_sin_filtros = (
                    gastos_sin_filtros.none()
                )

        # =====================================================
        # TOTAL HISTÓRICO DEL ESPACIO FINANCIERO
        # España se suma en EUR.
        # Argentina se suma en USD.
        # =====================================================

        total_historico = self.sumar_importes(
            gastos_sin_filtros,
            campo_importe,
        )

        gastos_base = gastos_sin_filtros

        if es_espana:
            (
                gastos_base,
                propiedad_seleccionada,
            ) = self.filtrar_propiedad(
                gastos_base,
                propiedad_seleccionada,
            )

        gastos_base, tipo_seleccionado = (
            self.filtrar_eleccion(
                queryset=gastos_base,
                campo="tipo",
                valor=tipo_seleccionado,
                opciones=Gasto.TIPOS,
            )
        )

        gastos_base, ambito_seleccionado = (
            self.filtrar_eleccion(
                queryset=gastos_base,
                campo="ambito",
                valor=ambito_seleccionado,
                opciones=Gasto.AMBITOS,
            )
        )

        if estado_seleccionado == "pagado":
            gastos_base = gastos_base.filter(
                pagado=True
            )

        elif estado_seleccionado == "pendiente":
            gastos_base = gastos_base.filter(
                pagado=False
            )

        else:
            estado_seleccionado = ""

        # =====================================================
        # PERIODO SELECCIONADO
        # =====================================================

        gastos_mes_base = gastos_base.filter(
            fecha__year=year,
            fecha__month=month,
        )

        gastos_anio_base = gastos_base.filter(
            fecha__year=year,
        )

        total_gastos_mes = self.sumar_importes(
            gastos_mes_base,
            campo_importe,
        )

        total_gastos_anio = self.sumar_importes(
            gastos_anio_base,
            campo_importe,
        )

        grafico_mes = self.datos_por_categoria(
            gastos_mes_base,
            campo_importe,
        )

        grafico_anio = self.datos_por_categoria(
            gastos_anio_base,
            campo_importe,
        )

        gastos = gastos_mes_base

        gastos, categoria_seleccionada = (
            self.filtrar_eleccion(
                queryset=gastos,
                campo="categoria",
                valor=categoria_seleccionada,
                opciones=Gasto.CATEGORIAS,
            )
        )

        gastos = gastos.order_by(
            "-fecha",
            "-fecha_creacion",
        )

        total_gastos_filtrados = (
            self.sumar_importes(
                gastos,
                campo_importe,
            )
        )

        total_pendiente = self.sumar_importes(
            gastos.filter(
                pagado=False
            ),
            campo_importe,
        )

        total_mejoras = self.sumar_importes(
            gastos.filter(
                Q(tipo="inversion")
                | Q(
                    categoria__in=[
                        "mobiliario",
                        "equipamiento",
                    ]
                )
            ),
            campo_importe,
        )

        # =====================================================
        # GASTOS ARGENTINOS SIN CONVERSIÓN
        # =====================================================

        numero_sin_conversion = 0
        gastos_sin_conversion = Gasto.objects.none()

        if es_argentina:
            gastos_sin_conversion = (
                gastos_sin_filtros
                .filter(
                    Q(importe_usd__isnull=True)
                    | Q(cotizacion_usd__isnull=True)
                )
                .order_by(
                    "-fecha",
                    "-fecha_creacion",
                )
            )

            numero_sin_conversion = (
                gastos_sin_conversion.count()
            )

        # =====================================================
        # MES ACTUAL Y ANTERIOR
        # =====================================================

        comparativa_base = (
            gastos_sin_filtros
        )

        if es_espana:
            comparativa_base, _ = (
                self.filtrar_propiedad(
                    comparativa_base,
                    propiedad_seleccionada,
                )
            )

        gastos_mes_actual = (
            comparativa_base.filter(
                fecha__year=hoy.year,
                fecha__month=hoy.month,
            )
        )

        gastos_mes_anterior = (
            comparativa_base.filter(
                fecha__year=anio_anterior,
                fecha__month=mes_anterior,
            )
        )

        total_mes_actual = self.sumar_importes(
            gastos_mes_actual,
            campo_importe,
        )

        total_mes_anterior = (
            self.sumar_importes(
                gastos_mes_anterior,
                campo_importe,
            )
        )

        diferencia_mensual = (
            total_mes_actual
            - total_mes_anterior
        )

        if total_mes_anterior:
            porcentaje_diferencia_mensual = (
                diferencia_mensual
                / total_mes_anterior
                * Decimal("100")
            )

        else:
            porcentaje_diferencia_mensual = (
                Decimal("0.00")
            )

        grafico_mes_anterior = (
            self.datos_por_categoria(
                gastos_mes_anterior,
                campo_importe,
            )
        )

        # =====================================================
        # INGRESOS
        # Solo se calculan en el espacio español.
        # =====================================================

        if es_espana:
            ingresos_mensuales = (
                ContratoAlquiler.objects
                .filter(
                    activo=True
                )
                .aggregate(
                    total=Sum(
                        "precio_mensual"
                    )
                )["total"]
                or Decimal("0.00")
            )

            beneficio_estimado = (
                ingresos_mensuales
                - total_mes_actual
            )

        else:
            ingresos_mensuales = (
                Decimal("0.00")
            )

            beneficio_estimado = (
                Decimal("0.00")
            )

        # =====================================================
        # RECURRENTES DEL PAÍS
        # =====================================================

        gastos_recurrentes = (
            GastoRecurrente.objects
            .filter(
                pais=pais_actual,
            )
            .select_related(
                "propiedad",
                "habitacion",
                "proyecto",
            )
        )

        if es_argentina:
            if proyecto_actual:
                gastos_recurrentes = (
                    gastos_recurrentes.filter(
                        proyecto=proyecto_actual,
                    )
                )
            else:
                gastos_recurrentes = (
                    gastos_recurrentes.none()
                )

        else:
            gastos_recurrentes = (
                self.filtrar_recurrentes_propiedad(
                    gastos_recurrentes,
                    propiedad_seleccionada,
                )
            )

        gastos_recurrentes = (
            gastos_recurrentes.order_by(
                "-activo",
                "nombre",
            )
        )

        gastos_recurrentes_activos = (
            gastos_recurrentes.filter(
                activo=True
            )
        )

        gastos_recurrentes_inactivos = (
            gastos_recurrentes.filter(
                activo=False
            )
        )

        total_recurrentes_activos = (
            gastos_recurrentes_activos.count()
        )

        total_recurrentes_inactivos = (
            gastos_recurrentes_inactivos.count()
        )

        total_fijo_mensual = (
            self.calcular_total_fijo_mensual(
                recurrentes=(
                    gastos_recurrentes_activos
                ),
                pais=pais_actual,
            )
        )

        # =====================================================
        # PREVISIÓN DEL MES ACTUAL
        # =====================================================

        prevision = (
            self.calcular_prevision_mensual(
                year=hoy.year,
                month=hoy.month,
                gastos_reales=(
                    gastos_mes_actual
                ),
                recurrentes=(
                    gastos_recurrentes_activos
                ),
                campo_importe=campo_importe,
                pais=pais_actual,
            )
        )

        total_esperado_mes = (
            prevision["total_esperado"]
        )

        pendiente_previsto_mes = (
            prevision[
                "pendiente_previsto"
            ]
        )

        grafico_esperado_labels = (
            prevision["labels"]
        )

        grafico_esperado_valores = (
            prevision["esperados"]
        )

        grafico_esperado_reales = (
            prevision["reales"]
        )

        grafico_esperado_colores = (
            prevision["colores"]
        )

        # =====================================================
        # MOVIMIENTOS
        # Por defecto: últimos diez de cualquier mes.
        # Si el usuario envía mes: solo ese mes.
        # =====================================================

        movimientos_base = gastos_base

        if periodo_explicito:
            movimientos_base = (
                movimientos_base.filter(
                    fecha__year=year,
                    fecha__month=month,
                )
            )

        movimientos_base, _ = (
            self.filtrar_eleccion(
                queryset=movimientos_base,
                campo="categoria",
                valor=categoria_seleccionada,
                opciones=Gasto.CATEGORIAS,
            )
        )

        vistas_validas = {
            "ultimos",
            "fijos",
            "puntuales",
            "sin_factura",
        }

        if vista_listado not in vistas_validas:
            vista_listado = "ultimos"

        condicion_gasto_fijo = (
            Q(
                gasto_recurrente__isnull=False
            )
            | Q(
                generado_automaticamente=True
            )
            | Q(
                tipo="recurrente"
            )
        )

        movimientos_recientes = (
            movimientos_base
        )

        if vista_listado == "fijos":
            movimientos_recientes = (
                movimientos_recientes.filter(
                    condicion_gasto_fijo
                )
            )

        elif vista_listado == "puntuales":
            movimientos_recientes = (
                movimientos_recientes.exclude(
                    condicion_gasto_fijo
                )
            )

        elif vista_listado == "sin_factura":
            movimientos_recientes = (
                movimientos_recientes
                .filter(
                    destino_gestoria="gestoria",
                )
                .filter(
                    Q(justificante="")
                    | Q(
                        justificante__isnull=True
                    )
                )
            )

        movimientos_recientes = (
            movimientos_recientes
            .select_related(
                "propiedad",
                "habitacion",
                "proyecto",
                "gasto_recurrente",
            )
            .order_by(
                "-fecha",
                "-fecha_creacion",
            )
        )

        numero_movimientos_listado = (
            movimientos_recientes.count()
        )

        movimientos_recientes = (
            movimientos_recientes[:10]
        )

        # =====================================================
        # PENDIENTES RECURRENTES
        # =====================================================

        gastos_pendientes = (
            GastoPendiente.objects
            .filter(
                estado="pendiente",
                gasto_recurrente__pais=(
                    pais_actual
                ),
            )
            .select_related(
                "gasto_recurrente",
                "gasto_recurrente__propiedad",
                "gasto_recurrente__habitacion",
                "gasto_recurrente__proyecto",
                "gasto_creado",
            )
        )

        if es_argentina:
            if proyecto_actual:
                gastos_pendientes = (
                    gastos_pendientes.filter(
                        gasto_recurrente__proyecto=(
                            proyecto_actual
                        )
                    )
                )
            else:
                gastos_pendientes = (
                    gastos_pendientes.none()
                )

        else:
            gastos_pendientes = (
                self.filtrar_pendientes_propiedad(
                    gastos_pendientes,
                    propiedad_seleccionada,
                )
            )

        gastos_pendientes = (
            gastos_pendientes.order_by(
                "fecha_programada",
                "fecha_creacion",
            )
        )

        gastos_pendientes_hoy = (
            gastos_pendientes.filter(
                fecha_programada=hoy,
            )
        )

        gastos_pendientes_vencidos = (
            gastos_pendientes.filter(
                fecha_programada__lt=hoy,
            )
        )

        gastos_pendientes_futuros = (
            gastos_pendientes.filter(
                fecha_programada__gt=hoy,
            )
        )

        numero_gastos_pendientes = (
            gastos_pendientes.count()
        )

        numero_gastos_vencidos = (
            gastos_pendientes_vencidos.count()
        )

        numero_gastos_pendientes_hoy = (
            gastos_pendientes_hoy.count()
        )

        # =====================================================
        # GESTORÍA
        # También queda separada por país.
        # =====================================================

        gastos_gestoria = (
            gastos_sin_filtros
            .filter(
                destino_gestoria="gestoria",
                fecha__year=gestoria_anio,
                fecha__month__in=(
                    meses_trimestre
                ),
            )
        )

        gastos_internos = (
            gastos_sin_filtros
            .filter(
                destino_gestoria="interno",
                fecha__year=gestoria_anio,
                fecha__month__in=(
                    meses_trimestre
                ),
            )
        )

        if es_espana:
            gastos_gestoria, _ = (
                self.filtrar_propiedad(
                    gastos_gestoria,
                    propiedad_seleccionada,
                )
            )

            gastos_internos, _ = (
                self.filtrar_propiedad(
                    gastos_internos,
                    propiedad_seleccionada,
                )
            )

        gastos_gestoria = (
            gastos_gestoria.order_by(
                "fecha",
                "propiedad__nombre",
                "proyecto__nombre",
                "categoria",
            )
        )

        gastos_internos = (
            gastos_internos.order_by(
                "fecha",
                "propiedad__nombre",
                "proyecto__nombre",
                "categoria",
            )
        )

        gastos_gestoria_completos = (
            gastos_gestoria.exclude(
                Q(justificante="")
                | Q(
                    justificante__isnull=True
                )
            )
        )

        gastos_gestoria_sin_justificante = (
            gastos_gestoria.filter(
                Q(justificante="")
                | Q(
                    justificante__isnull=True
                )
            )
        )

        gastos_gestoria_pagados = (
            gastos_gestoria.filter(
                pagado=True
            )
        )

        gastos_gestoria_no_pagados = (
            gastos_gestoria.filter(
                pagado=False
            )
        )

        numero_gastos_gestoria = (
            gastos_gestoria.count()
        )

        numero_gastos_gestoria_completos = (
            gastos_gestoria_completos.count()
        )

        numero_gastos_gestoria_sin_justificante = (
            gastos_gestoria_sin_justificante.count()
        )

        numero_gastos_internos = (
            gastos_internos.count()
        )

        total_gastos_gestoria = (
            self.sumar_importes(
                gastos_gestoria,
                campo_importe,
            )
        )

        total_gastos_gestoria_completos = (
            self.sumar_importes(
                gastos_gestoria_completos,
                campo_importe,
            )
        )

        total_gastos_gestoria_sin_justificante = (
            self.sumar_importes(
                gastos_gestoria_sin_justificante,
                campo_importe,
            )
        )

        total_gastos_internos = (
            self.sumar_importes(
                gastos_internos,
                campo_importe,
            )
        )

        gestoria_lista = (
            numero_gastos_gestoria > 0
            and (
                numero_gastos_gestoria_sin_justificante
                == 0
            )
            and numero_gastos_pendientes == 0
        )

        # =====================================================
        # CONTEXTO
        # =====================================================

        context = {
            "hoy": hoy,

            # Espacio financiero
            "pais_actual": pais_actual,
            "es_espana": es_espana,
            "es_argentina": es_argentina,
            "codigo_moneda": codigo_moneda,
            "simbolo_moneda": simbolo_moneda,
            "campo_importe": campo_importe,

            # Proyectos
            "proyectos_disponibles":
                proyectos_disponibles,
            "proyecto_actual": proyecto_actual,
            "proyecto_seleccionado":
                proyecto_seleccionado,

            # Movimientos
            "gastos": gastos,
            "movimientos_recientes":
                movimientos_recientes,
            "vista_listado": vista_listado,
            "numero_movimientos_listado":
                numero_movimientos_listado,
            "periodo_explicito":
                periodo_explicito,

            # Periodos
            "mes_seleccionado":
                mes_seleccionado,
            "anio_seleccionado": year,
            "nombre_mes_seleccionado":
                self.nombre_mes(month),
            "nombre_mes_actual":
                self.nombre_mes(hoy.month),
            "nombre_mes_anterior":
                self.nombre_mes(mes_anterior),
            "anio_mes_anterior":
                anio_anterior,

            # Resumen
            "total_fijo_mensual":
                total_fijo_mensual,
            "total_mes_actual":
                total_mes_actual,
            "total_mes_anterior":
                total_mes_anterior,
            "total_esperado_mes":
                total_esperado_mes,
            "pendiente_previsto_mes":
                pendiente_previsto_mes,
            "diferencia_mensual":
                diferencia_mensual,
            "porcentaje_diferencia_mensual":
                porcentaje_diferencia_mensual,

            "total_gastos":
                total_gastos_filtrados,
                        "total_historico":
                total_historico,
            "total_gastos_mes":
                total_gastos_mes,
            "total_gastos_anio":
                total_gastos_anio,
            "total_pendiente":
                total_pendiente,
            "total_mejoras":
                total_mejoras,
            "ingresos_mensuales":
                ingresos_mensuales,
            "beneficio_estimado":
                beneficio_estimado,
            "mostrar_ingresos":
                es_espana,

            # Conversión argentina
            "gastos_sin_conversion":
                gastos_sin_conversion,
            "numero_sin_conversion":
                numero_sin_conversion,
            "hay_gastos_sin_conversion":
                numero_sin_conversion > 0,

            # Recurrentes
            "gastos_recurrentes":
                gastos_recurrentes,
            "gastos_recurrentes_activos":
                gastos_recurrentes_activos,
            "gastos_recurrentes_inactivos":
                gastos_recurrentes_inactivos,
            "total_recurrentes_activos":
                total_recurrentes_activos,
            "total_recurrentes_inactivos":
                total_recurrentes_inactivos,

            # Pendientes
            "gastos_pendientes":
                gastos_pendientes,
            "gastos_pendientes_hoy":
                gastos_pendientes_hoy,
            "gastos_pendientes_vencidos":
                gastos_pendientes_vencidos,
            "gastos_pendientes_futuros":
                gastos_pendientes_futuros,
            "numero_gastos_pendientes":
                numero_gastos_pendientes,
            "numero_gastos_vencidos":
                numero_gastos_vencidos,
            "numero_gastos_pendientes_hoy":
                numero_gastos_pendientes_hoy,
            "hay_gastos_pendientes":
                numero_gastos_pendientes > 0,

            # Gestoría
            "gastos_para_gestoria":
                gastos_gestoria,
            "gastos_gestoria_completos":
                gastos_gestoria_completos,
            "gastos_gestoria_sin_justificante":
                gastos_gestoria_sin_justificante,
            "gastos_gestoria_pagados":
                gastos_gestoria_pagados,
            "gastos_gestoria_no_pagados":
                gastos_gestoria_no_pagados,
            "gastos_internos":
                gastos_internos,
            "numero_gastos_gestoria":
                numero_gastos_gestoria,
            "numero_gastos_gestoria_completos":
                numero_gastos_gestoria_completos,
            "numero_gastos_gestoria_sin_justificante":
                numero_gastos_gestoria_sin_justificante,
            "numero_gastos_internos":
                numero_gastos_internos,
            "total_gastos_gestoria":
                total_gastos_gestoria,
            "total_gastos_gestoria_completos":
                total_gastos_gestoria_completos,
            "total_gastos_gestoria_sin_justificante":
                total_gastos_gestoria_sin_justificante,
            "total_gastos_internos":
                total_gastos_internos,
            "gestoria_lista":
                gestoria_lista,
            "gestoria_anio":
                gestoria_anio,
            "gestoria_trimestre":
                gestoria_trimestre,
            "gestoria_periodo": (
                f"{self.NOMBRES_TRIMESTRES[gestoria_trimestre]} "
                f"de {gestoria_anio}"
            ),
            "trimestres": list(
                self.NOMBRES_TRIMESTRES.items()
            ),

            # Filtros
            "propiedades": (
                Flat.objects
                .all()
                .order_by("nombre")
                if es_espana
                else Flat.objects.none()
            ),
            "categorias": Gasto.CATEGORIAS,
            "tipos": Gasto.TIPOS,
            "ambitos": Gasto.AMBITOS,
            "propiedad_seleccionada":
                propiedad_seleccionada,
            "categoria_seleccionada":
                categoria_seleccionada,
            "tipo_seleccionado":
                tipo_seleccionado,
            "ambito_seleccionado":
                ambito_seleccionado,
            "estado_seleccionado":
                estado_seleccionado,

            # Gráfico del mes
            "grafico_mes_labels":
                grafico_mes["labels"],
            "grafico_mes_valores":
                grafico_mes["valores"],
            "grafico_mes_colores":
                grafico_mes["colores"],

            # Gráfico del mes anterior
            "grafico_mes_anterior_labels":
                grafico_mes_anterior["labels"],
            "grafico_mes_anterior_valores":
                grafico_mes_anterior["valores"],
            "grafico_mes_anterior_colores":
                grafico_mes_anterior["colores"],

            # Gráfico anual
            "grafico_anio_labels":
                grafico_anio["labels"],
            "grafico_anio_valores":
                grafico_anio["valores"],
            "grafico_anio_colores":
                grafico_anio["colores"],

            # Previsión
            "grafico_esperado_labels":
                grafico_esperado_labels,
            "grafico_esperado_valores":
                grafico_esperado_valores,
            "grafico_esperado_reales":
                grafico_esperado_reales,
            "grafico_esperado_colores":
                grafico_esperado_colores,

            # Compatibilidad
            "comparativa_labels": [
                "Previsto",
                self.nombre_mes(
                    hoy.month
                ),
                self.nombre_mes(
                    mes_anterior
                ),
            ],
            "comparativa_valores": [
                float(total_esperado_mes),
                float(total_mes_actual),
                float(total_mes_anterior),
            ],
            "comparativa_colores": [
                "#745f6d",
                "#72a5a1",
                "#c9a7ad",
            ],
        }

        return render(
            request,
            self.template_name,
            context,
        )

    # =========================================================
    # PROYECTO
    # =========================================================

    @staticmethod
    def obtener_proyecto(
        queryset,
        proyecto_seleccionado,
    ):
        if proyecto_seleccionado:
            try:
                proyecto_id = int(
                    proyecto_seleccionado
                )

            except (
                TypeError,
                ValueError,
            ):
                proyecto_id = None

            if proyecto_id:
                proyecto = queryset.filter(
                    pk=proyecto_id
                ).first()

                if proyecto:
                    return proyecto

        return queryset.first()

    # =========================================================
    # FIJO MENSUAL
    # =========================================================

    def calcular_total_fijo_mensual(
        self,
        recurrentes,
        pais,
    ):
        total = Decimal("0.00")

        for recurrente in recurrentes:
            importe = (
                self.obtener_importe_recurrente(
                    recurrente=recurrente,
                    pais=pais,
                )
            )

            if importe is None:
                continue

            divisor = (
                self.DIVISORES_FRECUENCIA.get(
                    recurrente.frecuencia,
                    Decimal("1"),
                )
            )

            total += importe / divisor

        return total.quantize(
            Decimal("0.01")
        )

    def obtener_importe_recurrente(
        self,
        recurrente,
        pais,
    ):
        if pais == "ES":
            return recurrente.importe

        ultimo_gasto = (
            Gasto.objects
            .filter(
                gasto_recurrente=recurrente,
                anulado=False,
                importe_usd__isnull=False,
            )
            .order_by(
                "-fecha",
                "-fecha_creacion",
            )
            .first()
        )

        if ultimo_gasto:
            return ultimo_gasto.importe_usd

        return None

    # =========================================================
    # PREVISIÓN
    # =========================================================

    def calcular_prevision_mensual(
        self,
        year,
        month,
        gastos_reales,
        recurrentes,
        campo_importe,
        pais,
    ):
        etiquetas = dict(
            Gasto.CATEGORIAS
        )

        reales_por_categoria = {
            fila["categoria"]: (
                fila["total"]
                or Decimal("0.00")
            )
            for fila in (
                gastos_reales
                .values("categoria")
                .annotate(
                    total=Sum(
                        campo_importe
                    )
                )
            )
        }

        esperados_por_categoria = dict(
            reales_por_categoria
        )

        ids_recurrentes_generados = set(
            gastos_reales
            .exclude(
                gasto_recurrente__isnull=True
            )
            .values_list(
                "gasto_recurrente_id",
                flat=True,
            )
        )

        inicio_mes = date(
            year,
            month,
            1,
        )

        ultimo_dia = calendar.monthrange(
            year,
            month,
        )[1]

        fin_mes = date(
            year,
            month,
            ultimo_dia,
        )

        for recurrente in recurrentes:
            if (
                recurrente.pk
                in ids_recurrentes_generados
            ):
                continue

            if not self.recurrente_corresponde_al_mes(
                recurrente,
                year,
                month,
            ):
                continue

            importe_estimado = (
                self.obtener_importe_estimado_recurrente(
                    recurrente=recurrente,
                    inicio_mes=inicio_mes,
                    fin_mes=fin_mes,
                    pais=pais,
                )
            )

            if importe_estimado is None:
                continue

            categoria = (
                recurrente.categoria
                or "otros"
            )

            esperados_por_categoria[categoria] = (
                esperados_por_categoria.get(
                    categoria,
                    Decimal("0.00"),
                )
                + importe_estimado
            )

        categorias = (
            set(esperados_por_categoria)
            | set(reales_por_categoria)
        )

        categorias_ordenadas = sorted(
            categorias,
            key=lambda categoria: (
                -esperados_por_categoria.get(
                    categoria,
                    Decimal("0.00"),
                ),
                categoria,
            ),
        )

        labels = []
        esperados = []
        reales = []
        colores = []

        for categoria in categorias_ordenadas:
            esperado = (
                esperados_por_categoria.get(
                    categoria,
                    Decimal("0.00"),
                )
            )

            real = (
                reales_por_categoria.get(
                    categoria,
                    Decimal("0.00"),
                )
            )

            if not esperado and not real:
                continue

            labels.append(
                etiquetas.get(
                    categoria,
                    categoria
                    .replace("_", " ")
                    .title(),
                )
            )

            esperados.append(
                float(esperado)
            )

            reales.append(
                float(real)
            )

            colores.append(
                self.COLORES_CATEGORIAS.get(
                    categoria,
                    "#aaa0a4",
                )
            )

        total_esperado = sum(
            esperados_por_categoria.values(),
            Decimal("0.00"),
        )

        total_real = sum(
            reales_por_categoria.values(),
            Decimal("0.00"),
        )

        pendiente_previsto = max(
            total_esperado - total_real,
            Decimal("0.00"),
        )

        return {
            "labels": labels,
            "esperados": esperados,
            "reales": reales,
            "colores": colores,
            "total_esperado":
                total_esperado,
            "total_real": total_real,
            "pendiente_previsto":
                pendiente_previsto,
        }

    def obtener_importe_estimado_recurrente(
        self,
        recurrente,
        inicio_mes,
        fin_mes,
        pais,
    ):
        if pais == "ES":
            if recurrente.importe is not None:
                return recurrente.importe

        ultimo_gasto = (
            Gasto.objects
            .filter(
                gasto_recurrente=recurrente,
                anulado=False,
                fecha__lt=inicio_mes,
            )
            .order_by(
                "-fecha",
                "-fecha_creacion",
            )
            .first()
        )

        if ultimo_gasto:
            if pais == "AR":
                return ultimo_gasto.importe_usd

            return ultimo_gasto.importe

        if pais == "AR":
            return None

        return getattr(
            recurrente,
            "importe_estimado",
            None,
        )

    def recurrente_corresponde_al_mes(
        self,
        recurrente,
        year,
        month,
    ):
        fecha_inicio = recurrente.fecha_inicio

        if not fecha_inicio:
            return False

        ultimo_dia = calendar.monthrange(
            year,
            month,
        )[1]

        dia_generacion = min(
            recurrente.dia_generacion or 1,
            ultimo_dia,
        )

        fecha_programada = date(
            year,
            month,
            dia_generacion,
        )

        if fecha_programada < fecha_inicio:
            return False

        if (
            recurrente.fecha_fin
            and fecha_programada
            > recurrente.fecha_fin
        ):
            return False

        frecuencia = recurrente.frecuencia

        if frecuencia == "anual":
            mes_generacion = (
                recurrente.mes_generacion
                or fecha_inicio.month
            )

            return (
                month == mes_generacion
            )

        intervalo = (
            self.MESES_FRECUENCIA.get(
                frecuencia
            )
        )

        if intervalo is None:
            return False

        meses_transcurridos = (
            (year - fecha_inicio.year) * 12
            + month
            - fecha_inicio.month
        )

        return (
            meses_transcurridos >= 0
            and (
                meses_transcurridos
                % intervalo
                == 0
            )
        )

    # =========================================================
    # AUXILIARES
    # =========================================================

    @staticmethod
    def obtener_periodo(
        mes_seleccionado,
        hoy,
    ):
        try:
            year, month = map(
                int,
                mes_seleccionado.split("-"),
            )

            if not 1 <= month <= 12:
                raise ValueError

        except (
            AttributeError,
            TypeError,
            ValueError,
        ):
            year = hoy.year
            month = hoy.month

        return (
            year,
            month,
            f"{year}-{month:02d}",
        )

    @staticmethod
    def obtener_entero(
        valor,
        valor_por_defecto,
    ):
        try:
            return int(valor)

        except (
            TypeError,
            ValueError,
        ):
            return valor_por_defecto

    @staticmethod
    def obtener_meses_trimestre(
        trimestre,
    ):
        primer_mes = (
            ((trimestre - 1) * 3) + 1
        )

        return [
            primer_mes,
            primer_mes + 1,
            primer_mes + 2,
        ]

    @staticmethod
    def nombre_mes(month):
        nombres = [
            "",
            "Enero",
            "Febrero",
            "Marzo",
            "Abril",
            "Mayo",
            "Junio",
            "Julio",
            "Agosto",
            "Septiembre",
            "Octubre",
            "Noviembre",
            "Diciembre",
        ]

        return nombres[month]

    @staticmethod
    def sumar_importes(
        queryset,
        campo_importe,
    ):
        return (
            queryset.aggregate(
                total=Sum(
                    campo_importe
                )
            )["total"]
            or Decimal("0.00")
        )

    def datos_por_categoria(
        self,
        queryset,
        campo_importe,
    ):
        etiquetas = dict(
            Gasto.CATEGORIAS
        )

        resultados = (
            queryset
            .values("categoria")
            .annotate(
                total=Sum(
                    campo_importe
                )
            )
            .order_by("-total")
        )

        labels = []
        valores = []
        colores = []

        for resultado in resultados:
            categoria = (
                resultado["categoria"]
            )

            total = (
                resultado["total"]
                or Decimal("0.00")
            )

            if not total:
                continue

            labels.append(
                etiquetas.get(
                    categoria,
                    categoria
                    .replace("_", " ")
                    .title(),
                )
            )

            valores.append(
                float(total)
            )

            colores.append(
                self.COLORES_CATEGORIAS.get(
                    categoria,
                    "#aaa0a4",
                )
            )

        return {
            "labels": labels,
            "valores": valores,
            "colores": colores,
        }

    @staticmethod
    def filtrar_propiedad(
        queryset,
        propiedad_seleccionada,
    ):
        if not propiedad_seleccionada:
            return queryset, ""

        if propiedad_seleccionada == "empresa":
            return (
                queryset.filter(
                    ambito="empresa",
                    propiedad__isnull=True,
                ),
                "empresa",
            )

        try:
            propiedad_id = int(
                propiedad_seleccionada
            )

        except (
            TypeError,
            ValueError,
        ):
            return queryset, ""

        return (
            queryset.filter(
                propiedad_id=propiedad_id,
            ),
            propiedad_id,
        )

    @staticmethod
    def filtrar_recurrentes_propiedad(
        queryset,
        propiedad_seleccionada,
    ):
        if not propiedad_seleccionada:
            return queryset

        if propiedad_seleccionada == "empresa":
            return queryset.filter(
                ambito="empresa",
                propiedad__isnull=True,
            )

        try:
            propiedad_id = int(
                propiedad_seleccionada
            )

        except (
            TypeError,
            ValueError,
        ):
            return queryset

        return queryset.filter(
            propiedad_id=propiedad_id,
        )

    @staticmethod
    def filtrar_pendientes_propiedad(
        queryset,
        propiedad_seleccionada,
    ):
        if not propiedad_seleccionada:
            return queryset

        if propiedad_seleccionada == "empresa":
            return queryset.filter(
                gasto_recurrente__ambito=(
                    "empresa"
                ),
                gasto_recurrente__propiedad__isnull=(
                    True
                ),
            )

        try:
            propiedad_id = int(
                propiedad_seleccionada
            )

        except (
            TypeError,
            ValueError,
        ):
            return queryset

        return queryset.filter(
            gasto_recurrente__propiedad_id=(
                propiedad_id
            ),
        )

    @staticmethod
    def filtrar_eleccion(
        queryset,
        campo,
        valor,
        opciones,
    ):
        valores_validos = {
            opcion
            for opcion, etiqueta in opciones
        }

        if valor not in valores_validos:
            return queryset, ""

        return (
            queryset.filter(
                **{
                    campo: valor,
                }
            ),
            valor,
        )


class CompletarGastoPendienteView(
    LoginRequiredMixin,
    View,
):
    template_name = (
        "hotel/gastos/"
        "completar_gasto_pendiente.html"
    )

    def get(self, request, pk):
        pendiente = get_object_or_404(
            GastoPendiente.objects
            .select_related(
                "gasto_recurrente",
                "gasto_recurrente__propiedad",
                "gasto_recurrente__habitacion",
            ),
            pk=pk,
            estado="pendiente",
        )

        form = CompletarGastoPendienteForm()

        return render(
            request,
            self.template_name,
            {
                "pendiente": pendiente,
                "form": form,
            },
        )

    @transaction.atomic
    def post(self, request, pk):
        pendiente = get_object_or_404(
            GastoPendiente.objects
            .select_for_update()
            .select_related(
                "gasto_recurrente",
            ),
            pk=pk,
            estado="pendiente",
        )

        form = CompletarGastoPendienteForm(
            request.POST,
            request.FILES,
        )

        if not form.is_valid():
            return render(
                request,
                self.template_name,
                {
                    "pendiente": pendiente,
                    "form": form,
                },
            )

        recurrente = pendiente.gasto_recurrente

        gasto = Gasto.objects.create(
            propiedad=recurrente.propiedad,
            habitacion=recurrente.habitacion,
            ambito=recurrente.ambito,
            tipo="recurrente",
            concepto=(
                recurrente.concepto
                or recurrente.nombre
            ),
            categoria=recurrente.categoria,
            importe=form.cleaned_data["importe"],
            fecha=pendiente.fecha_programada,
            pagado=form.cleaned_data["pagado"],
            proveedor=recurrente.proveedor,
            justificante=(
                form.cleaned_data["justificante"]
            ),
            gasto_recurrente=recurrente,
            periodo_recurrente=pendiente.periodo,
            generado_automaticamente=True,
            destino_gestoria=(
                recurrente.destino_gestoria
            ),
        )

        pendiente.gasto_creado = gasto
        pendiente.estado = "completado"
        pendiente.fecha_completado = (
            timezone.now()
        )

        pendiente.save(
            update_fields=[
                "gasto_creado",
                "estado",
                "fecha_completado",
            ]
        )

        messages.success(
            request,
            (
                f'El gasto "{recurrente.nombre}" '
                "se ha completado correctamente."
            ),
        )

        return redirect(
            "hotel:gastos_dashboard"
        )

# =========================================================
# CREAR GASTO INDIVIDUAL
# =========================================================

class CrearGastoView(
    LoginRequiredMixin,
    View,
):
    template_name = "hotel/gasto_form.html"

    def get(self, request):
        propiedad_id = request.GET.get(
            "propiedad",
        )

        hoy = timezone.localdate()

        form = GastoForm(
            propiedad_id=propiedad_id,
            initial={
                "pagado": True,
                "fecha": hoy,
                "fecha_inicio": hoy,
                "dia_generacion": hoy.day,
                "mes_generacion": hoy.month,
                "requiere_justificante": True,
            },
        )

        return self.render_form(
            request=request,
            form=form,
        )

    def post(self, request):
        propiedad_id = request.POST.get(
            "propiedad",
        )

        form = GastoForm(
            request.POST,
            request.FILES,
            propiedad_id=propiedad_id,
        )

        if not form.is_valid():
            print("\n===== ERROR AL CREAR GASTO =====")
            print(form.errors.as_json())
            print("Datos recibidos:", request.POST)
            print("Archivos recibidos:", request.FILES)
            print("================================\n")
            messages.error(
                request,
                "Revisa los campos señalados.",
            )

            return self.render_form(
                request=request,
                form=form,
            )

        datos = form.cleaned_data

        gasto = form.save(
            commit=False,
        )

        gasto.generado_automaticamente = False

        try:
            aplicar_conversion_gasto(
                gasto=gasto,
                cotizacion_manual=datos.get(
                    "cotizacion_usd"
                ),
            )

        except CotizacionNoDisponible as error:
            form.add_error(
                "cotizacion_usd",
                (
                    f"{error} Introduce manualmente "
                    "el dólar blue venta utilizado."
                ),
            )

            messages.error(
                request,
                (
                    "No se pudo obtener la cotización "
                    "automáticamente."
                ),
            )

            return self.render_form(
                request=request,
                form=form,
            )

        es_recurrente = datos.get(
            "es_recurrente",
            False,
        )

        with transaction.atomic():
            if es_recurrente:
                recurrente = self.crear_recurrencia(
                    datos=datos,
                    gasto=gasto,
                )

                fecha_periodo = (
                        datos.get("fecha")
                        or datos.get("fecha_inicio")
                        or timezone.localdate()
                )

                gasto.gasto_recurrente = recurrente
                gasto.periodo_recurrente = (
                    fecha_periodo.replace(day=1)
                )
                gasto.tipo = "recurrente"
                gasto.generado_automaticamente = False

            else:
                gasto.gasto_recurrente = None
                gasto.periodo_recurrente = None
                gasto.tipo = "extraordinario"
                gasto.generado_automaticamente = False

            gasto.save()
            form.save_m2m()

        if es_recurrente:
            mensaje = (
                f'El gasto fijo "{gasto.titulo}" '
                "se ha registrado correctamente. "
                "Los próximos movimientos se "
                "generarán automáticamente."
            )

        else:
            mensaje = (
                f'El gasto esporádico "{gasto.titulo}" '
                "se ha registrado correctamente."
            )

        if (
            gasto.pais == "AR"
            and gasto.importe_usd is not None
        ):
            mensaje += (
                " Equivalencia registrada: "
                f"{gasto.importe_usd} USD."
            )

        messages.success(
            request,
            mensaje,
        )

        return redirect(
            "hotel:gastos_dashboard"
        )

    def crear_recurrencia(
        self,
        datos,
        gasto,
    ):
        concepto = (
            datos.get("concepto")
            or ""
        ).strip()

        proveedor = (
            datos.get("proveedor")
            or ""
        ).strip()

        nombre = (
            concepto
            or proveedor
            or gasto.get_categoria_display()
            or "Gasto fijo"
        )

        fecha_inicio = (
            datos.get("fecha_inicio")
            or datos.get("fecha")
            or timezone.localdate()
        )

        recurrente = (
            GastoRecurrente.objects.create(
                nombre=nombre,
                pais=datos.get("pais"),
                ambito=datos.get("ambito"),
                propiedad=datos.get(
                    "propiedad"
                ),
                habitacion=datos.get(
                    "habitacion"
                ),
                proyecto=datos.get(
                    "proyecto"
                ),
                categoria=datos.get(
                    "categoria"
                ),
                tipo_suministro=datos.get(
                    "tipo_suministro",
                    "",
                ),
                tipo="recurrente",
                importe=datos.get("importe"),
                proveedor=proveedor,
                concepto=concepto,
                frecuencia=datos.get(
                    "frecuencia"
                ),
                dia_generacion=datos.get(
                    "dia_generacion"
                ),
                mes_generacion=datos.get(
                    "mes_generacion"
                ),
                fecha_inicio=fecha_inicio,
                fecha_fin=datos.get(
                    "fecha_fin"
                ),
                pagado_por_defecto=datos.get(
                    "pagado",
                    True,
                ),
                requiere_justificante=datos.get(
                    "requiere_justificante",
                    True,
                ),
                destino_gestoria=datos.get(
                    "destino_gestoria"
                ),
                notas=datos.get(
                    "notas",
                    "",
                ),
                activo=True,
            )
        )

        return recurrente

    def render_form(
        self,
        request,
        form,
    ):
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "titulo": "Registrar gasto",
                "subtitulo": (
                    "Añade un gasto esporádico "
                    "o configura un gasto fijo."
                ),
                "texto_boton": "Guardar gasto",
                "es_recurrente": bool(
                    form["es_recurrente"].value()
                ),
            },
        )

# =========================================================
# EDITAR GASTO INDIVIDUAL
# =========================================================

class EditarGastoView(
    LoginRequiredMixin,
    View,
):
    template_name = "hotel/gasto_form.html"

    extensiones_justificante = {
        ".pdf",
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
    }

    tamaño_maximo_justificante = (
        10 * 1024 * 1024
    )

    def obtener_gasto(self, pk):
        return get_object_or_404(
            Gasto.objects.select_related(
                "propiedad",
                "habitacion",
                "proyecto",
                "gasto_recurrente",
            ),
            pk=pk,
            anulado=False,
        )

    def obtener_destino(self, request):
        destino = request.POST.get(
            "next",
            "",
        )

        if (
            destino
            and url_has_allowed_host_and_scheme(
                url=destino,
                allowed_hosts={
                    request.get_host(),
                },
                require_https=request.is_secure(),
            )
        ):
            return destino

        return (
            f"{reverse('hotel:gastos_dashboard')}"
            "?vista_listado=sin_factura"
            "#gestoria"
        )

    def guardar_justificante(
        self,
        request,
        gasto,
    ):
        destino = self.obtener_destino(
            request
        )

        archivo = request.FILES.get(
            "justificante"
        )

        if not archivo:
            messages.error(
                request,
                (
                    "Selecciona una factura "
                    "o un justificante."
                ),
            )

            return redirect(destino)

        extension = Path(
            archivo.name
        ).suffix.lower()

        if (
            extension
            not in self.extensiones_justificante
        ):
            messages.error(
                request,
                (
                    "El justificante debe ser "
                    "PDF, JPG, JPEG, PNG o WEBP."
                ),
            )

            return redirect(destino)

        if (
            archivo.size
            > self.tamaño_maximo_justificante
        ):
            messages.error(
                request,
                (
                    "El justificante no puede "
                    "superar los 10 MB."
                ),
            )

            return redirect(destino)

        gasto.justificante = archivo

        gasto.save(
            update_fields=[
                "justificante",
            ],
        )

        messages.success(
            request,
            (
                f'La factura de "{gasto.titulo}" '
                "se ha subido correctamente."
            ),
        )

        return redirect(destino)

    def get(self, request, pk):
        gasto = self.obtener_gasto(pk)

        form = GastoForm(
            instance=gasto,
            propiedad_id=gasto.propiedad_id,
        )

        return self.render_form(
            request=request,
            form=form,
            gasto=gasto,
        )

    def post(self, request, pk):
        gasto = self.obtener_gasto(pk)

        accion = request.POST.get(
            "accion",
            "editar",
        )

        if accion == "subir_justificante":
            return self.guardar_justificante(
                request=request,
                gasto=gasto,
            )

        propiedad_id = request.POST.get(
            "propiedad",
        )

        form = GastoForm(
            request.POST,
            request.FILES,
            instance=gasto,
            propiedad_id=propiedad_id,
        )

        if not form.is_valid():
            messages.error(
                request,
                (
                    "No se pudieron guardar los cambios. "
                    "Revisa los campos señalados."
                ),
            )

            return self.render_form(
                request=request,
                form=form,
                gasto=gasto,
            )

        datos = form.cleaned_data

        gasto = form.save(
            commit=False,
        )

        try:
            aplicar_conversion_gasto(
                gasto=gasto,
                cotizacion_manual=datos.get(
                    "cotizacion_usd"
                ),
            )

        except CotizacionNoDisponible as error:
            form.add_error(
                "cotizacion_usd",
                (
                    f"{error} Introduce manualmente "
                    "el dólar blue venta utilizado."
                ),
            )

            messages.error(
                request,
                (
                    "No se pudo actualizar la "
                    "conversión del gasto."
                ),
            )

            return self.render_form(
                request=request,
                form=form,
                gasto=gasto,
            )

        with transaction.atomic():
            gasto.save()
            form.save_m2m()

        mensaje = (
            "El gasto se ha actualizado. "
            "Los demás periodos no se han "
            "modificado."
        )

        if (
            gasto.pais == "AR"
            and gasto.importe_usd is not None
        ):
            mensaje += (
                " Equivalencia registrada: "
                f"{gasto.importe_usd} USD."
            )

        messages.success(
            request,
            mensaje,
        )

        return redirect(
            "hotel:gastos_dashboard"
        )

    def render_form(
        self,
        request,
        form,
        gasto,
    ):
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "gasto": gasto,
                "titulo": "Editar gasto",
                "subtitulo": gasto.titulo,
                "texto_boton": "Guardar cambios",
                "es_recurrente": bool(
                    gasto.gasto_recurrente_id
                ),
            },
        )


# =========================================================
# CAMBIAR ESTADO DE PAGO
# =========================================================

class CambiarEstadoGastoView(
    LoginRequiredMixin,
    View,
):
    def post(self, request, pk):
        gasto = get_object_or_404(
            Gasto,
            pk=pk,
            anulado=False,
        )

        gasto.pagado = not gasto.pagado

        gasto.save(
            update_fields=[
                "pagado",
            ]
        )

        if gasto.pagado:
            mensaje = (
                "El gastos se ha marcado como pagado."
            )
        else:
            mensaje = (
                "El gastos se ha marcado como pendiente."
            )

        messages.success(
            request,
            mensaje,
        )

        siguiente = request.POST.get(
            "next",
        )

        if siguiente:
            return redirect(siguiente)

        return redirect(
            "hotel:gastos_dashboard"
        )


# =========================================================
# ELIMINAR O ANULAR GASTO
# =========================================================

class EliminarGastoView(
    LoginRequiredMixin,
    View,
):
    def post(self, request, pk):
        gasto = get_object_or_404(
            Gasto,
            pk=pk,
            anulado=False,
        )

        titulo = gasto.titulo
        siguiente = request.POST.get(
            "next",
        )

        if gasto.gasto_recurrente_id:
            gasto.anulado = True

            gasto.save(
                update_fields=[
                    "anulado",
                ]
            )

            messages.success(
                request,
                (
                    f'El gastos "{titulo}" se ha eliminado '
                    "de este periodo. No volverá a generarse."
                ),
            )

        else:
            gasto.delete()

            messages.success(
                request,
                f'El gastos "{titulo}" ha sido eliminado.',
            )

        if siguiente:
            return redirect(siguiente)

        return redirect(
            "hotel:gastos_dashboard"
        )



class EditarGastoRecurrenteView(
    LoginRequiredMixin,
    View,
):
    template_name = (
        "hotel/gasto_recurrente_editar.html"
    )

    def obtener_recurrente(self, pk):
        return get_object_or_404(
            GastoRecurrente.objects.select_related(
                "propiedad",
                "habitacion",
                "proyecto",
            ),
            pk=pk,
        )

    def get(self, request, pk):
        recurrente = self.obtener_recurrente(
            pk
        )

        form = EditarGastoRecurrenteForm(
            instance=recurrente,
        )

        return self.render_form(
            request=request,
            form=form,
            recurrente=recurrente,
        )

    def post(self, request, pk):
        recurrente = self.obtener_recurrente(
            pk
        )

        form = EditarGastoRecurrenteForm(
            request.POST,
            instance=recurrente,
        )

        if form.is_valid():
            recurrente = form.save()

            messages.success(
                request,
                (
                    f'El gasto fijo "{recurrente.nombre}" '
                    "se ha actualizado. Los movimientos "
                    "ya registrados no se han modificado."
                ),
            )

            return redirect(
                "hotel:gastos_dashboard"
            )

        messages.error(
            request,
            "Revisa los campos señalados.",
        )

        return self.render_form(
            request=request,
            form=form,
            recurrente=recurrente,
        )

    def render_form(
        self,
        request,
        form,
        recurrente,
    ):
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "recurrente": recurrente,
                "titulo": "Editar gasto fijo",
                "subtitulo": (
                    "Los cambios se aplicarán a "
                    "los próximos movimientos."
                ),
                "texto_boton": "Guardar cambios",
            },
        )


class EliminarGastoRecurrenteView(
    LoginRequiredMixin,
    View,
):
    @transaction.atomic
    def post(self, request, pk):
        recurrente = get_object_or_404(
            GastoRecurrente.objects.select_for_update(),
            pk=pk,
        )

        nombre = recurrente.nombre

        movimientos = (
            Gasto.objects
            .filter(
                gasto_recurrente=recurrente,
            )
        )

        numero_movimientos = movimientos.count()

        # Elimina también los archivos físicos asociados.
        for movimiento in movimientos.iterator():
            if movimiento.justificante:
                movimiento.justificante.delete(
                    save=False
                )

        movimientos.delete()

        GastoPendiente.objects.filter(
            gasto_recurrente=recurrente,
        ).delete()

        recurrente.delete()

        messages.success(
            request,
            (
                f'El gasto fijo "{nombre}" se ha '
                f'eliminado junto con {numero_movimientos} '
                "movimiento(s) asociado(s)."
            ),
        )

        return redirect(
            "hotel:gastos_dashboard"
        )


@login_required
def habitaciones_por_propiedad(request):
        propiedad_id = request.GET.get(
            "propiedad_id"
        )

        if not propiedad_id:
            return JsonResponse(
                {
                    "habitaciones": [],
                }
            )

        try:
            propiedad_id = int(propiedad_id)

        except (
                TypeError,
                ValueError,
        ):
            return JsonResponse(
                {
                    "habitaciones": [],
                },
                status=400,
            )

        habitaciones = list(
            Habitacion.objects
            .filter(
                propiedad_id=propiedad_id,
            )
            .order_by("nombre")
            .values(
                "id",
                "nombre",
            )
        )

        return JsonResponse(
            {
                "habitaciones": habitaciones,
            }
        )

@login_required
def proyectos_por_pais(request):
    pais = request.GET.get(
        "pais",
        "",
    ).strip().upper()

    paises_validos = {
        valor
        for valor, etiqueta in Proyecto.PAISES
    }

    if pais not in paises_validos:
        return JsonResponse(
            {
                "proyectos": [],
            }
        )

    proyectos = list(
        Proyecto.objects
        .filter(
            pais=pais,
            activo=True,
        )
        .order_by("nombre")
        .values(
            "id",
            "nombre",
            "provincia",
            "ciudad",
            "tipo",
        )
    )

    return JsonResponse(
        {
            "proyectos": proyectos,
        }
    )

class SubirJustificanteGastoView(
    LoginRequiredMixin,
    View,
):
    extensiones_permitidas = {
        ".pdf",
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
    }

    tamaño_maximo = 10 * 1024 * 1024

    def post(self, request, pk):
        gasto = get_object_or_404(
            Gasto,
            pk=pk,
            anulado=False,
        )

        archivo = request.FILES.get(
            "justificante"
        )

        siguiente = request.POST.get(
            "next"
        )

        if not siguiente:
            siguiente = (
                reverse("hotel:gastos_dashboard")
                + "?vista_listado=sin_factura"
                + "#movimientos"
            )

        if not archivo:
            messages.error(
                request,
                "Selecciona una factura o justificante.",
            )

            return HttpResponseRedirect(siguiente)

        extension = Path(
            archivo.name
        ).suffix.lower()

        if extension not in self.extensiones_permitidas:
            messages.error(
                request,
                (
                    "El justificante debe ser un archivo "
                    "PDF, JPG, JPEG, PNG o WEBP."
                ),
            )

            return HttpResponseRedirect(siguiente)

        if archivo.size > self.tamaño_maximo:
            messages.error(
                request,
                "El justificante no puede superar los 10 MB.",
            )

            return HttpResponseRedirect(siguiente)

        gasto.justificante = archivo

        gasto.save(
            update_fields=[
                "justificante",
            ]
        )

        messages.success(
            request,
            (
                f'Se ha añadido la factura de '
                f'"{gasto.titulo}".'
            ),
        )

        return HttpResponseRedirect(siguiente)

class ProyectosDashboardView(
    LoginRequiredMixin,
    View,
):
    template_name = (
        "hotel/proyectos/proyectos_dashboard.html"
    )

    def get(self, request):
        hoy = timezone.localdate()

        pais_seleccionado = request.GET.get(
            "pais",
            "",
        ).strip().upper()

        estado_seleccionado = request.GET.get(
            "estado",
            "",
        ).strip()

        busqueda = request.GET.get(
            "q",
            "",
        ).strip()

        paises_validos = {
            valor
            for valor, etiqueta in Proyecto.PAISES
        }

        estados_validos = {
            valor
            for valor, etiqueta in Proyecto.ESTADOS
        }

        if pais_seleccionado not in paises_validos:
            pais_seleccionado = ""

        if estado_seleccionado not in estados_validos:
            estado_seleccionado = ""

        proyectos_queryset = (
            Proyecto.objects.all()
        )

        if pais_seleccionado:
            proyectos_queryset = (
                proyectos_queryset.filter(
                    pais=pais_seleccionado,
                )
            )

        if estado_seleccionado:
            proyectos_queryset = (
                proyectos_queryset.filter(
                    estado=estado_seleccionado,
                )
            )

        if busqueda:
            proyectos_queryset = (
                proyectos_queryset.filter(
                    Q(nombre__icontains=busqueda)
                    | Q(ciudad__icontains=busqueda)
                    | Q(provincia__icontains=busqueda)
                    | Q(descripcion__icontains=busqueda)
                )
            )

        proyectos = list(
            proyectos_queryset.order_by(
                "-activo",
                "pais",
                "nombre",
            )
        )

        proyectos_ids = [
            proyecto.pk
            for proyecto in proyectos
        ]

        gastos_proyectos = (
            Gasto.objects
            .filter(
                proyecto_id__in=proyectos_ids,
                anulado=False,
            )
            .select_related("proyecto")
        )

        totales_historicos = self.totales_por_proyecto(
            gastos_proyectos
        )

        totales_anuales = self.totales_por_proyecto(
            gastos_proyectos.filter(
                fecha__year=hoy.year,
            )
        )

        totales_mensuales = self.totales_por_proyecto(
            gastos_proyectos.filter(
                fecha__year=hoy.year,
                fecha__month=hoy.month,
            )
        )

        facturas_pendientes = {
            fila["proyecto_id"]: fila["total"]
            for fila in (
                gastos_proyectos
                .filter(
                    destino_gestoria="gestoria",
                )
                .filter(
                    Q(justificante="")
                    | Q(justificante__isnull=True)
                )
                .values("proyecto_id")
                .annotate(total=Sum("importe"))
            )
        }

        numero_facturas_pendientes = {
            fila["proyecto_id"]: fila["cantidad"]
            for fila in (
                gastos_proyectos
                .filter(
                    destino_gestoria="gestoria",
                )
                .filter(
                    Q(justificante="")
                    | Q(justificante__isnull=True)
                )
                .values("proyecto_id")
                .annotate(
                    cantidad=Count("pk"),
                )
            )
        }

        for proyecto in proyectos:
            proyecto.total_historico = (
                totales_historicos.get(
                    proyecto.pk,
                    Decimal("0.00"),
                )
            )

            proyecto.total_anio = (
                totales_anuales.get(
                    proyecto.pk,
                    Decimal("0.00"),
                )
            )

            proyecto.total_mes = (
                totales_mensuales.get(
                    proyecto.pk,
                    Decimal("0.00"),
                )
            )

            proyecto.total_sin_factura = (
                facturas_pendientes.get(
                    proyecto.pk,
                    Decimal("0.00"),
                )
            )

            proyecto.numero_sin_factura = (
                numero_facturas_pendientes.get(
                    proyecto.pk,
                    0,
                )
            )

            proyecto.moneda = (
                "ARS"
                if proyecto.pais == "AR"
                else "EUR"
            )

            proyecto.simbolo_moneda = (
                "$"
                if proyecto.pais == "AR"
                else "€"
            )

        proyectos_españa = [
            proyecto
            for proyecto in proyectos
            if proyecto.pais == "ES"
        ]

        proyectos_argentina = [
            proyecto
            for proyecto in proyectos
            if proyecto.pais == "AR"
        ]

        total_españa = sum(
            (
                proyecto.total_historico
                for proyecto in proyectos_españa
            ),
            Decimal("0.00"),
        )

        total_argentina = sum(
            (
                proyecto.total_historico
                for proyecto in proyectos_argentina
            ),
            Decimal("0.00"),
        )

        proyectos_activos = [
            proyecto
            for proyecto in proyectos
            if proyecto.activo
        ]

        proyectos_pausados = [
            proyecto
            for proyecto in proyectos
            if proyecto.estado == "pausado"
        ]

        proyectos_finalizados = [
            proyecto
            for proyecto in proyectos
            if proyecto.estado == "finalizado"
        ]

        ultimos_gastos = (
            gastos_proyectos
            .order_by(
                "-fecha",
                "-fecha_creacion",
            )[:10]
        )

        return render(
            request,
            self.template_name,
            {
                "proyectos": proyectos,
                "proyectos_españa": proyectos_españa,
                "proyectos_argentina":
                    proyectos_argentina,

                "numero_proyectos": len(proyectos),
                "numero_activos":
                    len(proyectos_activos),
                "numero_pausados":
                    len(proyectos_pausados),
                "numero_finalizados":
                    len(proyectos_finalizados),

                "total_españa": total_españa,
                "total_argentina": total_argentina,

                "ultimos_gastos": ultimos_gastos,

                "paises": Proyecto.PAISES,
                "estados": Proyecto.ESTADOS,

                "pais_seleccionado":
                    pais_seleccionado,
                "estado_seleccionado":
                    estado_seleccionado,
                "busqueda": busqueda,

                "anio_actual": hoy.year,
            },
        )

    def totales_por_proyecto(
            self,
            queryset,
    ):
        return {
            fila["proyecto_id"]: (
                    fila["total"]
                    or Decimal("0.00")
            )
            for fila in (
                queryset
                .values("proyecto_id")
                .annotate(
                    total=Sum("importe"),
                )
            )
        }

class CrearProyectoView(
    LoginRequiredMixin,
    View,
):
    template_name = (
        "hotel/proyectos/proyecto_form.html"
    )

    def get(self, request):
        form = ProyectoForm(
            initial={
                "pais": "AR",
                "tipo": "aparthotel",
                "estado": "planificacion",
                "activo": True,
            },
        )

        return self.render_form(
            request,
            form,
        )

    def post(self, request):
        form = ProyectoForm(
            request.POST,
        )

        if form.is_valid():
            proyecto = form.save()

            messages.success(
                request,
                (
                    f'El proyecto "{proyecto.nombre}" '
                    "se ha creado correctamente."
                ),
            )

            return redirect(
                "hotel:proyectos_dashboard"
            )

        messages.error(
            request,
            "Revisa los campos señalados.",
        )

        return self.render_form(
            request,
            form,
        )

    def render_form(
        self,
        request,
        form,
    ):
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "titulo": "Crear proyecto",
                "subtitulo": (
                    "Registra un nuevo proyecto "
                    "de By Colección."
                ),
                "texto_boton": "Crear proyecto",
            },
        )


class EditarProyectoView(
    LoginRequiredMixin,
    View,
):
    template_name = (
        "hotel/proyectos/proyecto_form.html"
    )

    def obtener_proyecto(self, pk):
        return get_object_or_404(
            Proyecto,
            pk=pk,
        )

    def get(self, request, pk):
        proyecto = self.obtener_proyecto(pk)

        form = ProyectoForm(
            instance=proyecto,
        )

        return self.render_form(
            request,
            form,
            proyecto,
        )

    def post(self, request, pk):
        proyecto = self.obtener_proyecto(pk)

        form = ProyectoForm(
            request.POST,
            instance=proyecto,
        )

        if form.is_valid():
            proyecto = form.save()

            messages.success(
                request,
                (
                    f'El proyecto "{proyecto.nombre}" '
                    "se ha actualizado."
                ),
            )

            return redirect(
                "hotel:proyectos_dashboard"
            )

        messages.error(
            request,
            "Revisa los campos señalados.",
        )

        return self.render_form(
            request,
            form,
            proyecto,
        )

    def render_form(
        self,
        request,
        form,
        proyecto,
    ):
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "proyecto": proyecto,
                "titulo": "Editar proyecto",
                "subtitulo": (
                    "Actualiza la información y "
                    "el estado del proyecto."
                ),
                "texto_boton": "Guardar cambios",
            },
        )

class CambiarEstadoProyectoView(
    LoginRequiredMixin,
    View,
):
    def post(self, request, pk):
        proyecto = get_object_or_404(
            Proyecto,
            pk=pk,
        )

        nuevo_estado = request.POST.get(
            "estado",
            "",
        )

        estados_validos = {
            valor
            for valor, etiqueta in Proyecto.ESTADOS
        }

        if nuevo_estado not in estados_validos:
            messages.error(
                request,
                "El estado seleccionado no es válido.",
            )

            return redirect(
                "hotel:proyectos_dashboard"
            )

        proyecto.estado = nuevo_estado
        proyecto.activo = (
            nuevo_estado
            not in {
                "pausado",
                "finalizado",
            }
        )

        proyecto.save(
            update_fields=[
                "estado",
                "activo",
            ],
        )

        messages.success(
            request,
            (
                f'El proyecto "{proyecto.nombre}" '
                "ha cambiado de estado."
            ),
        )

        return redirect(
            "hotel:proyectos_dashboard"
        )


@login_required
def crear_ingreso_propiedad(request):
    if request.method == "POST":
        form = IngresoPropiedadForm(
            request.POST,
        )

        if form.is_valid():
            ingreso = form.save()

            messages.success(
                request,
                (
                    f'El ingreso de '
                    f'{ingreso.importe:.2f} € '
                    f'para {ingreso.propiedad} '
                    f'se ha registrado correctamente.'
                ),
            )

            return redirect(
                "hotel:dashboard"
            )

        messages.error(
            request,
            (
                "No se pudo registrar el ingreso. "
                "Revisa los campos señalados."
            ),
        )

    else:
        propiedad_id = request.GET.get(
            "propiedad"
        )

        initial = {
            "fecha": timezone.localdate(),
            "concepto": "Alquiler temporal",
        }

        if propiedad_id:
            initial["propiedad"] = (
                propiedad_id
            )

        form = IngresoPropiedadForm(
            initial=initial,
        )

    return render(
        request,
        "hotel/ingresos/ingreso_form.html",
        {
            "form": form,
            "titulo": "Registrar ingreso",
            "subtitulo": (
                "Añade un cobro de alquiler temporal "
                "a una propiedad."
            ),
            "texto_boton": "Guardar ingreso",
        },
    )