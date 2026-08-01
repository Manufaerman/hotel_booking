import calendar

from datetime import timedelta, date
from decimal import Decimal, ROUND_HALF_UP
from urllib.parse import quote
from django.db.models import Count
from dateutil.relativedelta import relativedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Exists, OuterRef, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView

from .forms import (
    AvalContratoForm,
    ContratoAlquilerForm,
    CrearProcesoFormalizacionForm,
    InquilinoForm,
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
)

from .services.contrato_pdf import generar_contrato_pdf


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


def modificar_inquilino(
    request,
    id,
    contrato_id,
):
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
    flat = Flat.objects.all()
    habitaciones = Habitacion.objects.all()
    return render(request, 'home.html', {'flat': flat, 'habitaciones': habitaciones})


def habitaciones_all(request):
    habitaciones_tolima = Habitacion.objects.filter(propiedad__nombre__icontains='Tolima')
    habitaciones_barichara = Habitacion.objects.filter(propiedad__nombre__icontains='Barichara')
    habitaciones_haro = Habitacion.objects.filter(propiedad__nombre__icontains='Haro')
    return render(request, 'habitaciones_all.html', {'habitaciones_tolima': habitaciones_tolima,
                                                     'habitaciones_barichara': habitaciones_barichara,
                                                     'habitaciones_haro': habitaciones_haro,
                                                     })


def flat_detail(request, id):
    piso = get_object_or_404(Flat, id=id)
    habitaciones = Habitacion.objects.filter(propiedad=piso, disponible=True)
    habitaciones_disponibles = len(habitaciones)
    habitaciones = Habitacion.objects.filter(propiedad=piso)
    return render(request, 'flat.html', {'piso': piso, 'habitaciones': habitaciones, 'habitaciones_disponibles': habitaciones_disponibles})


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
    datos = []
    labels = []
    gasto_por_propiedad = []
    propiedades = Flat.objects.all()
    for propiedad in propiedades:
        gasto_por_propiedad.append(propiedad.gastos.aggregate(total=Sum('importe'))['total'] or 0)
    hoy = timezone.now().date()
    gastos_mes = Gasto.objects.filter(
        fecha__year=hoy.year,
        fecha__month=hoy.month).aggregate(total=Sum("importe")
                                          )["total"] or 0
    for propiedad in propiedades:
        labels.append(propiedad.nombre)
        total = 0
        for habitacion in propiedad.habitaciones.all():
            total += habitacion.precio
        datos.append(total)

    meses_cortos = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                    'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    hoy = timezone.now().date()
    inicio_mes_actual = hoy.replace(day=1)
    labels_meses = []
    facturacion_mensual = []
    for i in range(5, -1, -1):
        mes = inicio_mes_actual - relativedelta(months=i)
        total = ContratoAlquiler.objects.filter(
            activo=True,
            fecha_inicio__lt=mes+relativedelta(months=1),
        ).aggregate(total=Sum('precio_mensual'))['total'] or 0
        labels_meses.append(meses_cortos[mes.month - 1])
        facturacion_mensual.append(float(total))

    data = {'labels': labels,
            'datos': datos,
            'gastos_mes': gastos_mes,
            'gastos_por_propiedad': gasto_por_propiedad,
            'label_meses': labels_meses,
            'labels_meses': labels_meses,
            'facturacion_mensual': facturacion_mensual,

            }
    return JsonResponse(data)

""" I will use jquery and js in order to display the bookings, show in the modals information and change the bookings"""


def dashboard(request):
    rooms = Flat.objects.all()
    mes = date.today().month

    ocupadas = Habitacion.objects.filter(disponible=False).count()
    beneficio_mes = Habitacion.objects.filter(disponible=False, contratos__activo=True).aggregate(total=Sum('precio'))['total'] or 0
    habitaciones_totales = Habitacion.objects.count()
    beneficio_estimado = Habitacion.objects.aggregate(total=Sum('precio'))['total'] or 0
    porcentaje_ocupacion = round((ocupadas/habitaciones_totales)*100, 1)
    print(porcentaje_ocupacion)
    print(Habitacion.objects.filter(disponible=True, contratos__isnull=False).count())
    print(Habitacion.objects.filter(disponible=False).count())

    return render(request, 'dashboard.html',
                      {'rooms': rooms, 'porcentaje_ocupacion': porcentaje_ocupacion, 'habitaciones_totales': habitaciones_totales, 'ocupadas': ocupadas,
                       'beneficio_mes': beneficio_mes, 'beneficio_estimado':beneficio_estimado})


def habitaciones(request, id):
    habitacion = get_object_or_404(Habitacion, id=id)
    return render(request, 'habitacion.html', {'habitacion': habitacion})


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


class NewContractView(
    LoginRequiredMixin,
    View,
):
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