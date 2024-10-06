from django.conf import settings
from django.urls import reverse, reverse_lazy
import datetime
from datetime import timedelta
from django.db import models
from .signal import save_price_signal


class Room(models.Model):
    ROOM_CATEGORIES = {
        ('YAC', 'double room with air conditioning'),
        ('NAC', 'Double bedroom without air conditioning'),
        ('ONE', 'Design apartment of a room with air conditioning'),
        ('TWO', 'Full two bedroom apartment without air conditioning'),
        ('3AC', 'Full three bedroom apartment with air conditioning')
    }
    name = models.CharField(max_length=300)
    number = models.IntegerField()
    category = models.CharField(max_length=3, choices=ROOM_CATEGORIES)
    bed = models.IntegerField()
    capacity = models.IntegerField()
    image = models.ImageField(upload_to='img/room', default='img/room/default.jpg')
    image1 = models.ImageField(upload_to='img/room', default='img/room/default.jpg')
    image2 = models.ImageField(upload_to='img/room', default='img/room/default.jpg')

    def __str__(self):
        return f'{self.name}'

    def get_absolute_url(self):
        return reverse('hotel:roomandflats', args=[str(self.id)])




class Price(models.Model):
    price = models.IntegerField()
    date_price = models.DateField()
    room = models.ForeignKey(Room, on_delete=models.CASCADE)


class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE,)
    check_in = models.DateField()
    check_out = models.DateField()
    price = models.ForeignKey(Price, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.room}'

    def get_room_category(self):
        room_categories = dict(self.room.ROOM_CATEGORIES)
        room_categories = room_categories.get(self.room.category)
        return room_categories

    def get_cancel_booking_url(self):
        return reverse_lazy('hotel:cancelbookingview', args=[self.pk, ])


    # acabo de crear el sender para prices

    """def save_booking_prices(self):
        save_price_signal.send(sender=self.__class__, room=self.room, price=self.price,
                               check_in=self.check_in, check_out=self.check_out)"""





    def total_previous_month_price(self):
        string_date = datetime.date.today() - timedelta(weeks=4)
        string_date = string_date.month
        bookings = Booking.objects.filter(day__month=string_date)
        price_previus_month = sum(int(book.price.price) for book in bookings)

        return f' {price_previus_month} Euros'





