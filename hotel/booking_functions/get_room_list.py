from ..views import Room
from django.urls import reverse
"""
def get_room_list():

    room2 = Room.objects.all()[0]
    room_categories = dict(room2.ROOM_CATEGORIES)
    room_list = []
    for room in room_categories:
        properties = Room.objects.filter(category=room)[0]
        room2 = room_categories.get(room)
        room_url = reverse('hotel:roomdetailview', kwargs={'category': room})
        room_list.append((properties, room2, room_url))

    return room_list
"""
def get_room_list():
    try:
        first_room = Room.objects.first()
        if not first_room:
            return []

        room_categories = dict(first_room.ROOM_CATEGORIES)
        room_list = []

        for category in room_categories:
            properties = Room.objects.filter(category=category).first()
            if not properties:
                continue  # salta si no hay ninguna habitación en esa categoría

            room_name = room_categories.get(category)
            room_url = reverse('hotel:roomdetailview', kwargs={'category': category})
            room_list.append((properties, room_name, room_url))

        return room_list
    except Exception as e:
        print(f"Error en get_room_list: {e}")
        return []