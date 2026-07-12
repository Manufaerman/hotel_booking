import textwrap

from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import Flat, Habitacion, ContratoAlquiler, Inquilino, Gasto
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import View
from .forms import InquilinoForm, ContratoAlquilerForm
from datetime import date
from django.shortcuts import render
from .models import Visit
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.utils import timezone
from django.views.generic import TemplateView

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
    return render(request, 'contratos.html', {'contratos':contratos})


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
    dia = date.today()
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    margen_x = 70
    margen_y = 70
    ancho_texto = width-(margen_x*2)
    y = height - margen_y
    p.setFont("Helvetica-Bold", 16)
    p.drawString(margen_x, y, "CONTRATO DE ARRENDAMIENTO DE HABITACION")
    y -= 40
    p.setFont("Helvetica", 11)
    texto = f"""
En Madrid, a {dia.strftime("%d/%m/%Y")}.\n\n
REUNIDOS
De una parte,
Don Manuel Acosta Faerman, mayor de edad, de nacionalidad Española, con domicilio en C/Lorca 1 y DNI nº 06002387-P, actuando en su propio nombre y en representación de MACRABBIT, S.L.U. (en adelante, el “Propietario”).\n
Y de otra parte,
Doña {contrato.inquilino.nombre}, mayor de edad, de nacionalidad {contrato.inquilino.nacionalidad}, con domicilio en {contrato.inquilino.direccion} y DNI nº {contrato.inquilino.dni}, cuya fotocopia queda incorporada como Anexo al presente Contrato. Actúa en su propio nombre y representación (en adelante, el “Inquilino”).\n
El Propietario y el Inquilino serán denominados conjuntamente como las “Partes”.
Ambas partes, reconociéndose mutuamente capacidad legal suficiente para contratar y obligarse, acuerdan formalizar el presente CONTRATO DE ARRENDAMIENTO DE HABITACIÓN.\n
EXPONEN
1º.- Que el Propietario es titular de la vivienda amueblada sita en Madrid, calle {contrato.habitacion.propiedad}, {contrato.habitacion.propiedad.descripcion_contrato}.
El Propietario manifiesta expresamente que tanto el inmueble como la habitación objeto de arrendamiento, identificada con el número {contrato.habitacion.nombre}, reúnen las condiciones necesarias de habitabilidad, uso y conservación para satisfacer las necesidades de alojamiento del Inquilino.
En adelante, la habitación objeto del arrendamiento será denominada la “Habitación” y, conjuntamente con las zonas comunes y demás dependencias de la vivienda, el “Inmueble”.\n
2º.- Que el Inquilino manifiesta su interés en tomar en arrendamiento la Habitación anteriormente descrita, así como el uso compartido de las zonas comunes del Inmueble, destinándolo exclusivamente a su alojamiento habitual.\n
3º.- Que ambas partes, reconociéndose mutuamente plena capacidad legal para contratar, acuerdan formalizar el presente CONTRATO DE ARRENDAMIENTO DE HABITACIÓN (el “Contrato”), que se regirá por lo dispuesto en los artículos 1.542 a 1.582 del Código Civil, así como por las demás disposiciones aplicables, con sujeción a las siguientes:\n
CLÁUSULAS\n
PRIMERA: OBJETO
1.1 El Propietario arrienda al Inquilino, que acepta en este acto, la Habitación junto con las zonas comunes del Inmueble descritas en el Expositivo 1º.
1.2 El Inquilino se compromete a usar dicha Habitación y las zonas comunes exclusivamente como vivienda habitual.
1.3 Queda estrictamente prohibido:
Cualquier uso distinto al descrito anteriormente.
El subarrendamiento total o parcial.
La cesión del Contrato sin consentimiento previo y por escrito del Propietario.
El uso del Inmueble para actividades comerciales, industriales, oficina o despacho profesional.
Destinar la Habitación al hospedaje de carácter vacacional.
El incumplimiento de esta obligación facultará al Propietario para resolver el presente Contrato.
1.4 Por las dimensiones de la Habitación, únicamente el Inquilino podrá ocuparla, no siendo de uso compartido.
1.5 El Inquilino se obliga a no molestar ni perjudicar la convivencia pacífica del resto de ocupantes y vecinos.
1.6 El Inquilino se compromete a respetar las normas de convivencia y buena conducta en las zonas comunes.
1.7 Se prohíbe expresamente la tenencia de animales domésticos en el Inmueble salvo autorización previa y por escrito del Propietario.
1.8 Queda prohibido fumar en la Habitación y en cualquier zona interior del Inmueble. Esta prohibición incluye cigarrillos, vapeadores, cigarrillos electrónicos y dispositivos similares. En caso de incumplimiento, el Inquilino asumirá los costes de limpieza y desodorización correspondientes.
El incumplimiento de cualquiera de las obligaciones anteriores podrá constituir causa suficiente de resolución contractual.\n
SEGUNDA: PLAZO DE VIGENCIA
2.1 El Contrato entrará en vigor en fecha {contrato.fecha_inicio.strftime("%d/%m/%Y")}, con una duración inicial obligatoria de seis (6) meses.
2.2 Transcurrido dicho plazo mínimo —o cualquiera de sus prórrogas sucesivas de tres (3) meses— cualquiera de las Partes podrá desistir del Contrato notificándolo por escrito con al menos treinta (30) días de antelación.\n
TERCERA: DERECHO DE ACCESO DEL PROPIETARIO
El Inquilino se compromete a permitir el acceso del Propietario a las zonas comunes del Inmueble y a la Habitación objeto del presente Contrato, previa notificación razonable, salvo casos de urgencia o emergencia.
El incumplimiento de esta obligación podrá facultar al Propietario para resolver el Contrato y reclamar los daños y perjuicios ocasionados.\n
CUARTA: ENTREGA DE LA HABITACIÓN
4.1 El Propietario entrega la Habitación y el Inmueble en adecuadas condiciones de habitabilidad, conservación y funcionamiento, a satisfacción del Inquilino.
La Habitación se entrega amueblada y el Inmueble dispone de cocina equipada.
4.2 En este acto se entrega al Inquilino un juego completo de llaves de acceso a la Habitación y al Inmueble.\n
QUINTA: RENTA
5.1 Ambas Partes acuerdan una renta mensual de {contrato.precio_mensual} €.
La renta incluye los gastos de agua, luz, gas e internet hasta un máximo conjunto de 200 € mensuales, cuya gestión corresponderá al Propietario.
5.2 La falta de pago de una mensualidad facultará al Propietario para resolver el Contrato y ejercitar las acciones legales correspondientes.
5.3 La renta se devengará desde la fecha de entrada en vigor del presente Contrato.
El Inquilino entrega en este acto el importe correspondiente a los días pendientes del mes en curso, sirviendo el presente documento como recibo de pago.
5.4 El pago de la renta se realizará por mensualidades anticipadas dentro de los cinco (5) primeros días laborables de cada mes mediante transferencia bancaria a la siguiente cuenta:
Titular: MACRABBIT, S.L.U.
Entidad: BANKINTER
IBAN: ES92 0128 0068 1301 0003 3162\n
SEXTA: GARANTÍA
6.1 El Inquilino entrega al Propietario la cantidad de {contrato.fianza} €, en concepto de garantía contractual, que el Propietario declara recibir en este acto.
6.2 La garantía responderá de posibles daños, desperfectos, impagos o incumplimientos contractuales imputables al Inquilino.
La devolución de dicha garantía se efectuará en el plazo máximo de una semana desde la finalización del Contrato, previa comprobación del estado de la Habitación y del Inmueble.
SÉPTIMA: SERVICIOS Y GASTOS
7.1 El Propietario asumirá los gastos ordinarios de suministros del Inmueble (agua, luz, gas e internet) hasta un máximo conjunto de 200 € mensuales.
Una vez superado dicho importe, el exceso será repercutido entre los inquilinos de la siguiente forma:
Habitacion  doble con aire acondicionado: 40%
Habitación doble: 35%
Habitación individual: 25%
En caso de que todas las habitaciones sean dobles, el exceso se dividirá en partes iguales.
7.2 Los suministros permanecerán a nombre del Propietario.
7.3 Los gastos de comunidad e IBI serán íntegramente asumidos por el Propietario.
7.4 Las tasas municipales correspondientes serán igualmente asumidas por el Propietario.
7.5 El Propietario no será responsable de interrupciones de suministros ajenas a su voluntad.\n
OCTAVA: GASTOS DE REPARACIÓN Y CONSERVACIÓN
8.1 El Propietario realizará las reparaciones necesarias para conservar el Inmueble en condiciones de habitabilidad, salvo aquellas derivadas de daños causados por negligencia, mal uso o culpa del Inquilino.
El Inquilino será responsable de los daños ocasionados por él mismo o sus invitados.
8.2 El Inquilino deberá permitir las reparaciones urgentes que no puedan demorarse hasta la finalización del Contrato.
8.3 Queda prohibido el uso de estufas eléctricas o aparatos de aire acondicionado no proporcionados por el Propietario. En caso de incumplimiento, el Propietario podrá requerir su retirada inmediata y, en caso de persistencia, resolver el Contrato.\n
NOVENA: OBRAS
9.1 El Inquilino no podrá realizar obras, instalaciones ni modificaciones sin autorización previa y escrita del Propietario.
Especialmente queda prohibido:
a) Instalar aparatos adheridos a paredes o estructuras.
b) Realizar perforaciones o alteraciones en paredes, azulejos o suelos.
c) Colocación de cerrojos o cerraduras no suministradas por la propiedad.
9.2 El incumplimiento facultará al Propietario para resolver el Contrato y exigir la reposición al estado original.\n
DÉCIMA: DEVOLUCIÓN DE LA HABITACIÓN
10.1 Finalizado el Contrato, el Inquilino deberá abandonar la Habitación y el Inmueble sin necesidad de requerimiento previo.
10.2 La Habitación deberá devolverse en buen estado de conservación, libre de objetos personales y completamente desocupada.
10.3 El Inquilino se obliga a reparar cualquier desperfecto causado durante la vigencia del Contrato.
10.4 El retraso en la entrega devengará una penalización equivalente al doble de la renta diaria vigente por cada día de demora, sin perjuicio de las acciones legales correspondientes.\n

DECIMOPRIMERA: DERECHO DE TANTEO Y RETRACTO
El Inquilino renuncia expresamente a los derechos de tanteo y retracto que pudieran corresponderle.\n
DECIMOSEGUNDA: CAUSAS DE TERMINACIÓN
Serán causas de resolución del Contrato, además de las previstas legalmente:
a) El impago de renta o cantidades asumidas por el Inquilino.
b) La falta de entrega de la garantía pactada.
c) La realización de daños u obras no autorizadas.
d) Actividades molestas, peligrosas, ilícitas o insalubres.
e) El subarrendamiento no autorizado.
f) El incumplimiento de cualquiera de las obligaciones contractuales.\n

DECIMOTERCERA: PROTECCIÓN DE DATOS
13.1 Los datos personales facilitados serán tratados por el Propietario con la finalidad de gestionar la relación contractual conforme a la normativa vigente.
El Inquilino podrá ejercitar sus derechos de acceso, rectificación, supresión, limitación y portabilidad dirigiéndose al Propietario.
13.2 En caso de impago, los datos podrán comunicarse a ficheros de solvencia patrimonial conforme a la legislación aplicable.\n
DECIMOCUARTA: LEY APLICABLE Y JURISDICCIÓN
14.1 El presente Contrato se regirá por el Código Civil y demás normativa aplicable.
14.2 Las Partes se someten a los juzgados y tribunales del lugar donde radique el Inmueble.\n
DECIMOQUINTA: NOTIFICACIONES
15.1 Toda comunicación relacionada con el presente Contrato deberá realizarse por escrito mediante correo postal, correo electrónico, SMS o cualquier otro medio que permita acreditar su envío y recepción.
15.2 A efectos de notificaciones, las Partes designan:\n
Por el Inquilino:
Email: {contrato.inquilino.email}
Teléfono: +34 {contrato.inquilino.telefono}
Por el Propietario:
Email: office@bycoleccion.com
Teléfono: +34 639 44 61 42\n
DECIMOSEXTA: MOBILIARIO DE LA HABITACIÓN
La habitación se entrega al arrendatario amueblada, con el mobiliario, enseres y elementos detallados en el inventario adjunto al presente contrato.
Todos los muebles, electrodomésticos, accesorios y demás elementos entregados deberán permanecer en todo momento dentro de la habitación asignada durante la vigencia del contrato. El arrendatario no podrá retirarlos, trasladarlos, depositarlos, almacenarlos ni abandonarlos en zonas comunes, otras habitaciones, pasillos, trasteros, garajes o cualquier otra parte del inmueble o edificio, sin autorización previa y expresa del arrendador.
Al finalizar el contrato, la totalidad del mobiliario y elementos inventariados deberá encontrarse dentro de la habitación, en el mismo lugar y estado de conservación en que fue entregada, salvo el desgaste normal derivado de un uso adecuado. Cualquier falta, deterioro, traslado no autorizado o reposición necesaria será asumida económicamente por el arrendatario.

INVENTARIO:
Cama de dos plazas con colchon y cabecero.
Television con SMART TV de 32"
Armario de 100 cm de ancho por 200 cm.
Armario de 50 cm por 200 cm.
Mesita de luz vintage verde
mesita de luz de bambu y cristal

DECIMOSÈPTIMA: FIRMA DEL CONTRATO
Las Partes aceptan el presente Contrato y sus anexos, comprometiéndose a cumplirlo de buena fe.

EL PROPIETARIO
MACRABBIT, S.L.U.\n\n\n
Representada por Manuel Acosta Faerman

EL INQUILINO\n\n\n
{contrato.inquilino.nombre}

Listado de anexos:
Anexo I – Documento de identificación.

"""

    p.setFont("Helvetica", 11)

    lineas_finales = []

    for parrafo in texto.split("\n"):

        wrapped = textwrap.wrap(parrafo, width=95)

        if not wrapped:

            lineas_finales.append("")

        else:

            lineas_finales.extend(wrapped)

    for linea in lineas_finales:

        if y < margen_y:
            p.showPage()

            p.setFont("Helvetica", 11)

            y = height - margen_y

        p.drawString(margen_x, y, linea)

        y -= 18

    p.save()

    return response


def contacto(requets):

    return render(requets, 'contacto.html')



