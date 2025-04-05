from django.conf import settings
from django.urls import reverse, reverse_lazy
import datetime
from datetime import timedelta
from django.db import models

from .booking_functions.dates_functions import all_dates_between_dates



class Room(models.Model):
    ROOM_CATEGORIES = {
        ('YAC', 'Disfruta de una estancia cómoda y moderna en esta habitación con cama de matrimonio, ideal para profesionales y viajeros frecuentes. Equipada con calefacción y aire acondicionado, ofrece un ambiente acogedor durante todo el año. \n 📍Ubicación Ideal: A solo minutos del Aeropuerto de Madrid-Barajas y IFEMA, perfecta para estancias largas con excelente conexión a la ciudad.¡Reserva ahora y vive la comodidad en Madrid!'),
        ('NAC', 'Disfruta de una estancia cómoda y moderna en esta habitación con cama de matrimonio, ideal para profesionales y viajeros frecuentes. Equipada con calefacción, garantiza un ambiente acogedor en los meses más fríos. \n📍 Ubicación Ideal: A solo minutos del Aeropuerto de Madrid-Barajas y IFEMA, perfecta para estancias largas con excelente conexión a la ciudad.¡Reserva ahora y vive la comodidad en Madrid!'),
        ('ONE', 'Disfruta de este moderno apartamento de un dormitorio, diseñado para ofrecer confort y estilo. Cuenta con aire acondicionado, una luminosa zona de estar y un baño totalmente equipado.\n 🌿 Terraza privada ideal para relajarte o trabajar al aire libre.\n📍 Ubicación estratégica, cerca del Aeropuerto de Madrid-Barajas y IFEMA. ¡Reserva tu estancia y vive Madrid con el máximo confort!'),
        ('TWO', 'Amplio y cómodo apartamento de dos dormitorios, ideal para estancias prolongadas. Su diseño moderno y funcional ofrece un ambiente acogedor con una luminosa zona de estar, cocina totalmente equipada y baño completo. Calefacción para el invierno. \n📍 Ubicación estratégica, cerca del Aeropuerto de Madrid-Barajas y IFEMA, con excelentes conexiones al centro de la ciudad. ¡Reserva ahora y disfruta de Madrid con comodidad y estilo!'),
        ('3AC', 'Amplio y moderno apartamento de tres dormitorios, perfecto para familias o grupos. Su diseño elegante y funcional ofrece una luminosa sala de estar, cocina totalmente equipada y baño completo. \n ✅ Aire acondicionado para un confort ideal todo el año. \n 📍 Ubicación estratégica, con excelentes conexiones y todos los servicios cercanos ¡Reserva tu estancia y disfruta de la comodidad con estilo!')
    }
    name = models.CharField(max_length=300)
    number = models.IntegerField()
    category = models.CharField(choices=ROOM_CATEGORIES, max_length=2000)
    bed = models.IntegerField()
    capacity = models.IntegerField()
    image = models.ImageField(upload_to='img/room', default='img/room/default.jpg')
    image1 = models.ImageField(upload_to='img/room', default='img/room/default.jpg')
    image2 = models.ImageField(upload_to='img/room', default='img/room/default.jpg')
    subtitle = models.CharField(max_length=300, default='hola')
    description = models.TextField(max_length=1000, default='hola')

    def __str__(self):
        return f'{self.name}'

    def get_absolute_url(self):
        return reverse('hotel:roomandflats', args=[str(self.id)])




class Price(models.Model):
    price = models.IntegerField(null=True, blank=True)
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

    def total_bill_booking(self):
        all_dates = all_dates_between_dates(str(self.check_in),str(self.check_out))
        price = self.price

        return (int(len(all_dates))-1) * int(self.price.price)

    def check_in_date(self):
        return str(self.check_in.day)+'-' + str(self.check_in.month)+'-' + str(self.check_in.year)[2:]

    def check_out_date(self):
        return str(self.check_out.day)+'-' + str(self.check_in.month)+'-' + str(self.check_in.year)[2:]

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





