from django.db import connection
from ..booking_functions.save_many_prices import all_dates_between_dates, first_day_month, last_day_month
from ..models import Room, Booking, PriceDate

def run():
   first_day = first_day_month()
   last_day = last_day_month()
   bookings = Booking.objects.filter(check_in__fecha__gt=first_day,
                                     check_in__fecha__lte=last_day,
                                     room__id=2)
   lista = []
   for book in bookings:
      pricedate_in = book.check_in
      price = pricedate_in.price
      pricedate_in = pricedate_in.fecha
      pricedate_out = book.check_out
      pricedate_out = pricedate_out.fecha

      lista.append(all_dates_between_dates(pricedate_in, pricedate_out))
      lista = []
   print (lista)