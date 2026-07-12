from django.dispatch import receiver
from .signal import save_price_signal




"""@receiver(save_price_signal, sender= Booking)
def save_prices(sender, room, check_in, check_out, precio, **kwargs):
    all_dates = all_dates_between_dates(check_in, check_out)
    for date in all_dates:
        price_book = Price.objects.get_or_create(room=room, precio=precio, date_price=date)
        price_book[0].save()"""



