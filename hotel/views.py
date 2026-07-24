from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.http import JsonResponse
from .models import Flat, Habitacion, ContratoAlquiler, Inquilino, Gasto
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import View
from .forms import InquilinoForm, ContratoAlquilerForm
from datetime import date
from django.shortcuts import render
from .models import Visit
from django.http import HttpResponse
from django.utils import timezone
from .services.contrato_pdf import generar_contrato_pdf


def finalizar_contrato(request, id):
    contrato = get_object_or_404(ContratoAlquiler, id=id)
    if request.method == 'POST':
        contrato.finalizar()
        messages.success(request, 'Contrato finalizado correctamente')

    return redirect('hotel:contratos')


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
    template_name = 'newcontract.html'

    def get(self, request):
        propiedad_id = request.GET.get('propiedad')

        context = {
            'inquilino_form': InquilinoForm(),
            'contrato_form': ContratoAlquilerForm(propiedad_id=propiedad_id),
            'propiedades': Flat.objects.all(),
            'propiedad_id': propiedad_id,
        }

        return render(request, self.template_name, context)

    def post(self, request):
        propiedad_id = request.POST.get('propiedad')

        inquilino_form = InquilinoForm(request.POST)
        contrato_form = ContratoAlquilerForm(
            request.POST,
            propiedad_id=propiedad_id
        )

        if inquilino_form.is_valid() and contrato_form.is_valid():
            inquilino = inquilino_form.save()

            contrato = contrato_form.save(commit=False)
            contrato.inquilino = inquilino
            contrato.save()

            return redirect('hotel:contrato_pdf', contrato_id=contrato.id)

        context = {
            'inquilino_form': inquilino_form,
            'contrato_form': contrato_form,
            'propiedades': Flat.objects.all(),
            'propiedad_id': propiedad_id,
        }

        return render(request, self.template_name, context)


def contrato_pdf(request, contrato_id):
    contrato = ContratoAlquiler.objects.get(id=contrato_id)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="contrato_{contrato.id}.pdf'

    return generar_contrato_pdf(request, response, contrato)


def contacto(requets):

    return render(requets, 'contacto.html')



