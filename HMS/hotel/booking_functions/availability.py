import datetime
from ..models import Room, Booking, Price
from .save_many_prices import first_day_month, last_day_month, all_dates_between_dates


def total_price_booking(check_in, check_out, price):
    all_dates = len(all_dates_between_dates(check_in, check_out)) - 1
    return price * all_dates

def total_price_cleanings_current_month():
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

def total_month_bookings():
    first_day = first_day_month()
    last_day = last_day_month()
    bookings = Booking.objects.filter(check_in__gt=first_day,
                                      check_in__lt=last_day
                                      )
    datos = {}

    for book in bookings:
        datos[book.id] = {
            'check_in': book.check_in,
            'check_out': book.check_out,
            'price': book.price.price,
            'room': book.room,
            'all_dates_book': all_dates_between_dates(book.check_in, book.check_out)
        }
    list_prices = []
    for book in datos.keys():
        all_dates_books = datos[book].get('all_dates_book')
        room = datos[book].get('room')
        price_ = datos[book].get('price')

        for date in all_dates_books:
            price = Price.objects.get_or_create(room=room, price=price_, date_price=date)
            list_prices.append(price[0].price)

    return sum(list_prices)


def total_days_book_current_month():
    first_day = first_day_month()
    last_day = last_day_month()
    bookings = Booking.objects.filter(check_in__gt=first_day,
                                      check_in__lte=last_day)
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