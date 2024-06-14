from django.conf import settings
from django.urls import reverse, reverse_lazy
import datetime
from datetime import timedelta
from django.db import models
from .booking_functions.save_many_prices import all_dates_between_dates, first_day_month, last_day_month



class PriceDate(models.Model):
    price = models.IntegerField()
    fecha = models.DateField()


class Room(models.Model):
    ROOM_CATEGORIES = {
        ('YAC', 'Double bedroom with AC'),
        ('NAC', 'Double bedroom without AC'),
        ('ONE', '1 ROOM flat whit AC'),
        ('TWO', '2 ROOMS flat without AC'),
        ('3AC', '3 ROOMS flat whit AC')
    }
    name = models.CharField(max_length=300)
    number = models.IntegerField()
    category = models.CharField(max_length=3, choices=ROOM_CATEGORIES)
    bed = models.IntegerField()
    capacity = models.IntegerField()

    def __str__(self):
        return f'{self.name} has {self.category}whit {self.bed} bed and with capacity for {self.capacity}'

    def get_absolute_url(self):
        return reverse('roomlist', args=[str(self.id)])

class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE,)
    check_in = models.ForeignKey(PriceDate, on_delete=models.CASCADE, related_name='check_in')
    check_out = models.ForeignKey(PriceDate, on_delete=models.CASCADE, related_name='check_out')

    def __str__(self):
        return f'{self.user} has book {self.room} from {self.check_in} to {self.check_out}'

    def get_room_category(self):
        room_categories = dict(self.room.ROOM_CATEGORIES)
        room_categories = room_categories.get(self.room.category)
        return room_categories

    def get_cancel_booking_url(self):
        return reverse_lazy('hotel:cancelbookingview', args=[self.pk, ])



    def total_previous_month_price(self):
        string_date = datetime.date.today() - timedelta(weeks=4)
        string_date = string_date.month
        bookings = Booking.objects.filter(day__month=string_date)
        price_previus_month = sum(int(book.price.price) for book in bookings)

        return f' {price_previus_month} Euros'





