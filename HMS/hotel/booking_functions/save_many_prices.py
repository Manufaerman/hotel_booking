import datetime
from ..models import Price, Booking
from datetime import timedelta
import calendar


def save_price(check_in, check_out, price):
    date_list = [(check_in + timedelta(days=d)).strftime("%Y-%m-%d") for d in range((check_out.day - check_in.day) + 1)]
    list_objects = []
    for d in date_list:
        x = Price.objects.create(
            day=d,
            price=price
        )
        x.save()
        list_objects.append(x)
    return list_objects

# required import from datetime import timedelta
def all_date_between_dates(check_in, check_out):

    date_list = [(check_in + timedelta(days=d)).strftime("%Y-%m-%d") for d in range((check_out.day - check_in.day) + 1)]

    return date_list

def total_actual_month_price():
    string_date = datetime.date.today()
    bookings = Booking.objects.filter(day__month=string_date.month)

    price = sum(int(book.price.price) for book in bookings)


    return f' {price} Euros'

def total_previous_month_price():
    string_date = datetime.date.today()-timedelta(weeks=4)
    string_date = string_date.month
    bookings = Booking.objects.filter(day__month=string_date)
    price = sum(int(book.price.price) for book in bookings)

    return f' {price} Euros'

def list_days_month():
    string_date = datetime.date.today()
    bookings = Booking.objects.filter(day__month=string_date.month)
    actual_day = string_date.day-1
    start_month = string_date - timedelta(actual_day)
    res = calendar.monthrange(string_date.year, string_date.month)[1]
    end_month = start_month + timedelta(res-1)
    lis_of_dates = all_date_between_dates(start_month, end_month)


    return lis_of_dates

def list_true_false_calendar(data):
    days_month = list_days_month()
    booking_objects = Booking.objects.filter(room__id=data)
    print(booking_objects)
    string_bookings_days = [repr(book.day).strip('<Day: >') for book in booking_objects]
    string_bookings_days = [datetime.datetime.strptime(b, '%Y-%m-%d') for b in string_bookings_days]
    string_bookings_days = [b.strftime('%Y-%m-%d') for b in string_bookings_days]
    lista = []
    for b in days_month:
        if b in string_bookings_days:
            print(string_bookings_days)
            lista.append(True)
        else:
            lista.append(False)

    return lista