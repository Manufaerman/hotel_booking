from django.db import models
from django.conf import settings

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


class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()

    def __str__(self):
        return f'{self.user} has book {self.room} from {self.check_in} to {self.check_out}'
