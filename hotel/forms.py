import datetime
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from django import forms
from django.contrib.auth.models import User

from hotel.models import Booking
from user_profile.models import UserProfile



class AvailibilityForm(forms.Form):

    check_in = forms.DateField(
        required=True,
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
        input_formats=["%Y-%m-%d"]
    )

    check_out = forms.DateField(
        required=True,
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
        input_formats=["%Y-%m-%d"]
    )


OPCIONES_COLOR = [
    ('tolima', 'Tolima'),
    ('barichara', 'Barichara'),
    ('san luis', 'San Luis')
]

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone', 'dni', 'address', 'cp', 'city', 'country', 'birthday']

class BookingForm(forms.ModelForm):  # <-- IMPORTANTE: ModelForm, no Form
    class Meta:
        model = Booking
        fields = ['check_in', 'check_out', 'room', 'price']

class AddBooking(forms.Form):
    flat = forms.ChoiceField(
        choices=OPCIONES_COLOR,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='',
        required=True,
    )
    name = forms.CharField(
        required=True,
        label='',
        widget=forms.TextInput(attrs={'placeholder': 'Name'}),
    )
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'last Name'}),)
    email = forms.EmailField(
        required=False,
        label='',
        widget=forms.TextInput(attrs={'placeholder': 'Email'}),
    )
    phone = forms.IntegerField(
        required=False,
        label='',
        widget=forms.TextInput(attrs={'placeholder': 'Phone'}),
    )
    check_in = forms.DateField(
        required=True,
        label='',
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
        input_formats=["%Y-%m-%d"]
    )

    check_out = forms.DateField(
        required=True,
        label='',
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
        input_formats=["%Y-%m-%d"]
    )

    price = forms.IntegerField(
        max_value=4050,
        label='',
        widget=forms.TextInput(attrs={'placeholder': 'Price'}),
    )

    def clean(self):
        cleaned_data = self.cleaned_data
        check_in = cleaned_data['check_in']
        check_out = cleaned_data['check_out']
        today = datetime.date.today()

        return cleaned_data
        """
                if check_in < today:
            raise ValidationError('Invalid date - renewal in past')

        if check_in > check_out:
            raise ValidationError('Invalid date - check in greater than check out')

        else:
        """

