import datetime
import os
import calendar
from hotel.booking_functions.dates_functions import first_day_month_x, last_day_month_x, all_dates_between_dates, list_days_month
from hotel.models import Booking, Price
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "HMS.settings")

from datetime import date, datetime, timedelta


def run(id: str, month: str = str(date.month)):
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



mes = '02'
run(mes)










