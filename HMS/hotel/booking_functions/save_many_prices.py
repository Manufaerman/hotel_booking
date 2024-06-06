import calendar
import datetime

from ..views import Room
from ..models import Price, Booking
from datetime import timedelta


def save_price(check_in, check_out, price):
    date_list = [(check_in + timedelta(days=d)).strftime("%Y-%m-%d") for d in range((check_out.day - check_in.day) + 1)]
    list_dates = []
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

def total_month_price():
    string_date = '2024-06-08'
    check_out = '2024-06-08'
    check_in = datetime.datetime.strptime(string_date,"%Y-%m-%d" )
    current_month_start = check_in.day-1
    current_month_start = check_in - timedelta(current_month_start)

    experimento = calendar.monthrange(check_in.year, check_in.month)[1]
    experimento = experimento-1

    current_month_end = current_month_start + timedelta(experimento)


    #objeto = [(check_in + timedelta(days=d)).strftime("%Y-%m-%d") for d in range((check_out.day - check_in.day) + 1)]
    today = datetime.datetime.now()
    month = today.month
    return f' from {current_month_start} to {current_month_end}'