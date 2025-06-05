from calendar import monthrange

from django.db.models import Sum
from ..models import Room, Booking
from .dates_functions import first_day_month_x, last_day_month_x, all_dates_between_dates,\
    list_days_month, first_day_month, last_day_month
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from icecream import ic


def total_price_booking(check_in, check_out, price):
    all_dates = len(all_dates_between_dates(check_in, check_out)) - 1
    return price * all_dates


def total_price_cleanings_current_month(month=date.today().month):
    first_day = first_day_month_x(str(month))
    last_day = last_day_month_x(str(month))
    bookings = Booking.objects.filter(check_in__gt=first_day,
                                      check_in__lte=last_day)

    booking_name = [book.room.name for book in bookings]
    booking_numbers = dict(zip(booking_name, map(lambda x: booking_name.count(x), booking_name)))
    print(booking_numbers)
    precios = {}
    try:

        precios['Tolima'] = booking_numbers['Tolima'] * 3 * 12

    except KeyError:
        precios['Tolima'] = 0


    try:
        precios['Barichara'] = booking_numbers['Barichara'] * 2 * 12

    except KeyError:
        precios['Barichara'] = 0

    try:
        precios[booking_numbers['San luis']] = booking_numbers['San luis'] * 2 * 12

    except KeyError:
        precios['San Luis'] = 0

    return sum(precios.values())


# return all the prices of a month
def total_month_bookings(month: int = None, year: int = None):

    today = date.today()
    month = int(month or today.month)
    year = year or today.year

    first_day = date(year, int(month), 1)

    last_day = date(year, month, monthrange(year, month)[1])

    total = Booking.objects.filter(
        check_in__gte=first_day,
        check_in__lte=last_day
    ).aggregate(total_price=Sum('price'))['total_price'] or 0

    return total


def previus_month_bookings():
    today = date.today()
    first_day = date(today.year, today.month, 1) + relativedelta(months=-1)
    last_day = date(today.year, today.month, 1)  # primer día del mes actual

    total = Booking.objects.filter(
        check_in__gte=first_day,
        check_in__lt=last_day
    ).aggregate(Sum('total_price'))['total_price__sum'] or 0

    return total


#working  --->
def total_days_book_and_not_book_current_month(room_id: str, month: int = None):
    if month is None:
        month = date.today().month
    year = date.today().year

    first_day = date(year, month, 1)
    if month == 12:
        last_day = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = date(year, month + 1, 1) - timedelta(days=1)

    bookings = Booking.objects.filter(
        check_in__lte=last_day,
        check_out__gte=first_day,
        room__id=room_id
    )

    days_status = {}
    for booking in bookings:
        start = max(booking.check_in, first_day)
        end = min(booking.check_out, last_day)
        total_days = (end - start).days + 1

        if total_days <= 0:
            continue

        price_per_day = round(booking.price / ((booking.check_out - booking.check_in).days or 1), 2)

        for i in range(total_days):
            current_day = start + timedelta(days=i)
            day_str = current_day.strftime('%Y-%m-%d')
            days_status[day_str] = (price_per_day, True)

    # Agregar días sin reserva
    current_day = first_day
    while current_day <= last_day:
        day_str = current_day.strftime('%Y-%m-%d')
        if day_str not in days_status:
            days_status[day_str] = (0, False)
        current_day += timedelta(days=1)

    # Solo devolver el día del mes como clave
    res = {day[-2:]: value for day, value in sorted(days_status.items())}
    return res


def check_availability(room, check_in, check_out):
    avail_list = []
    bookings_list = Booking.objects.filter(room=room)
    if len(bookings_list) > 0:
        for booking in bookings_list:
            new_check_in = booking.check_in
            new_check_out = booking.check_out
            
            print(avail_list)
            if new_check_in >= check_out or new_check_out <= check_in:
                avail_list.append(True)
            else:
                avail_list.append(False)
    else:
        avail_list = [True,]

    return all(avail_list) #all return True if all items are true (any) does the opposite

def booking_month_x(id: str, month: str = str(date.today().month)):
    # Si el mes es de un solo dígito, completamos con 0
    if len(month) == 1:
        month = '0' + month

    first_day = first_day_month_x(month)
    last_day = last_day_month_x(month)

    # Aseguramos que check_in esté entre los dos extremos
    bookings = Booking.objects.filter(
        check_in__gte=first_day,
        check_in__lte=last_day,
        room__id=id,
    )

    return bookings


def booking_year():
    rooms = Room.objects.all()
    lista = []
    for room in rooms:
        bookings = Booking.objects.filter(room)
        lista.append(bookings)
    return lista


if __name__ == "__main__":
    ic | booking_year()
