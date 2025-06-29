from django.conf import settings
from django.urls import reverse, reverse_lazy
from datetime import timedelta, date, datetime
from django.db import models
from django.utils import timezone
from .booking_functions.dates_functions import all_dates_between_dates

class Habitacion(models.Model):
    BATHROOM = {
        ('ONE',
         'En suite'),
        ('TWO',
         'Compartido'),
    }
    BED = {
        ('ONE',
         'Doble'),
        ('TWO',
         'Simple'),
    }
    nombre = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=100, default='hola')
    subtitle = models.CharField(max_length=100, default='hola')
    capacity = models.IntegerField(default=1)
    tv = models.BooleanField(default=True)
    aire_acondicionado = models.BooleanField(default=False)
    calefaccion = models.BooleanField(default=True)
    bed = models.CharField(choices=BED, max_length=100, default='ONE')
    bathroom = models.CharField(choices=BATHROOM, max_length=100, default='ONE')
    share_kitchen = models.BooleanField(default=True)
    terrace = models.BooleanField(default=False)
    share_garden = models.BooleanField(default=True)
    descripcion = models.TextField(blank=True)
    image = models.ImageField(upload_to='img/room', default='img/room/default.jpg')
    image1 = models.ImageField(upload_to='img/room', default='img/room/default.jpg')
    image2 = models.ImageField(upload_to='img/room', default='img/room/default.jpg')
    gastos = models.BooleanField(default=True)
    price = models.IntegerField(db_default=500)

    def alquilada(self):
        return self.contratos.filter(fecha_fin__isnull=True).exists()

    def rendimiento_mensual_actual(self):
        contrato = self.contrato.filter(fecha_fin__isnull=True).first()
        return contrato.precio_mensual if contrato else 0

    def rendimiento_anual_estimado(self):
        contratos = self.contratos.all()
        total = 0
        for contrato in contratos:
            inicio =contrato.fecha_inicio
            fin = contrato.fecha_fin or date.today()
            meses = (fin.year - inicio.year) * 12 + (fin.month - inicio.month) + 1
            total += contrato.precio_mensual * meses
        return total

    def __str__(self):
        return self.nombre

class Inquilino(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    telefono = models.IntegerField()

    def __str__(self):
        return self.nombre

class ContratoAlquiler(models.Model):
    habitacion = models.ForeignKey(Habitacion, related_name='contratos', on_delete=models.CASCADE)
    inquilino = models.ForeignKey(Inquilino, related_name='contratos', on_delete=models.CASCADE)
    fecha_inicio = models.DateField(default=timezone.now)
    fecha_fin = models.DateField(null=True, blank=True)
    precio_mensual = models.DecimalField(max_digits=10, decimal_places=2)

    def Finalizar(self):
        self.activo = False
        self.save()

    def __str__(self):
        return f"{self.inquilino.nombre} alquila {self.habitacion.nombre} desde {self.fecha_inicio}"

class Room(models.Model):
    ROOM_CATEGORIES = {
        ('ONE', 'Disfruta de este moderno apartamento de un dormitorio, diseñado para ofrecer confort y estilo. Cuenta con aire acondicionado, una luminosa zona de estar y un baño totalmente equipado.\n Terraza privada ideal para relajarte o trabajar al aire libre.\n Ubicación estratégica, cerca del Aeropuerto de Madrid-Barajas y IFEMA. ¡Reserva tu estancia y vive Madrid con el máximo confort!'),
        ('TWO', 'Amplio y cómodo apartamento de dos dormitorios, ideal para estancias prolongadas. Su diseño moderno y funcional ofrece un ambiente acogedor con una luminosa zona de estar, cocina totalmente equipada y baño completo. Calefacción para el invierno. \n Ubicación estratégica, cerca del Aeropuerto de Madrid-Barajas y IFEMA, con excelentes conexiones al centro de la ciudad. ¡Reserva ahora y disfruta de Madrid con comodidad y estilo!'),
        ('3AC', 'Amplio y moderno apartamento de tres dormitorios, perfecto para familias o grupos. Su diseño elegante y funcional ofrece una luminosa sala de estar, cocina totalmente equipada y baño completo. \n  Aire acondicionado para un confort ideal todo el año. \n  Ubicación estratégica, con excelentes conexiones y todos los servicios cercanos ¡Reserva tu estancia y disfruta de la comodidad con estilo!')
    }
    aire_acondicionado = models.BooleanField(default=False)
    name = models.CharField(max_length=300)
    number = models.IntegerField()
    category = models.CharField(choices=ROOM_CATEGORIES, max_length=2000)
    bed = models.IntegerField()
    doble_bed = models.BooleanField(default=True)
    capacity = models.IntegerField()
    image = models.ImageField(upload_to='img/room', default='img/room/default.jpg')
    title = models.TextField(max_length=1000,default='hola', null=True, blank=True)
    description_image = models.TextField(max_length=1000, default='hola', null=True, blank=True)
    image1 = models.ImageField(upload_to='img/room', default='img/room/default.jpg',null=True, blank=True)
    title1 = models.TextField(max_length=1000, default='hola', null=True, blank=True)
    description_image1 = models.TextField(max_length=1000,default='hola', null=True, blank=True)
    image2 = models.ImageField(upload_to='img/room', default='img/room/default.jpg', null=True, blank=True)
    title2 = models.TextField(max_length=1000, default='hola', null=True, blank=True)
    description_image2 = models.TextField(max_length=1000,default='hola', null=True, blank=True)
    image3 = models.ImageField(upload_to='img/room', default='img/room/default.jpg', null=True, blank=True)
    image4 = models.ImageField(upload_to='img/room', default='img/room/default.jpg', null=True, blank=True)
    image5 = models.ImageField(upload_to='img/room', default='img/room/default.jpg', null=True, blank=True)
    image6 = models.ImageField(upload_to='img/room', default='img/room/default.jpg', null=True, blank=True)
    subtitle = models.CharField(max_length=300, default='hola')
    description = models.TextField(max_length=1000, default='hola')
    """
    air_conditioning = models.BooleanField()
    supletory_screen = models.BooleanField()
    double_bed = models.BooleanField()
    television = models.BooleanField()
    """



    def __str__(self):
        return f'{self.name}'

    def get_absolute_url(self):
        return reverse('hotel:roomandflats', args=[str(self.id)])





class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE,)
    check_in = models.DateField()
    check_out = models.DateField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
      return f'Reserva de {self.user} en {self.room} del {self.check_in} al {self.check_out}'


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





