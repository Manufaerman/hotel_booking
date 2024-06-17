import datetime

from ..booking_functions.save_many_prices import all_dates_between_dates, first_day_month, last_day_month,\
list_days_month
from datetime import date, datetime
from ..models import Booking, Price

def run(id=1):
    first_day = first_day_month()
    last_day = last_day_month()
    bookings = Booking.objects.filter(check_in__gt=first_day,
                                      check_in__lte=last_day)

    booking_name = [book.room.name for book in bookings]
    booking_numbers = dict(zip(booking_name, map(lambda x: booking_name.count(x), booking_name)))
    print(booking_numbers)
    precios = {}
    try:

        precios['Tolima'] = booking_numbers['Tolima'] * 3 * 12
        print(precios['Tolima'])

    except KeyError:
        precios['Tolima'] = 0

    try:
        precios['Barichara'] = booking_numbers['Barichara'] * 2 * 12
        print(precios['Barichara'])
    except KeyError:
        precios['Barichara'] = 0

    try:
        precios[booking_numbers['San luis']] = booking_numbers['San luis'] * 2 * 12
        print(precios['San luis'])
    except KeyError:
        precios['San Luis'] = 0

    print(sum(precios.values()),'------------------')
    print(precios.values())








