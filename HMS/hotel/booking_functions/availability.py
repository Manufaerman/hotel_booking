import datetime
from ..models import Room, Booking
from .save_many_prices import first_day_month, last_day_month, all_dates_between_dates


def total_price_booking(check_in, check_out, price):
    all_dates = len(all_dates_between_dates(check_in, check_out)) - 1
    return price * all_dates

def total_price_cleanings_current_month():
    first_day = first_day_month()
    last_day = last_day_month()
    bookings = Booking.objects.filter(check_in__fecha__gt=first_day,
                                      check_in__fecha__lte=last_day)

    booking_name = [book.room.name for book in bookings]
    booking_numbers = dict(zip(booking_name, map(lambda x: booking_name.count(x), booking_name)))
    print(booking_numbers)
    precios = {}
    if booking_numbers['Tolima']:
        precios['Tolima'] = booking_numbers['Tolima'] * 3 * 12

    if booking_numbers['Barichara']:
        precios['Barichara'] = booking_numbers['Barichara'] * 2 * 12

    if booking_numbers['San luis']:
        precios['San luis'] = booking_numbers['San luis'] * 2 * 12

    return sum(precios.values())

def total_month_bookings():
    first_day = first_day_month()
    last_day = last_day_month()
    bookings = Booking.objects.filter(check_in__fecha__gt=first_day,
                                          check_in__fecha__lte=last_day)
    lista = []
    for book in bookings:
        pricedate_in = book.check_in
        price = pricedate_in.price
        pricedate_in = pricedate_in.fecha
        pricedate_out = book.check_out
        pricedate_out = pricedate_out.fecha

        lista.append((len(all_dates_between_dates(pricedate_in, pricedate_out)) - 1) * price)

    return sum(lista)

def total_days_book_current_month():
    first_day = first_day_month()
    last_day = last_day_month()
    bookings = Booking.objects.filter(check_in__fecha__gt=first_day,
                                      check_in__fecha__lte=last_day)
    lista = []
    for book in bookings:
        pricedate_in = book.check_in
        price = pricedate_in.price
        pricedate_in = pricedate_in.fecha
        pricedate_out = book.check_out
        pricedate_out = pricedate_out.fecha

        lista.append(all_dates_between_dates(pricedate_in, pricedate_out))
    return lista


def check_availability(room, check_in, check_out):
    avail_list = []
    bookings_list = Booking.objects.filter(room=room)
    if len(bookings_list) > 0:
        for booking in bookings_list:
            pricedate = booking.check_in
            pricedate_out = booking.check_out
            pricedate_out = pricedate_out.fecha
            pricedate = pricedate.fecha
            print(avail_list)
            if pricedate > check_out or pricedate_out < check_in:
                avail_list.append(True)
            else:
                avail_list.append(False)
    else:
        avail_list = [True,]

    return all(avail_list) #all return True if all items are true (any) does the opposite