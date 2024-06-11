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

    rooms = Room.objects.all()
    room_names = ((room.id, room.name)for room in rooms)

    name = forms.ChoiceField(choices=room_names, required=True)

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

    price = forms.IntegerField(max_value=150)


