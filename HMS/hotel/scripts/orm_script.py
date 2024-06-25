import datetime

from django.urls import reverse
import calendar
from dateutil.relativedelta import relativedelta

from ..booking_functions.availability import total_month_bookings, total_days_book_and_not_book_current_month
from ..booking_functions.dates_functions import all_dates_between_dates, first_day_month, last_day_month,\
list_days_month
from datetime import date, datetime, timedelta
from ..models import Booking, Price, Room

def run(id=1):
    first_day = first_day_month()
    last_day = last_day_month()
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

    print(res)








