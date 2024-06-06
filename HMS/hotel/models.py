from django.db import models
from django.conf import settings
from django.urls import reverse, reverse_lazy
from datetime import date, timedelta
# Create your models here.

class Room(models.Model):
    ROOM_CATEGORIES = {
        ('YAC', 'Double bedroom with AC'),
        ('NAC', 'Double bedroom with out AC'),
        ('ONE', '1 ROOM flat whit AC'),
        ('TWO', '2 ROOMS flat whit out AC'),
        ('3AC', '3 ROOMS flat whit AC')
    }
    name = models.CharField(max_length=300)
    number = models.IntegerField()
    category = models.CharField(max_length=3, choices=ROOM_CATEGORIES)
    bed = models.IntegerField()
    capacity = models.IntegerField()

    def __str__(self):
        return f'{self.name} has {self.category}whit {self.bed} bed and with capacity for {self.capacity}'

class Price(models.Model):
    day = models.DateField()
    price = models.IntegerField()

    def total_price(self, check_in, check_out):
        total_price = 0
        return total_price

class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE,)
    price = models.ForeignKey(Price, on_delete=models.CASCADE,)
    day = models.DateField(default='2024-07-01')
    check_in = models.DateField()
    check_out = models.DateField()

    def __str__(self):
        return f'{self.user} has book {self.room} from {self.check_in} to {self.check_out}'

    def get_room_category(self):
        room_categories = dict(self.room.ROOM_CATEGORIES)
        room_categories = room_categories.get(self.room.category)
        return room_categories

    def get_cancel_booking_url(self):
        return reverse_lazy('hotel:cancelbookingview', args=[self.pk,])


class day(models.Model):
    day = models.IntegerField(max_length=33)
    month = models.IntegerField(max_length=13)
    year =models.IntegerField(max_length=3000)
