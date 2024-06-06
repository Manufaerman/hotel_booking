from ..views import Room
from django.urls import reverse

def get_room_list():
    room2 = Room.objects.all()[0]
    room_categories = dict(room2.ROOM_CATEGORIES)
    room_list = []
    for room in room_categories:
        room2 = room_categories.get(room)
        room_url = reverse('hotel:roomdetailview', kwargs={'category': room})
        room_list.append((room2, room_url))

    return room_list