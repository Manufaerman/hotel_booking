import calendar

from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

from dateutil.relativedelta import relativedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Count, Q, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
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
    contrato = get_object_or_404(ContratoAlquiler, id=id)
    propìedad_id = contrato.habitacion.propiedad_id
    print(propìedad_id)

    if not propìedad_id:
        propìedad_id = contrato.habitacion.flat_id
        print(propìedad_id)
    if request.method == 'POST':
        print('no es valido')
        propìedad_id = request.POST.get('propiedad')
        form = ContratoAlquilerForm(request.POST, instance=contrato, propiedad_id=propìedad_id)
        if form.is_valid():
                print('el form es validop la concgha de la lora')
                form.save()
                messages.success(request, 'Contrato modificado correctamente')
                return redirect('hotel:contratos')
    else:
        print('estamos en el else')
        form = ContratoAlquilerForm(instance=contrato)
    return render(request, 'modificar.html', {'form': form, 'contrato': contrato})


def modificar_inquilino(request, id, contrato_id):
    contrato = get_object_or_404(ContratoAlquiler, id=contrato_id)
    inquilino = get_object_or_404(Inquilino, id=id)
    print(inquilino)
    if request.method == 'POST':
        form = InquilinoForm(request.POST, instance=inquilino)
        if form.is_valid():
            form.save()
            messages.success(request, 'Inquilino modificado correctamente')
            return redirect('hotel:contratos')

    else:
        form = InquilinoForm(instance=inquilino)
        return render(request, 'modificar_inquilino.html', {'form': form,
                                                          'contrato': contrato,
                                                          'inquilino': inquilino})
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
    visitas = Visit.objects.order_by('-timestamp')[:100]  # últimas 100
    total = Visit.objects.count()
    return render(request, 'visitas.html', {'visitas': visitas, 'total': total})


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
    habitaciones = Habitacion.objects.all()
    ocupadas = Habitacion.objects.filter(disponible=True).count()
    libres = Habitacion.objects.filter(disponible=True).count()
    ingresos_actuales = Habitacion.objects.filter(disponible=False).aggregate(total=Sum('precio'))['total'] or 0
    dinero_no_entrando = Habitacion.objects.filter(disponible=True).aggregate(total=Sum('precio'))['total'] or 0
    ranking_libres = Flat.objects.annotate(
        libres=Count('habitaciones', filter=Q(habitaciones__disponible=True))
    ).order_by('-libres')
    resumen_propiedades = Flat.objects.annotate(
        total_habitaciones=Count('habitaciones'),
        ocupadas=Count('habitaciones', filter=Q(habitaciones__disponible=False)),
        libres=Count('habitaciones', filter=Q(habitaciones__disponible=True))
    ).order_by('nombre')
    return render(request, 'habitaciones_dashboard.html',
                  {'habitaciones': habitaciones,
                   'total_habitaciones': len(habitaciones),
                   'ocupadas': ocupadas,
                   'libres': libres,
                   'ingresos_actuales': ingresos_actuales,
                   'dinero_no_entrando': dinero_no_entrando,
                   'ranking_libres': ranking_libres,
                   'resumen_propiedades':resumen_propiedades})

def contratos(request):
    contratos = ContratoAlquiler.objects.all()
    return render(request, 'contratos.html', {'contratos': contratos})


class NewContractView(View):
    template_name = "newcontract.html"

    def get(self, request):

        propiedad_id = request.GET.get("propiedad")
        if propiedad_id:
            propiedad_id = int(propiedad_id)
        else:
            propiedad_id = None
        context = {
            "inquilino_form": InquilinoForm(),

            "contrato_form": ContratoAlquilerForm(
                propiedad_id=propiedad_id
            ),

            "aval_form": AvalContratoForm(prefix="aval"),

            "propiedades": Flat.objects.all(),
            "propiedad_id": propiedad_id,
            "tiene_aval": False,
        }

        return render(request, self.template_name, context)

    def post(self, request):
        propiedad_id = request.POST.get("propiedad")
        tiene_aval = request.POST.get("tiene_aval") == "on"

        inquilino_form = InquilinoForm(request.POST)

        contrato_form = ContratoAlquilerForm(
            request.POST,
            propiedad_id=propiedad_id
        )

        aval_form = AvalContratoForm(
            request.POST,
            prefix="aval"
        )

        contrato_valido = (
            inquilino_form.is_valid()
            and contrato_form.is_valid()
        )

        aval_valido = True

        if tiene_aval:
            aval_valido = aval_form.is_valid()

        if contrato_valido and aval_valido:

            with transaction.atomic():
                inquilino = inquilino_form.save()

                contrato = contrato_form.save(commit=False)
                contrato.inquilino = inquilino
                contrato.save()

                if tiene_aval:
                    aval = aval_form.save(commit=False)
                    aval.contrato = contrato
                    aval.save()

            return redirect(
                "hotel:contrato_pdf",
                contrato_id=contrato.id
            )

        context = {
            "inquilino_form": inquilino_form,
            "contrato_form": contrato_form,
            "aval_form": aval_form,
            "propiedades": Flat.objects.all(),
            "propiedad_id": propiedad_id,
            "tiene_aval": tiene_aval,
        }

        return render(request, self.template_name, context)


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


def contacto(requets):

    return render(requets, 'contacto.html')


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


class CrearProcesoFormalizacionView(LoginRequiredMixin, View):
    """
    Permite que el personal introduzca los datos del futuro inquilino
    y las condiciones económicas.

    Crea Inquilino y ProcesoFormalizacion, pero no ContratoAlquiler.
    """

    template_name = "hotel/crear_proceso_formalizacion.html"

    def obtener_habitacion(self, request, habitacion_id):
        habitacion = get_object_or_404(
            Habitacion,
            pk=habitacion_id,
        )

        if habitacion.contrato_activo:
            messages.error(
                request,
                "Primero debes finalizar el contrato activo de esta habitación.",
            )
            return None

        if habitacion.proceso_formalizacion_activo:
            messages.info(
                request,
                "Esta habitación ya tiene un proceso de formalización activo.",
            )
            return None

        return habitacion

    def get(self, request, habitacion_id):
        habitacion = self.obtener_habitacion(
            request,
            habitacion_id,
        )

        if habitacion is None:
            return redirect("hotel:habitaciones_dashboard")

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

        return render(
            request,
            self.template_name,
            {
                "habitacion": habitacion,
                "inquilino_form": inquilino_form,
                "proceso_form": proceso_form,
            },
        )

    @transaction.atomic
    def post(self, request, habitacion_id):
        habitacion = self.obtener_habitacion(
            request,
            habitacion_id,
        )

        if habitacion is None:
            return redirect("hotel:habitaciones_dashboard")

        inquilino_form = InquilinoForm(
            request.POST,
            prefix="inquilino",
        )

        proceso_form = CrearProcesoFormalizacionForm(
            request.POST,
            prefix="proceso",
        )

        inquilino_valido = inquilino_form.is_valid()
        proceso_valido = proceso_form.is_valid()

        if not (inquilino_valido and proceso_valido):
            messages.error(
                request,
                "Oye, faltan datos o hay algún campo incorrecto. "
                "Revisa los campos señalados.",
            )

            return render(
                request,
                self.template_name,
                {
                    "habitacion": habitacion,
                    "inquilino_form": inquilino_form,
                    "proceso_form": proceso_form,
                },
            )

        inquilino = inquilino_form.save()

        proceso = proceso_form.save(commit=False)
        proceso.habitacion = habitacion
        proceso.inquilino = inquilino
        proceso.estado = ProcesoFormalizacion.Estado.PENDIENTE

        # El enlace inicial permanece disponible durante siete días.
        proceso.fecha_limite = (
            timezone.now() + timedelta(days=7)
        )

        if (
            proceso.tipo_primera_renta
            == ProcesoFormalizacion.TipoPrimeraRenta.MES_COMPLETO
        ):
            proceso.importe_primera_renta = (
                proceso.precio_mensual
            )
        else:
            proceso.importe_primera_renta = (
                calcular_renta_proporcional(
                    precio_mensual=proceso.precio_mensual,
                    fecha_inicio=proceso.fecha_inicio_contrato,
                )
            )

        proceso.save()

        messages.success(
            request,
            "Proceso creado. Ya puedes enviar el enlace "
            "al futuro inquilino.",
        )

        return redirect(
            "hotel:detalle_proceso_formalizacion",
            pk=proceso.pk,
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


class ConfirmarFormalizacionView(
    LoginRequiredMixin,
    View,
):
    """
    Confirma la recepción del documento firmado y los pagos.

    El ContratoAlquiler se crea por primera vez cuando el proceso
    queda formalizado.
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
                "Este proceso ya no puede formalizarse.",
            )
            return redirect(
                "hotel:detalle_proceso_formalizacion",
                pk=proceso.pk,
            )

        if proceso.contrato_id:
            messages.info(
                request,
                "Este proceso ya tiene un contrato asociado.",
            )
            return redirect(
                "hotel:detalle_proceso_formalizacion",
                pk=proceso.pk,
            )

        if proceso.inquilino is None:
            messages.error(
                request,
                "El proceso no tiene un inquilino asociado.",
            )
            return redirect(
                "hotel:detalle_proceso_formalizacion",
                pk=proceso.pk,
            )

        if proceso.habitacion is None:
            messages.error(
                request,
                "El proceso no tiene una habitación asociada.",
            )
            return redirect(
                "hotel:detalle_proceso_formalizacion",
                pk=proceso.pk,
            )

        if proceso.habitacion.contrato_activo:
            messages.error(
                request,
                "La habitación ya tiene otro contrato activo.",
            )
            return redirect(
                "hotel:detalle_proceso_formalizacion",
                pk=proceso.pk,
            )

        if not proceso.fecha_inicio_contrato:
            messages.error(
                request,
                "El proceso no tiene una fecha de inicio.",
            )
            return redirect(
                "hotel:detalle_proceso_formalizacion",
                pk=proceso.pk,
            )

        if not proceso.duracion_meses:
            messages.error(
                request,
                "El proceso no tiene una duración válida.",
            )
            return redirect(
                "hotel:detalle_proceso_formalizacion",
                pk=proceso.pk,
            )

        if proceso.precio_mensual is None:
            messages.error(
                request,
                "El proceso no tiene un precio mensual.",
            )
            return redirect(
                "hotel:detalle_proceso_formalizacion",
                pk=proceso.pk,
            )

        if proceso.fianza is None:
            messages.error(
                request,
                "El proceso no tiene una fianza definida.",
            )
            return redirect(
                "hotel:detalle_proceso_formalizacion",
                pk=proceso.pk,
            )

        fecha_fin = (
            proceso.fecha_inicio_contrato
            + relativedelta(months=proceso.duracion_meses)
            - timedelta(days=1)
        )

        contrato = ContratoAlquiler.objects.create(
            inquilino=proceso.inquilino,
            habitacion=proceso.habitacion,
            fecha_inicio=proceso.fecha_inicio_contrato,
            fecha_fin=fecha_fin,
            precio_mensual=proceso.precio_mensual,
            fianza=proceso.fianza,
            activo=True,
        )

        ahora = timezone.now()

        proceso.contrato = contrato
        proceso.contrato_firmado_recibido = True
        proceso.fecha_contrato_firmado = ahora
        proceso.fianza_recibida = True
        proceso.renta_recibida = True
        proceso.estado = ProcesoFormalizacion.Estado.FORMALIZADO
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
            "Proceso formalizado y contrato creado correctamente.",
        )

        return redirect("hotel:habitaciones_dashboard")

class DescargarContratoFormalizacionView(View):

    def get(self, request, token):

        proceso = get_object_or_404(
            ProcesoFormalizacion.objects.select_related(
                "habitacion",
                "habitacion__propiedad",
                "inquilino",
            ),
            token=token,
        )

        proceso.actualizar_estado()
        proceso.refresh_from_db()

        if proceso.estado not in {
            ProcesoFormalizacion.Estado.PENDIENTE,
            ProcesoFormalizacion.Estado.INICIADO,
        }:
            messages.error(
                request,
                "Este documento ya no está disponible.",
            )
            return redirect(
                "hotel:formalizacion_publica",
                token=proceso.token,
            )
        fecha_fin = (
                proceso.fecha_inicio_contrato
                + relativedelta(months=proceso.duracion_meses)
                - timedelta(days=1)
        )

        contrato_provisional = ContratoAlquiler(
            habitacion=proceso.habitacion,
            inquilino=proceso.inquilino,
            fecha_inicio=proceso.fecha_inicio_contrato,
            precio_mensual=proceso.precio_mensual,
            fecha_fin=fecha_fin,
            activo=False,
        )

        # Adapta estos nombres a los campos reales de ContratoAlquiler.
        if hasattr(contrato_provisional, "duracion_meses"):
            contrato_provisional.duracion_meses = proceso.duracion_meses

        if hasattr(contrato_provisional, "fianza"):
            contrato_provisional.fianza = proceso.fianza

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="formalizacion_'
            f'{proceso.habitacion.nombre}.pdf"'
        )

        response = generar_contrato_pdf(
            request,
            response,
            contrato_provisional,
        )

        if not proceso.contrato_descargado:
            proceso.contrato_descargado = True
            proceso.fecha_descarga = timezone.now()

            if proceso.estado == ProcesoFormalizacion.Estado.PENDIENTE:
                proceso.estado = ProcesoFormalizacion.Estado.INICIADO
                proceso.fecha_inicio = timezone.now()
                proceso.fecha_limite = (
                    timezone.now() + timedelta(hours=24)
                )

            proceso.save(
                update_fields=[
                    "contrato_descargado",
                    "fecha_descarga",
                    "estado",
                    "fecha_inicio",
                    "fecha_limite",
                ]
            )

        return response

class FormalizacionPublicaView(View):

    template_name = "hotel/formalizacion_publica.html"

    def get(self, request, token):

        proceso = get_object_or_404(
            ProcesoFormalizacion.objects.select_related(
                "habitacion",
                "habitacion__propiedad",
                "inquilino",
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
                "hotel/formalizacion_no_disponible.html",
                {"proceso": proceso},
                status=410,
            )

        return render(
            request,
            self.template_name,
            {"proceso": proceso},
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