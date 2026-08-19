import re
from django import forms
from django.contrib.auth.models import User
from hotel.models import Inquilino, ContratoAlquiler, Flat, Habitacion, AvalContrato
from user_profile.models import UserProfile
from django import forms
from .models import ProcesoFormalizacion

from django import forms
from django.utils import timezone

from .models import (
    Flat,
    Habitacion,
    Gasto,
)


class GastoForm(forms.ModelForm):

    class Meta:
        model = Gasto

        fields = [
            "propiedad",
            "habitacion",
            "concepto",
            "categoria",
            "importe",
            "fecha",
            "pagado",
            "proveedor",
            "justificante",
            "notas",
        ]

        labels = {
            "propiedad": "Propiedad",
            "habitacion": "Habitación",
            "concepto": "Concepto",
            "categoria": "Categoría",
            "importe": "Importe",
            "fecha": "Fecha",
            "pagado": "Pagado",
            "proveedor": "Proveedor",
            "justificante": "Factura o justificante",
            "notas": "Notas",
        }

        widgets = {
            "propiedad": forms.Select(
                attrs={
                    "class": "gasto-control",
                },
            ),
            "habitacion": forms.Select(
                attrs={
                    "class": "gasto-control",
                },
            ),
            "concepto": forms.TextInput(
                attrs={
                    "class": "gasto-control",
                    "placeholder": "Ej. Reparación de la ducha",
                },
            ),
            "categoria": forms.Select(
                attrs={
                    "class": "gasto-control",
                },
            ),
            "importe": forms.NumberInput(
                attrs={
                    "class": "gasto-control",
                    "min": "0.01",
                    "step": "0.01",
                    "placeholder": "0,00",
                },
            ),
            "fecha": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "class": "gasto-control",
                    "type": "date",
                },
            ),
            "pagado": forms.CheckboxInput(
                attrs={
                    "class": "gasto-checkbox",
                },
            ),
            "proveedor": forms.TextInput(
                attrs={
                    "class": "gasto-control",
                    "placeholder": "Nombre del proveedor",
                },
            ),
            "justificante": forms.ClearableFileInput(
                attrs={
                    "class": "gasto-file",
                    "accept": ".pdf,.jpg,.jpeg,.png,.webp",
                },
            ),
            "notas": forms.Textarea(
                attrs={
                    "class": "gasto-control gasto-textarea",
                    "rows": 3,
                    "placeholder": "Información adicional",
                },
            ),
        }

    def __init__(self, *args, **kwargs):
        propiedad_id = kwargs.pop(
            "propiedad_id",
            None,
        )

        super().__init__(
            *args,
            **kwargs,
        )

        self.fields[
            "fecha"
        ].input_formats = ["%Y-%m-%d"]

        self.fields[
            "propiedad"
        ].queryset = Flat.objects.all().order_by(
            "nombre"
        )

        if not propiedad_id and self.is_bound:
            propiedad_id = self.data.get(
                "propiedad"
            )

        if (
            not propiedad_id
            and self.instance
            and self.instance.pk
        ):
            propiedad_id = self.instance.propiedad_id

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
        else:
            self.fields[
                "habitacion"
            ].queryset = Habitacion.objects.none()

        self.fields[
            "habitacion"
        ].required = False

        self.fields[
            "habitacion"
        ].empty_label = (
            "Gasto general de la propiedad"
        )

        if not self.is_bound and not self.instance.pk:
            self.fields[
                "fecha"
            ].initial = timezone.localdate()

    def clean_justificante(self):
        archivo = self.cleaned_data.get(
            "justificante"
        )

        if not archivo:
            return archivo

        extensiones_permitidas = (
            ".pdf",
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
        )

        if not archivo.name.lower().endswith(
            extensiones_permitidas
        ):
            raise forms.ValidationError(
                "El justificante debe ser PDF, JPG, PNG o WEBP."
            )

        limite = 10 * 1024 * 1024

        if archivo.size > limite:
            raise forms.ValidationError(
                "El justificante no puede superar los 10 MB."
            )

        return archivo


class CrearProcesoFormalizacionForm(forms.ModelForm):

    class Meta:
        model = ProcesoFormalizacion

        fields = [
            "fecha_inicio_contrato",
            "duracion_meses",
            "precio_mensual",
            "fianza",
        ]

        widgets = {
            "fecha_inicio_contrato": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),
            "duracion_meses": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                }
            ),
            "precio_mensual": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": 0,
                }
            ),
            "fianza": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": 0,
                }
            ),
        }

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
