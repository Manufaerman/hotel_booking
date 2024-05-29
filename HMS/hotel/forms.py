from django import forms


class AvailibilityForm(forms.Form):
    ROOM_CATEGORIES = {
        ('YAC', 'Double bedroom with AC'),
        ('NAC', 'Double bedroom with out AC'),
        ('ONE', '1 ROOM flat whit AC'),
        ('TWO', '2 ROOMS flat whit out AC'),
        ('3AC', '3 ROOMS flat whit AC')
    }
    room_category = forms.ChoiceField(required=True, choices=ROOM_CATEGORIES)
    check_in = forms.DateField(required=True, input_formats='%Y-%m-%dT%H:%M',)
    check_out = forms.DateField(required=True, input_formats='%Y-%m-%dT%H:%M', )


"""
"""


