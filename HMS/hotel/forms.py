import datetime
from django.core.exceptions import ValidationError
from django import forms
from .models import Room


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



class AddBooking(forms.Form):

    name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Name'}),
    )
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'last Name'}),)
    email = forms.EmailField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Email'}),
    )
    phone = forms.IntegerField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Phone'}),
    )
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

    price = forms.IntegerField(
        max_value=150,
        widget=forms.TextInput(attrs={'placeholder': 'Price'}),
    )

    def clean(self):
        cleaned_data = self.cleaned_data
        check_in = cleaned_data['check_in']
        check_out = cleaned_data['check_out']
        today = datetime.date.today()

        if check_in < today:
            raise ValidationError('Invalid date - renewal in past')

        if check_in > check_out:
            raise ValidationError('Invalid date - check in greater than check out')

        else:
            return cleaned_data