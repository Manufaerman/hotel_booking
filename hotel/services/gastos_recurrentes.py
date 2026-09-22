import calendar
from datetime import date

from dateutil.relativedelta import relativedelta
from django.db import transaction
from django.utils import timezone

from hotel.models import Gasto, GastoRecurrente


def fecha_segura(anio, mes, dia):
    ultimo_dia = calendar.monthrange(anio, mes)[1]

    return date(
        anio,
        mes,
        min(dia, ultimo_dia),
    )


def frecuencia_en_meses(frecuencia):
    frecuencias = {
        "mensual": 1,
        "trimestral": 3,
        "semestral": 6,
        "anual": 12,
    }

    return frecuencias[frecuencia]


def generar_gastos_recurrentes(hasta=None):
    if hasta is None:
        hasta = timezone.localdate()

    recurrentes = (
        GastoRecurrente.objects
        .filter(
            activo=True,
            fecha_inicio__lte=hasta,
        )
        .select_related(
            "propiedad",
            "habitacion",
        )
    )

    creados = []

    for recurrente in recurrentes:
        creados.extend(
            generar_gastos_de_recurrente(
                recurrente,
                hasta,
            )
        )

    return creados


@transaction.atomic
def generar_gastos_de_recurrente(
    recurrente,
    hasta=None,
):
    if hasta is None:
        hasta = timezone.localdate()

    if not recurrente.activo:
        return []

    if recurrente.fecha_inicio > hasta:
        return []

    fecha_limite = hasta

    if (
        recurrente.fecha_fin
        and recurrente.fecha_fin < fecha_limite
    ):
        fecha_limite = recurrente.fecha_fin

    primera_fecha = obtener_primera_fecha(
        recurrente
    )

    intervalo = frecuencia_en_meses(
        recurrente.frecuencia
    )

    if intervalo <= 0:
        raise ValueError(
            "La frecuencia debe producir "
            "un intervalo superior a cero."
        )

    fecha_programada = primera_fecha
    creados = []

    while fecha_programada <= fecha_limite:
        periodo = fecha_programada.replace(
            day=1
        )

        moneda = (
            "EUR"
            if recurrente.pais == "ES"
            else "ARS"
        )

        gasto, creado = (
            Gasto.objects.get_or_create(
                gasto_recurrente=recurrente,
                periodo_recurrente=periodo,
                defaults={
                    "pais": recurrente.pais,
                    "moneda": moneda,
                    "ambito": recurrente.ambito,
                    "propiedad": recurrente.propiedad,
                    "habitacion": recurrente.habitacion,
                    "proyecto": recurrente.proyecto,
                    "tipo": "recurrente",
                    "concepto": (
                        recurrente.concepto
                        or recurrente.nombre
                    ),
                    "categoria": (
                        recurrente.categoria
                    ),
                    "tipo_suministro": (
                        recurrente.tipo_suministro
                    ),
                    "importe": recurrente.importe,
                    "fecha": fecha_programada,
                    "pagado": (
                        recurrente.pagado_por_defecto
                    ),
                    "proveedor": (
                        recurrente.proveedor
                    ),
                    "requiere_justificante": (
                        recurrente
                        .requiere_justificante
                    ),
                    "destino_gestoria": (
                        recurrente
                        .destino_gestoria
                    ),
                    "notas": recurrente.notas,
                    "generado_automaticamente": True,
                },
            )
        )

        if creado:
            creados.append(gasto)

        siguiente_fecha = (
            fecha_programada
            + relativedelta(
                months=intervalo,
            )
        )

        fecha_programada = fecha_segura(
            siguiente_fecha.year,
            siguiente_fecha.month,
            recurrente.dia_generacion,
        )

    return creados


def obtener_primera_fecha(recurrente):
    inicio = recurrente.fecha_inicio

    if recurrente.frecuencia == "anual":
        mes = (
            recurrente.mes_generacion
            or inicio.month
        )

        primera_fecha = fecha_segura(
            inicio.year,
            mes,
            recurrente.dia_generacion,
        )

        if primera_fecha < inicio:
            primera_fecha = fecha_segura(
                inicio.year + 1,
                mes,
                recurrente.dia_generacion,
            )

        return primera_fecha

    primera_fecha = fecha_segura(
        inicio.year,
        inicio.month,
        recurrente.dia_generacion,
    )

    if primera_fecha < inicio:
        primera_fecha = (
            primera_fecha
            + relativedelta(
                months=frecuencia_en_meses(
                    recurrente.frecuencia
                )
            )
        )

        primera_fecha = fecha_segura(
            primera_fecha.year,
            primera_fecha.month,
            recurrente.dia_generacion,
        )

    return primera_fecha