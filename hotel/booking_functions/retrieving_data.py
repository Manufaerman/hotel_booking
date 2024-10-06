from datetime import date

from .availability import total_month_bookings
from ..models import Booking, Room


def booking_year_property(room_id: int = 1, year: int = 2023):
    bookings = Booking.objects.filter(check_in__year=year).filter(room=room_id)
    dates = []
    prices = []
    data = {}
    for book in bookings:
        dates.append(book.check_in.month)
        prices.append(book.price.price)

    data['labels'] = dates
    data['prices'] = prices
    return data


def multiple_year_property(room_id: int = 1, year: int = 2023):
    rooms = Room.objects.all()
    data = {}
    for room in rooms:
        set = booking_year_property(room_id, year)
        set = set['prices']
        data[room.name] = set
    return data


def booking_monthandyear_property(room_id: int = 1, year: int = 2023, month=date.today().month):
    bookings = Booking.objects.filter(check_in__year=2023).filter(room=2).filter(check_in__month=month)

    prices = []
    for book in bookings:
        prices.append(book.price.price)

    prices = sum(prices)

    return prices


"""
devuelve el total de dinero recaudado en un mes concreto sumando todas las propiedades
del MES en el que estamos
"""


def booking_month_allproperties(year: int = 2023, month=date.today().month):
    bookings = Booking.objects.filter(check_in__year=2023).filter(check_in__month=month)

    prices = []
    for book in bookings:
        prices.append(book.price.price)

    prices = sum(prices)

    return prices


"""
devuelve una lista con la facturqacion total de cada mes del año corriente
"""


def all_month_all_properties():
    total_year = []
    months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    for month in months:
        mes = total_month_bookings(month)
        total_year.append(mes)

    return total_year

"""
devuelve una lista con la facturqacion total de cada mes del año 2023
"""
def all_month_properties_past():
    months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    prices = []
    for month in months:
        bookings = booking_month_allproperties(month=month)
        prices.append(bookings)

    return prices