import datetime

from django.urls import reverse

from ..booking_functions.dates_functions import all_dates_between_dates, first_day_month, last_day_month,\
list_days_month
from datetime import date, datetime
from ..models import Booking, Price, Room

def run(id=1):
    room2 = Room.objects.all()[0]
    room_categories = dict(room2.ROOM_CATEGORIES)
    room_list = []
    for room in room_categories:
        print(room)
        room2 = room_categories.get(room)
        room_url = reverse('hotel:roomdetailview', kwargs={'category': room})
        room_list.append((room2, room_url))

    print(room_list)








