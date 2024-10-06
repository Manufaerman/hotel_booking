from datetime import date

from hotel.booking_functions.availability import total_month_bookings
from hotel.booking_functions.dates_functions import first_day_month_x, last_day_month_x, all_dates_between_dates
from hotel.models import Booking, Room, Price
from hotel.booking_functions.retrieving_data import booking_year_property, booking_month_allproperties


def run( year: int = 2023):
    months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    prices = []
    for month in months:
        bookings = booking_month_allproperties(month=month)
        prices.append(bookings)

    print(prices)




run()
