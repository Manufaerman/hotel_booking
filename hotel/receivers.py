from django.dispatch import receiver
from .signal import save_price_signal
from .models import Booking, Price
from .booking_functions.dates_functions import all_dates_between_dates



"""@receiver(save_price_signal, sender= Booking)
def save_prices(sender, room, check_in, check_out, price, **kwargs):
    all_dates = all_dates_between_dates(check_in, check_out)
    for date in all_dates:
        price_book = Price.objects.get_or_create(room=room, price=price, date_price=date)
        price_book[0].save()"""



