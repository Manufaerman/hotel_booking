from datetime import date, datetime, timedelta

from hotel.booking_functions.availability import total_month_bookings
from hotel.booking_functions.dates_functions import first_day_month_x, last_day_month_x, all_dates_between_dates
from hotel.models import Booking, Room, Price
from hotel.booking_functions.retrieving_data import booking_year_property, booking_month_allproperties


def run():
    check_in = "2024-10-25"
    check_out = '2024-11-28'





