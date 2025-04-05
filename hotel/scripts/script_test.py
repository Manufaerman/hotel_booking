from datetime import date, datetime, timedelta

from django.urls import reverse

from hotel.booking_functions.availability import total_month_bookings
from hotel.booking_functions.dates_functions import first_day_month_x, last_day_month_x, all_dates_between_dates
from hotel.models import Booking, Room, Price
from hotel.booking_functions.retrieving_data import booking_year_property, booking_month_allproperties


def run():
    room2 = Room.objects.all()[0]
    room_categories = dict(room2.ROOM_CATEGORIES)
    print(room_categories, 'room categorias')
    room_list = []
    counter = 0
    for room in room_categories:
        properties = Room.objects.filter(category=room)[0]
        room2 = room_categories.get(room)
        room_url = reverse('hotel:roomdetailview', kwargs={'category': room})
        room_list.append((room, room2, room_url,))
        print(properties.capacity)
    return properties





