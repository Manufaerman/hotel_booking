from django.db import models

# Create your models here.

class Room(models.Model):
    ROOM_CATEGORIES = {
        ('YAC', 'Double bedroom with AC'),
        ('NAC', 'Double bedroom with out AC'),
        ('ONE', '1 ROOMS whit AC'),
        ('TWO', '2 ROOMS whit out AC'),
        ('3AC', '3 ROOMS whit AC')
    }
    name = models.CharField(max_length=300)
    number = models.IntegerField()
    category = models.CharField(max_length=5, choices=ROOM_CATEGORIES)
    bed = models.IntegerField()
    capacity = models.IntegerField()

    def __str__(self):
        return f'{self.name} has {self.category} {self.bed} with capacity for {self.capacity}'


