
from django import forms
from django.contrib.auth.models import User
from hotel.models import Inquilino, ContratoAlquiler, Flat, Habitacion, AvalContrato
from user_profile.models import UserProfile
from django import forms
from .models import ProcesoFormalizacion


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
        queryset=Flat.objects.all(),
        required=True,
        label="Flat"
    )

    class Meta:
        model = ContratoAlquiler
        fields = [
            "propiedad",
            "habitacion",
            "fecha_inicio",
            "fecha_fin",
            "precio_mensual",
            "fianza"]

        widgets = {
            "fecha_inicio": forms.DateInput(
                attrs={"type": "date"}
            ),
            "fecha_fin": forms.DateInput(
                attrs={"type": "date"}
            ),
        }

        labels = {
            "fecha_inicio": "Fecha de inicio",
            "fecha_fin": "Fecha de finalización",
        }

    def __init__(self, *args, **kwargs):
        propiedad_id = kwargs.pop("propiedad_id", None)
        contrato = kwargs.get('instance', None)
        if not propiedad_id and contrato:
            propiedad_id = contrato.habitacion.propiedad_id
        super().__init__(*args, **kwargs)
        if propiedad_id:
            habitaciones = Habitacion.objects.filter(propiedad_id=propiedad_id)
            self.fields["habitacion"].queryset = habitaciones
            self.fields["propiedad"].initial = propiedad_id
        else:

            self.fields["habitacion"].queryset = Habitacion.objects.none()


class AvalContratoForm(forms.ModelForm):
    class Meta:
        model = AvalContrato
        fields = [
            "nombre_completo",
            "dni_nie",
            "domicilio",
        ]


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
        fields = ['nombre', 'email', 'dni', 'direccion', 'telefono', 'nacionalidad']


from django import forms

from .models import ProcesoFormalizacion


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
