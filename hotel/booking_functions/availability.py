import datetime
from ..models import Room, Booking, Price
from .dates_functions import first_day_month_x, last_day_month_x, all_dates_between_dates,\
    list_days_month, first_day_month, last_day_month
from datetime import date
from dateutil.relativedelta import relativedelta
from icecream import ic


def total_price_booking(check_in, check_out, price):
    all_dates = len(all_dates_between_dates(check_in, check_out)) - 1
    return price * all_dates


def total_price_cleanings_current_month(month='0' + str(date.today().month)):
    first_day = first_day_month_x(month)
    last_day = last_day_month_x(month)
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
def total_month_bookings(month: str = '0' + str(date.today().month)):
    x = 1
    first_day = first_day_month_x(month)
    last_day = last_day_month_x(month)
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


def previus_month_bookings(month='0' + str(date.today().month)):
    first_day = first_day_month_x(month)
    last_day = last_day_month_x(month)
    last_day = last_day + relativedelta(months=-1)
    first_day = first_day + relativedelta(months=-1)
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

        for day in all_dates_books:
            price = Price.objects.get_or_create(room=room, price=price_, date_price=day)
            list_prices.append(price[0].price)

    return sum(list_prices)


#working  --->
def total_days_book_and_not_book_current_month(id: str, month: str = str(date.today().month)):
    first_day = first_day_month_x(month)
    last_day = last_day_month_x(month)
    bookings = Booking.objects.filter(check_in__gt=first_day,
                                      check_in__lte=last_day,
                                      room__id=id, )

    book_not_book_and_price = {}
    for book in bookings:
        dates = all_dates_between_dates(book.check_in, book.check_out)
        for day in dates:
            print(day)
            price = Price.objects.get(date_price=day, room__id=id, price=book.price.price)
            book_not_book_and_price[date.strftime(price.date_price, '%Y-%m-%d')] = price.price


    month_days = list_days_month()

    for day in month_days:
        if day not in book_not_book_and_price:
            try:
                prices = Price.objects.get(date_price=day,
                                           room__id=id)
                print(prices)
                book_not_book_and_price[day] = prices.price, False

            except Price.DoesNotExist:
                book_not_book_and_price[day] = 0, False

            # to check if what its return
            except Price.MultipleObjectsReturned:
                pass

    res = dict(sorted(book_not_book_and_price.items()))
    res = {x[8:]: z for x, z in sorted(res.items())}
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
    if len(month)<1:
        month = '0'+month
        first_day = first_day_month_x(month)
        last_day = last_day_month_x(month)
        bookings = Booking.objects.filter(check_in__gt=first_day,
                                          check_in__lte=last_day,
                                          room__id=id, )
        return bookings
    else:
        first_day = first_day_month_x(month)
        last_day = last_day_month_x(month)
        bookings = Booking.objects.filter(check_in__gt=first_day,
                                          check_in__lte=last_day,
                                          room__id=id, )

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
