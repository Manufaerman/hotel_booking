from ..views import Room
from ..models import Price
from datetime import timedelta


def save_price(check_in, check_out, price):
    date_list = [(check_in + timedelta(days=d)).strftime("%Y-%m-%d") for d in range((check_out.day - check_in.day) + 1)]
    list_dates = []
    for d in date_list:
        x = Price.objects.create(
            day=d,
            price=price
        )
        x.save()
    return 'You are doing great !'

# required import from datetime import timedelta
def all_date_between_dates(check_in, check_out):

    date_list = [(check_in + timedelta(days=d)).strftime("%Y-%m-%d") for d in range((check_out.day - check_in.day) + 1)]

    return date_list