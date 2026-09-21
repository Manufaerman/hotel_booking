import re
from django.contrib.auth.models import User
from hotel.models import Inquilino, ContratoAlquiler, Flat, Habitacion, AvalContrato, Proyecto,IngresoPropiedad
from user_profile.models import UserProfile
from .models import ProcesoFormalizacion
from decimal import Decimal
from django.utils import timezone
from django import forms
from .models import (
    Gasto,
    GastoRecurrente,

)
class EditarGastoRecurrenteForm(
    forms.ModelForm,
):
    class Meta:
        model = GastoRecurrente

        fields = [
            "nombre",
            "pais",
            "ambito",
            "propiedad",
            "habitacion",
            "proyecto",
            "categoria",
            "tipo_suministro",
            "importe",
            "proveedor",
            "concepto",
            "frecuencia",
            "dia_generacion",
            "mes_generacion",
            "fecha_inicio",
            "fecha_fin",
            "pagado_por_defecto",
            "requiere_justificante",
            "destino_gestoria",
            "activo",
            "notas",
        ]

        labels = {
            "nombre": "Nombre del gasto fijo",
            "pais": "País",
            "ambito": "¿A qué corresponde?",
            "propiedad": "Propiedad",
            "habitacion": "Habitación",
            "proyecto": "Proyecto",
            "categoria": "Categoría",
            "tipo_suministro": "Tipo de suministro",
            "importe": "Importe habitual",
            "proveedor": "Proveedor",
            "concepto": "Concepto",
            "frecuencia": "Frecuencia",
            "dia_generacion": "Día de generación",
            "mes_generacion": "Mes de generación",
            "fecha_inicio": "Fecha de inicio",
            "fecha_fin": "Fecha de finalización",
            "pagado_por_defecto": "Pagado por defecto",
            "requiere_justificante": "Requiere factura",
            "destino_gestoria": "Destino contable",
            "activo": "Generación activa",
            "notas": "Notas",
        }

        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "class": "gastos-control",
                },
            ),
            "pais": forms.Select(
                attrs={
                    "class": "gastos-control",
                },
            ),
            "ambito": forms.Select(
                attrs={
                    "class": "gastos-control",
                },
            ),
            "propiedad": forms.Select(
                attrs={
                    "class": "gastos-control",
                },
            ),
            "habitacion": forms.Select(
                attrs={
                    "class": "gastos-control",
                },
            ),
            "proyecto": forms.Select(
                attrs={
                    "class": "gastos-control",
                },
            ),
            "categoria": forms.Select(
                attrs={
                    "class": "gastos-control",
                },
            ),
            "tipo_suministro": forms.Select(
                attrs={
                    "class": "gastos-control",
                },
            ),
            "importe": forms.NumberInput(
                attrs={
                    "class": "gastos-control",
                    "min": "0.01",
                    "step": "0.01",
                    "inputmode": "decimal",
                },
            ),
            "proveedor": forms.TextInput(
                attrs={
                    "class": "gastos-control",
                },
            ),
            "concepto": forms.TextInput(
                attrs={
                    "class": "gastos-control",
                },
            ),
            "frecuencia": forms.Select(
                attrs={
                    "class": "gastos-control",
                },
            ),
            "dia_generacion": forms.NumberInput(
                attrs={
                    "class": "gastos-control",
                    "min": "1",
                    "max": "31",
                },
            ),
            "mes_generacion": forms.NumberInput(
                attrs={
                    "class": "gastos-control",
                    "min": "1",
                    "max": "12",
                },
            ),
            "fecha_inicio": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "class": "gastos-control",
                    "type": "date",
                },
            ),
            "fecha_fin": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "class": "gastos-control",
                    "type": "date",
                },
            ),
            "pagado_por_defecto": forms.CheckboxInput(
                attrs={
                    "class": "gastos-checkbox",
                },
            ),
            "requiere_justificante": forms.CheckboxInput(
                attrs={
                    "class": "gastos-checkbox",
                },
            ),
            "destino_gestoria": forms.Select(
                attrs={
                    "class": "gastos-control",
                },
            ),
            "activo": forms.CheckboxInput(
                attrs={
                    "class": "gastos-checkbox",
                },
            ),
            "notas": forms.Textarea(
                attrs={
                    "class": "gastos-control gastos-textarea",
                    "rows": 3,
                },
            ),
        }

class GastoForm(forms.ModelForm):

    FRECUENCIAS = [
        ("mensual", "Mensual"),
        ("bimestral", "Cada dos meses"),
        ("trimestral", "Cada tres meses"),
        ("semestral", "Cada seis meses"),
        ("anual", "Anual"),
    ]

    MESES = [
        (1, "Enero"),
        (2, "Febrero"),
        (3, "Marzo"),
        (4, "Abril"),
        (5, "Mayo"),
        (6, "Junio"),
        (7, "Julio"),
        (8, "Agosto"),
        (9, "Septiembre"),
        (10, "Octubre"),
        (11, "Noviembre"),
        (12, "Diciembre"),
    ]

    es_recurrente = forms.BooleanField(
        required=False,
        label="Repetir este gasto automáticamente",
        widget=forms.CheckboxInput(
            attrs={
                "class": "gastos-checkbox",
            },
        ),
    )

    frecuencia = forms.ChoiceField(
        required=False,
        choices=FRECUENCIAS,
        initial="mensual",
        label="Frecuencia",
        widget=forms.Select(
            attrs={
                "class": "gastos-control",
            },
        ),
    )

    dia_generacion = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=31,
        initial=1,
        label="Día previsto",
        help_text=(
            "Día del mes en el que debe generarse."
        ),
        widget=forms.NumberInput(
            attrs={
                "class": "gastos-control",
                "min": "1",
                "max": "31",
                "inputmode": "numeric",
            },
        ),
    )

    mes_generacion = forms.TypedChoiceField(
        required=False,
        choices=MESES,
        coerce=int,
        empty_value=None,
        label="Mes de generación",
        widget=forms.Select(
            attrs={
                "class": "gastos-control",
            },
        ),
    )

    fecha_inicio = forms.DateField(
        required=False,
        label="Fecha de inicio",
        input_formats=[
            "%Y-%m-%d",
        ],
        widget=forms.DateInput(
            format="%Y-%m-%d",
            attrs={
                "class": "gastos-control",
                "type": "date",
            },
        ),
    )

    fecha_fin = forms.DateField(
        required=False,
        label="Fecha de finalización",
        input_formats=[
            "%Y-%m-%d",
        ],
        widget=forms.DateInput(
            format="%Y-%m-%d",
            attrs={
                "class": "gastos-control",
                "type": "date",
            },
        ),
    )

    requiere_justificante = forms.BooleanField(
        required=False,
        initial=True,
        label="Recordarme subir la factura",
        widget=forms.CheckboxInput(
            attrs={
                "class": "gastos-checkbox",
            },
        ),
    )

    class Meta:

        model = Gasto

        fields = [
            "pais",
            "ambito",
            "propiedad",
            "habitacion",
            "proyecto",
            "categoria",
            "tipo_suministro",
            "consumo",
            "unidad_consumo",
            "proveedor",
            "concepto",
            "importe",
            "fecha",
            "cotizacion_usd",
            "pagado",
            "destino_gestoria",
            "justificante",
            "notas",
        ]

        labels = {
            "pais": "País",
            "ambito": "Destino",
            "propiedad": "Propiedad",
            "habitacion": "Habitación",
            "proyecto": "Proyecto",
            "categoria": "Categoría",
            "tipo_suministro": "Tipo de suministro",
            "consumo": "Consumo",
            "unidad_consumo": "Unidad",
            "proveedor": "Proveedor",
            "concepto": "Concepto",
            "importe": "Importe",
            "fecha": "Fecha",
            "cotizacion_usd": (
                "Dólar blue venta"
            ),
            "pagado": "El gasto ya está pagado",
            "destino_gestoria": (
                "¿Debe enviarse a la gestoría?"
            ),
            "justificante": (
                "Factura o justificante"
            ),
            "notas": "Notas",
        }

        widgets = {
            "pais": forms.RadioSelect(
                attrs={
                    "class": "gastos-country-radio",
                },
            ),
            "ambito": forms.RadioSelect(
                attrs={
                    "class": "gastos-scope-radio",
                },
            ),
            "propiedad": forms.Select(
                attrs={
                    "class": "gastos-control",
                },
            ),
            "habitacion": forms.Select(
                attrs={
                    "class": "gastos-control",
                },
            ),
            "proyecto": forms.Select(
                attrs={
                    "class": "gastos-control",
                },
            ),
            "categoria": forms.Select(
                attrs={
                    "class": "gastos-control",
                },
            ),
            "tipo_suministro": forms.Select(
                attrs={
                    "class": "gastos-control",
                },
            ),
            "consumo": forms.NumberInput(
                attrs={
                    "class": "gastos-control",
                    "min": "0.01",
                    "step": "0.01",
                    "inputmode": "decimal",
                    "placeholder": "Ej. 350",
                },
            ),
            "unidad_consumo": forms.Select(
                attrs={
                    "class": "gastos-control",
                },
            ),
            "proveedor": forms.TextInput(
                attrs={
                    "class": "gastos-control",
                    "placeholder": (
                        "Nombre del proveedor"
                    ),
                    "autocomplete": "organization",
                },
            ),
            "concepto": forms.TextInput(
                attrs={
                    "class": "gastos-control",
                    "placeholder": (
                        "Ej. Factura de septiembre"
                    ),
                    "autocomplete": "off",
                },
            ),
            "importe": forms.NumberInput(
                attrs={
                    "class": "gastos-control",
                    "min": "0.01",
                    "step": "0.01",
                    "placeholder": "0,00",
                    "inputmode": "decimal",
                },
            ),
            "fecha": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "class": "gastos-control",
                    "type": "date",
                },
            ),
            "cotizacion_usd": forms.NumberInput(
                attrs={
                    "class": "gastos-control",
                    "min": "0.0001",
                    "step": "0.0001",
                    "placeholder": (
                        "Se consultará automáticamente"
                    ),
                    "inputmode": "decimal",
                },
            ),
            "pagado": forms.CheckboxInput(
                attrs={
                    "class": "gastos-checkbox",
                },
            ),
            "destino_gestoria": forms.Select(
                attrs={
                    "class": "gastos-control",
                },
            ),
            "justificante": (
                forms.ClearableFileInput(
                    attrs={
                        "class": "gastos-file",
                        "accept": (
                            ".pdf,.jpg,.jpeg,.png,"
                            ".webp,application/pdf,"
                            "image/jpeg,image/png,"
                            "image/webp"
                        ),
                    },
                )
            ),
            "notas": forms.Textarea(
                attrs={
                    "class": (
                        "gastos-control "
                        "gastos-textarea"
                    ),
                    "rows": 3,
                    "placeholder": (
                        "Información adicional"
                    ),
                },
            ),
        }

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        propiedad_id = kwargs.pop(
            "propiedad_id",
            None,
        )

        super().__init__(
            *args,
            **kwargs,
        )

        self.fields["ambito"].choices = [
            ("empresa", "Sociedad"),
            ("propiedad", "Propiedad"),
            ("proyecto", "Proyecto"),
        ]

        self.fields["fecha"].input_formats = [
            "%Y-%m-%d",
        ]

        campos_opcionales = [
            "propiedad",
            "habitacion",
            "proyecto",
            "tipo_suministro",
            "consumo",
            "unidad_consumo",
            "concepto",
            "cotizacion_usd",
        ]

        for nombre in campos_opcionales:
            self.fields[nombre].required = False

        self.fields["importe"].required = True

        self.fields["propiedad"].empty_label = (
            "Selecciona una propiedad"
        )

        self.fields["habitacion"].empty_label = (
            "Toda la propiedad"
        )

        self.fields["proyecto"].empty_label = (
            "Selecciona un proyecto"
        )

        self.fields["tipo_suministro"].choices = [
            ("", "Selecciona el suministro"),
            *Gasto.TIPOS_SUMINISTRO,
        ]

        self.fields["unidad_consumo"].choices = [
            ("", "Selecciona la unidad"),
            *Gasto.UNIDADES_CONSUMO,
        ]

        self.fields["propiedad"].queryset = (
            Flat.objects
            .all()
            .order_by("nombre")
        )

        self.fields["habitacion"].queryset = (
            Habitacion.objects.none()
        )

        self.fields["proyecto"].queryset = (
            Proyecto.objects.none()
        )

        self._configurar_habitaciones(
            propiedad_id
        )

        self._configurar_proyectos()

        if (
            not self.is_bound
            and not self.instance.pk
        ):
            hoy = timezone.localdate()

            self.fields["fecha"].initial = hoy

            self.fields[
                "fecha_inicio"
            ].initial = hoy

            self.fields[
                "dia_generacion"
            ].initial = hoy.day

            self.fields[
                "mes_generacion"
            ].initial = hoy.month

        if (
            self.instance
            and self.instance.pk
        ):
            self.fields[
                "es_recurrente"
            ].initial = False

    def _configurar_habitaciones(
        self,
        propiedad_id,
    ):
        if not propiedad_id and self.is_bound:
            propiedad_id = self.data.get(
                "propiedad"
            )

        if (
            not propiedad_id
            and self.instance
            and self.instance.pk
        ):
            propiedad_id = (
                self.instance.propiedad_id
            )

        try:
            propiedad_id = (
                int(propiedad_id)
                if propiedad_id
                else None
            )

        except (
            TypeError,
            ValueError,
        ):
            propiedad_id = None

        if propiedad_id:
            self.fields[
                "habitacion"
            ].queryset = (
                Habitacion.objects
                .filter(
                    propiedad_id=propiedad_id,
                )
                .order_by("nombre")
            )

    def _configurar_proyectos(self):
        if self.is_bound:
            pais = self.data.get(
                "pais"
            )

            proyecto_id = self.data.get(
                "proyecto"
            )

        else:
            pais = getattr(
                self.instance,
                "pais",
                None,
            )

            proyecto_id = getattr(
                self.instance,
                "proyecto_id",
                None,
            )

        if pais:
            self.fields[
                "proyecto"
            ].queryset = (
                Proyecto.objects
                .filter(
                    pais=pais,
                    activo=True,
                )
                .order_by("nombre")
            )

        elif proyecto_id:
            self.fields[
                "proyecto"
            ].queryset = (
                Proyecto.objects
                .filter(
                    pk=proyecto_id,
                )
            )

    def clean(self):
        cleaned_data = super().clean()

        pais = cleaned_data.get("pais")
        ambito = cleaned_data.get("ambito")

        propiedad = cleaned_data.get(
            "propiedad"
        )

        habitacion = cleaned_data.get(
            "habitacion"
        )

        proyecto = cleaned_data.get(
            "proyecto"
        )

        categoria = cleaned_data.get(
            "categoria"
        )

        tipo_suministro = cleaned_data.get(
            "tipo_suministro"
        )

        consumo = cleaned_data.get(
            "consumo"
        )

        unidad_consumo = cleaned_data.get(
            "unidad_consumo"
        )

        importe = cleaned_data.get(
            "importe"
        )

        cotizacion_usd = cleaned_data.get(
            "cotizacion_usd"
        )

        fecha = cleaned_data.get(
            "fecha"
        )

        es_recurrente = cleaned_data.get(
            "es_recurrente",
            False,
        )

        frecuencia = cleaned_data.get(
            "frecuencia"
        )

        dia_generacion = cleaned_data.get(
            "dia_generacion"
        )

        mes_generacion = cleaned_data.get(
            "mes_generacion"
        )

        fecha_inicio = cleaned_data.get(
            "fecha_inicio"
        )

        fecha_fin = cleaned_data.get(
            "fecha_fin"
        )


        # =================================================
        # PAÍS, MONEDA Y DESTINO
        # =================================================

        if not pais:
            self.add_error(
                "pais",
                "Selecciona el país del gasto.",
            )

        if pais == "ES":
            self.instance.moneda = "EUR"

            cleaned_data[
                "cotizacion_usd"
            ] = None

            self.instance.cotizacion_usd = None
            self.instance.importe_usd = None
            self.instance.fecha_cotizacion = None
            self.instance.fuente_cotizacion = ""

            if ambito == "proyecto":
                self.add_error(
                    "ambito",
                    (
                        "En España selecciona "
                        "Sociedad o Propiedad."
                    ),
                )

        elif pais == "AR":
            self.instance.moneda = "ARS"

            if ambito != "proyecto":
                self.add_error(
                    "ambito",
                    (
                        "Los gastos de Argentina deben "
                        "asignarse a un proyecto."
                    ),
                )

            if (
                cotizacion_usd is not None
                and cotizacion_usd <= 0
            ):
                self.add_error(
                    "cotizacion_usd",
                    (
                        "La cotización debe ser "
                        "superior a cero."
                    ),
                )


        # =================================================
        # DESTINO
        # =================================================

        if ambito == "empresa":
            cleaned_data["propiedad"] = None
            cleaned_data["habitacion"] = None
            cleaned_data["proyecto"] = None

            self.instance.propiedad = None
            self.instance.habitacion = None
            self.instance.proyecto = None

        elif ambito == "propiedad":
            cleaned_data["proyecto"] = None
            self.instance.proyecto = None

            if not propiedad:
                self.add_error(
                    "propiedad",
                    (
                        "Selecciona la propiedad "
                        "correspondiente."
                    ),
                )

            if (
                propiedad
                and habitacion
                and habitacion.propiedad_id
                != propiedad.pk
            ):
                self.add_error(
                    "habitacion",
                    (
                        "La habitación no pertenece "
                        "a la propiedad seleccionada."
                    ),
                )

        elif ambito == "proyecto":
            cleaned_data["propiedad"] = None
            cleaned_data["habitacion"] = None

            self.instance.propiedad = None
            self.instance.habitacion = None

            if not proyecto:
                self.add_error(
                    "proyecto",
                    "Selecciona un proyecto.",
                )

            elif (
                pais
                and proyecto.pais != pais
            ):
                self.add_error(
                    "proyecto",
                    (
                        "El proyecto no pertenece "
                        "al país seleccionado."
                    ),
                )

        else:
            self.add_error(
                "ambito",
                (
                    "Selecciona el destino "
                    "del gasto."
                ),
            )


        # =================================================
        # SUMINISTROS
        # =================================================

        if categoria == "suministros":
            if not tipo_suministro:
                self.add_error(
                    "tipo_suministro",
                    (
                        "Selecciona el tipo "
                        "de suministro."
                    ),
                )

            if (
                consumo is not None
                and consumo <= Decimal("0")
            ):
                self.add_error(
                    "consumo",
                    (
                        "El consumo debe ser "
                        "superior a cero."
                    ),
                )

            if (
                consumo is not None
                and not unidad_consumo
            ):
                self.add_error(
                    "unidad_consumo",
                    (
                        "Selecciona la unidad."
                    ),
                )

            if (
                unidad_consumo
                and consumo is None
            ):
                self.add_error(
                    "consumo",
                    (
                        "Introduce el consumo o elimina "
                        "la unidad seleccionada."
                    ),
                )

        else:
            cleaned_data[
                "tipo_suministro"
            ] = ""

            cleaned_data["consumo"] = None

            cleaned_data[
                "unidad_consumo"
            ] = ""

            self.instance.tipo_suministro = ""
            self.instance.consumo = None
            self.instance.unidad_consumo = ""


        # =================================================
        # IMPORTE
        # =================================================

        if importe is None:
            self.add_error(
                "importe",
                "Introduce el importe del gasto.",
            )

        elif importe < Decimal("0.01"):
            self.add_error(
                "importe",
                (
                    "El importe debe ser "
                    "superior a cero."
                ),
            )


        # =================================================
        # RECURRENCIA
        # =================================================

        if es_recurrente:
            if not frecuencia:
                self.add_error(
                    "frecuencia",
                    "Selecciona la frecuencia.",
                )

            if dia_generacion is None:
                self.add_error(
                    "dia_generacion",
                    (
                        "Indica el día previsto "
                        "de generación."
                    ),
                )

            if not fecha_inicio:
                fecha_inicio = (
                    fecha
                    or timezone.localdate()
                )

                cleaned_data[
                    "fecha_inicio"
                ] = fecha_inicio

            if (
                fecha_inicio
                and fecha_fin
                and fecha_fin < fecha_inicio
            ):
                self.add_error(
                    "fecha_fin",
                    (
                        "La fecha de finalización "
                        "no puede ser anterior "
                        "a la fecha de inicio."
                    ),
                )

            if (
                frecuencia == "anual"
                and not mes_generacion
            ):
                self.add_error(
                    "mes_generacion",
                    (
                        "Selecciona el mes del "
                        "gasto anual."
                    ),
                )

        return cleaned_data

    def clean_justificante(self):
        archivo = self.cleaned_data.get(
            "justificante"
        )

        if not archivo:
            return archivo

        nombre = getattr(
            archivo,
            "name",
            "",
        )

        extensiones_permitidas = (
            ".pdf",
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
        )

        if not nombre.lower().endswith(
            extensiones_permitidas
        ):
            raise forms.ValidationError(
                (
                    "El justificante debe ser "
                    "PDF, JPG, JPEG, PNG o WEBP."
                )
            )

        tamaño = getattr(
            archivo,
            "size",
            0,
        )

        limite = 10 * 1024 * 1024

        if tamaño and tamaño > limite:
            raise forms.ValidationError(
                (
                    "El justificante no puede "
                    "superar los 10 MB."
                )
            )

        return archivo

class CompletarGastoPendienteForm(forms.Form):

    importe = forms.DecimalField(
        min_value=Decimal("0.01"),
        max_digits=10,
        decimal_places=2,
        label="Importe real",
    )

    justificante = forms.FileField(
        required=True,
        label="Factura o justificante",
    )

    pagado = forms.BooleanField(
        required=False,
        initial=True,
        label="Pagado",
    )

class ContratoAlquilerForm(forms.ModelForm):

    propiedad = forms.ModelChoiceField(
        queryset=Flat.objects.all().order_by("nombre"),
        required=True,
        label="Propiedad",
    )

    class Meta:
        model = ContratoAlquiler

        fields = [
            "propiedad",
            "habitacion",
            "fecha_inicio",
            "fecha_fin",
            "precio_mensual",
            "fianza",
        ]

        widgets = {
            "fecha_inicio": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "type": "date",
                },
            ),
            "fecha_fin": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "type": "date",
                },
            ),
            "precio_mensual": forms.NumberInput(
                attrs={
                    "min": "0.01",
                    "step": "0.01",
                },
            ),
            "fianza": forms.NumberInput(
                attrs={
                    "min": "0",
                    "step": "0.01",
                },
            ),
        }

        labels = {
            "habitacion": "Habitación libre",
            "fecha_inicio": "Fecha de inicio",
            "fecha_fin": "Fecha de renovación o finalización",
            "precio_mensual": "Precio mensual",
            "fianza": "Fianza",
        }

    def __init__(self, *args, **kwargs):
        propiedad_id = kwargs.pop(
            "propiedad_id",
            None,
        )

        habitacion_id = kwargs.pop(
            "habitacion_id",
            None,
        )

        contrato = kwargs.get(
            "instance",
        )

        super().__init__(
            *args,
            **kwargs,
        )

        self.fields[
            "fecha_inicio"
        ].input_formats = ["%Y-%m-%d"]

        self.fields[
            "fecha_fin"
        ].input_formats = ["%Y-%m-%d"]

        # En un POST recuperamos la propiedad enviada.
        if not propiedad_id and self.is_bound:
            propiedad_id = self.data.get(
                "propiedad"
            )

        # Al modificar un contrato utilizamos su propiedad.
        if (
            not propiedad_id
            and contrato
            and contrato.habitacion_id
        ):
            propiedad_id = (
                contrato.habitacion.propiedad_id
            )

        habitaciones_libres = (
            Habitacion.objects.none()
        )

        if propiedad_id:
            contratos_activos = (
                ContratoAlquiler.objects
                .filter(
                    activo=True,
                )
            )

            # Cuando modificamos un contrato, no contamos
            # ese mismo contrato como impedimento.
            if contrato and contrato.pk:
                contratos_activos = (
                    contratos_activos.exclude(
                        pk=contrato.pk,
                    )
                )

            habitaciones_libres = (
                Habitacion.objects
                .filter(
                    propiedad_id=propiedad_id,
                )
                .exclude(
                    pk__in=contratos_activos.values(
                        "habitacion_id"
                    ),
                )
                .exclude(
                    procesos_formalizacion__estado__in=[
                        ProcesoFormalizacion.Estado.PENDIENTE,
                        ProcesoFormalizacion.Estado.INICIADO,
                    ],
                )
                .distinct()
                .order_by("nombre")
            )

            self.fields[
                "propiedad"
            ].initial = propiedad_id

        self.fields[
            "habitacion"
        ].queryset = habitaciones_libres

        self.fields[
            "habitacion"
        ].empty_label = (
            "Selecciona una habitación libre"
        )

        if (
            habitacion_id
            and habitaciones_libres.filter(
                pk=habitacion_id,
            ).exists()
        ):
            self.fields[
                "habitacion"
            ].initial = habitacion_id

class AvalContratoForm(forms.ModelForm):

    class Meta:
        model = AvalContrato

        fields = [
            "nombre_completo",
            "dni_nie",
            "domicilio",
        ]

        widgets = {
            "nombre_completo": forms.TextInput(
                attrs={
                    "placeholder": "Nombre y apellidos",
                    "autocomplete": "name",
                }
            ),
            "dni_nie": forms.TextInput(
                attrs={
                    "placeholder": "DNI, NIE o pasaporte",
                }
            ),
            "domicilio": forms.TextInput(
                attrs={
                    "placeholder": "Domicilio del avalista",
                    "autocomplete": "street-address",
                }
            ),
        }

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['telefono', 'dni', 'direccion', 'cp', 'ciudad', 'pais', 'cumpleaños']

class InquilinoForm(forms.ModelForm):

    class Meta:
        model = Inquilino

        fields = [
            "nombre",
            "email",
            "dni",
            "direccion",
            "telefono",
            "nacionalidad",
        ]

        widgets = {
            "telefono": forms.TextInput(
                attrs={
                    "type": "tel",
                    "inputmode": "tel",
                    "autocomplete": "tel",
                    "placeholder": "+34 612 345 678",
                }
            ),
        }

        labels = {
            "telefono": "Teléfono / WhatsApp",
        }

    def clean_telefono(self):
        telefono = self.cleaned_data.get("telefono")

        if not telefono:
            return telefono

        telefono = telefono.strip()

        if telefono.startswith("00"):
            telefono = f"+{telefono[2:]}"

        if not telefono.startswith("+"):
            raise forms.ValidationError(
                "Incluye el prefijo internacional, por ejemplo +34, +57 o +1."
            )

        solo_numeros = re.sub(
            r"\D",
            "",
            telefono,
        )

        if len(solo_numeros) < 8:
            raise forms.ValidationError(
                "Introduce un número de teléfono válido."
            )

        if len(solo_numeros) > 15:
            raise forms.ValidationError(
                "El número de teléfono es demasiado largo."
            )

        return telefono

class CrearProcesoFormalizacionForm(forms.ModelForm):

    class Meta:
        model = ProcesoFormalizacion

        fields = [
            "fecha_inicio_contrato",
            "duracion_meses",
            "precio_mensual",
            "fianza",
            "tipo_primera_renta",
            "observaciones",
        ]

        labels = {
            "fecha_inicio_contrato": "Fecha de inicio",
            "duracion_meses": "Duración inicial en meses",
            "precio_mensual": "Precio mensual",
            "fianza": "Fianza",
            "tipo_primera_renta": "Primera renta",
            "observaciones": "Observaciones internas",
        }

        error_messages = {
            "fecha_inicio_contrato": {
                "required": "Oye, te falta indicar la fecha de inicio.",
                "invalid": "Introduce una fecha de inicio válida.",
            },
            "duracion_meses": {
                "required": "Oye, te falta indicar la duración.",
                "invalid": "Introduce una duración válida.",
            },
            "precio_mensual": {
                "required": "Oye, te falta indicar el precio mensual.",
                "invalid": "Introduce un precio mensual válido.",
            },
            "fianza": {
                "required": "Oye, te falta indicar la fianza.",
                "invalid": "Introduce un importe de fianza válido.",
            },
            "tipo_primera_renta": {
                "required": "Oye, te falta seleccionar la primera renta.",
                "invalid_choice": "Selecciona una opción válida.",
            },
        }

        widgets = {
            "fecha_inicio_contrato": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "type": "date",
                    "required": True,
                },
            ),
            "duracion_meses": forms.NumberInput(
                attrs={
                    "min": 1,
                    "required": True,
                },
            ),
            "precio_mensual": forms.NumberInput(
                attrs={
                    "min": 0.01,
                    "step": "0.01",
                    "required": True,
                },
            ),
            "fianza": forms.NumberInput(
                attrs={
                    "min": 0,
                    "step": "0.01",
                    "required": True,
                },
            ),
            "tipo_primera_renta": forms.Select(
                attrs={
                    "required": True,
                },
            ),
            "observaciones": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": (
                        "Información interna que no aparecerá "
                        "en el contrato."
                    ),
                },
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields[
            "fecha_inicio_contrato"
        ].input_formats = ["%Y-%m-%d"]

        # Las condiciones son obligatorias.
        for field_name in [
            "fecha_inicio_contrato",
            "duracion_meses",
            "precio_mensual",
            "fianza",
            "tipo_primera_renta",
        ]:
            self.fields[field_name].required = True

        # Las observaciones continúan siendo opcionales.
        self.fields["observaciones"].required = False

    def clean_fecha_inicio_contrato(self):
        fecha = self.cleaned_data.get("fecha_inicio_contrato")

        if fecha is None:
            raise forms.ValidationError(
                "Oye, te falta indicar la fecha de inicio."
            )

        return fecha

    def clean_duracion_meses(self):
        duracion = self.cleaned_data.get("duracion_meses")

        if duracion is None:
            raise forms.ValidationError(
                "Oye, te falta indicar la duración."
            )

        if duracion < 1:
            raise forms.ValidationError(
                "La duración debe ser de al menos un mes."
            )

        return duracion

    def clean_precio_mensual(self):
        precio = self.cleaned_data.get("precio_mensual")

        if precio is None:
            raise forms.ValidationError(
                "Oye, te falta indicar el precio mensual."
            )

        if precio <= 0:
            raise forms.ValidationError(
                "El precio mensual debe ser mayor que cero."
            )

        return precio

    def clean_fianza(self):
        fianza = self.cleaned_data.get("fianza")

        if fianza is None:
            raise forms.ValidationError(
                "Oye, te falta indicar la fianza."
            )

        if fianza < 0:
            raise forms.ValidationError(
                "La fianza no puede ser negativa."
            )

        return fianza

    def clean_tipo_primera_renta(self):
        tipo = self.cleaned_data.get("tipo_primera_renta")

        if not tipo:
            raise forms.ValidationError(
                "Oye, te falta seleccionar la primera renta."
            )

        return tipo

class ProyectoForm(forms.ModelForm):

    class Meta:
        model = Proyecto

        fields = [
            "nombre",
            "pais",
            "tipo",
            "estado",
            "ciudad",
            "provincia",
            "activo",
            "descripcion",
        ]

        labels = {
            "nombre": "Nombre del proyecto",
            "pais": "País",
            "tipo": "Tipo de proyecto",
            "estado": "Estado",
            "ciudad": "Ciudad",
            "provincia": "Provincia",
            "activo": "Proyecto activo",
            "descripcion": "Descripción",
        }

        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "class": "proyectos-control",
                    "placeholder": "Ej. Fedora",
                    "autocomplete": "off",
                },
            ),
            "pais": forms.Select(
                attrs={
                    "class": "proyectos-control",
                },
            ),
            "tipo": forms.Select(
                attrs={
                    "class": "proyectos-control",
                },
            ),
            "estado": forms.Select(
                attrs={
                    "class": "proyectos-control",
                },
            ),
            "ciudad": forms.TextInput(
                attrs={
                    "class": "proyectos-control",
                    "placeholder": "Ej. San Fernando del Valle",
                },
            ),
            "provincia": forms.TextInput(
                attrs={
                    "class": "proyectos-control",
                    "placeholder": "Ej. Catamarca",
                },
            ),
            "activo": forms.CheckboxInput(
                attrs={
                    "class": "proyectos-checkbox",
                },
            ),
            "descripcion": forms.Textarea(
                attrs={
                    "class": (
                        "proyectos-control "
                        "proyectos-textarea"
                    ),
                    "rows": 4,
                    "placeholder": (
                        "Objetivos, características y "
                        "estado general del proyecto."
                    ),
                },
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        estado = cleaned_data.get("estado")
        activo = cleaned_data.get("activo")

        if estado == "finalizado" and activo:
            cleaned_data["activo"] = False

        return cleaned_data

class IngresoPropiedadForm(forms.ModelForm):

    class Meta:
        model = IngresoPropiedad

        fields = [
            "propiedad",
            "concepto",
            "importe",
            "fecha",
            "pagador",
            "notas",
        ]

        labels = {
            "propiedad": "Propiedad",
            "concepto": "Concepto",
            "importe": "Importe recibido",
            "fecha": "Fecha del ingreso",
            "pagador": "Pagador o referencia",
            "notas": "Notas",
        }

        widgets = {
            "propiedad": forms.Select(
                attrs={
                    "class": "ingreso-control",
                },
            ),
            "concepto": forms.TextInput(
                attrs={
                    "class": "ingreso-control",
                    "placeholder": (
                        "Ej. Alquiler temporal"
                    ),
                },
            ),
            "importe": forms.NumberInput(
                attrs={
                    "class": "ingreso-control",
                    "min": "0.01",
                    "step": "0.01",
                    "inputmode": "decimal",
                    "placeholder": "0,00",
                },
            ),
            "fecha": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "class": "ingreso-control",
                    "type": "date",
                },
            ),
            "pagador": forms.TextInput(
                attrs={
                    "class": "ingreso-control",
                    "placeholder": (
                        "Ej. Luis"
                    ),
                    "autocomplete": "name",
                },
            ),
            "notas": forms.Textarea(
                attrs={
                    "class": (
                        "ingreso-control "
                        "ingreso-textarea"
                    ),
                    "rows": 4,
                    "placeholder": (
                        "Información adicional "
                        "sobre la estancia"
                    ),
                },
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            **kwargs,
        )

        self.fields[
            "propiedad"
        ].queryset = (
            Flat.objects
            .all()
            .order_by("nombre")
        )

        self.fields[
            "fecha"
        ].input_formats = [
            "%Y-%m-%d",
        ]

        if not self.is_bound:
            self.fields[
                "fecha"
            ].initial = timezone.localdate()

            self.fields[
                "concepto"
            ].initial = "Alquiler temporal"

    def clean_importe(self):
        importe = self.cleaned_data.get(
            "importe"
        )

        if (
            importe is None
            or importe <= 0
        ):
            raise forms.ValidationError(
                "El importe debe ser superior a cero."
            )

        return importe