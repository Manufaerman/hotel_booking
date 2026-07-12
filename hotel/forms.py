
from django import forms
from django.contrib.auth.models import User

from hotel.models import Inquilino, ContratoAlquiler, Flat, Habitacion
from user_profile.models import UserProfile




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
            "precio_mensual",
            "fianza",
        ]

    def __init__(self, *args, **kwargs):
        propiedad_id = kwargs.pop("propiedad_id", None)
        contrato = kwargs.get('instance', None)
        if not propiedad_id and contrato:
            propiedad_id = contrato.habitacion.propiedad_id
        print(propiedad_id, 'estamos en el formmmm justo antes del super', kwargs)
        super().__init__(*args, **kwargs)
        print('kwaersdfgvhjh al entrarrrr', kwargs)
        if propiedad_id:
            habitaciones = Habitacion.objects.filter(propiedad_id=propiedad_id)
            print(habitaciones,'aqui estan todas las habitaciones')
            self.fields["habitacion"].queryset = habitaciones
            self.fields["propiedad"].initial = propiedad_id
        else:

            self.fields["habitacion"].queryset = Habitacion.objects.none()

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

