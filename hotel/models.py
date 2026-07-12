from dateutil.relativedelta import relativedelta
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date
from django.db import models
from django.utils import timezone
from django.utils.timezone import now


class Visit(models.Model):
    ip = models.GenericIPAddressField()
    path = models.CharField(max_length=200)
    user_agent = models.TextField()
    timestamp = models.DateTimeField(default=now)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.ip} - {self.city}, {self.country} - {self.path}"


class Flat(models.Model):
    ROOM_CATEGORIES = {
        ('ONE',
         'Disfruta de este moderno apartamento de un dormitorio, diseñado para ofrecer confort y estilo. Cuenta con aire acondicionado, una luminosa zona de estar y un baño totalmente equipado.\n Terraza privada ideal para relajarte o trabajar al aire libre.\n Ubicación estratégica, cerca del Aeropuerto de Madrid-Barajas y IFEMA. ¡Reserva tu estancia y vive Madrid con el máximo confort!'),
        ('TWO',
         'Amplio y cómodo apartamento de dos dormitorios, ideal para estancias prolongadas. Su diseño moderno y funcional ofrece un ambiente acogedor con una luminosa zona de estar, cocina totalmente equipada y baño completo. Calefacción para el invierno. \n Ubicación estratégica, cerca del Aeropuerto de Madrid-Barajas y IFEMA, con excelentes conexiones al centro de la ciudad. ¡Reserva ahora y disfruta de Madrid con comodidad y estilo!'),
        ('3AC',
         'Amplio y moderno apartamento de tres dormitorios. Su diseño elegante y funcional ofrece una luminosa sala de estar, cocina totalmente equipada y baño completo. \n  Aire acondicionado para un confort ideal todo el año. \n  Ubicación estratégica, con excelentes conexiones y todos los servicios cercanos ¡Reserva tu estancia y disfruta de la comodidad con estilo!'),
        ('PLUS', 'Antigua casa española de carácter auténtico, rodeada por la calma de un jardín sencillo presidido por un olivo centenario. Sus dos cocinas y espacios luminosos la convierten en un lugar ideal tanto para el teletrabajo como para disfrutar de largas comidas al aire libre, en un ambiente sereno y acogedor de inspiración mediterránea.')
    }
    TIPO_ALQUILER = {
        ('habitaciones', 'Alquiler por habitaciones'),
        ('completo', 'Alquiler piso completo')
    }
    tipo_alquiler = models.CharField(choices=TIPO_ALQUILER, default='habitaciones', max_length=20,)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    descripcion_contrato = models.TextField(max_length=1000, null=True, blank=True, default='compuesta por 3 habitaciones numeradas del 1 al 3, un cuarto de baño, cocina y zonas comunes')
    aire_acondicionado = models.BooleanField(default=False)
    nombre = models.CharField(max_length=300)
    toilet = models.IntegerField(default='1')
    category = models.CharField(choices=ROOM_CATEGORIES, max_length=2000)
    dimensiones = models.IntegerField(default=90)
    wifi = models.BooleanField(default=True)
    television = models.BooleanField(default=True)
    capacity = models.IntegerField()
    cocina = models.ImageField(upload_to='img/room', default='img/room/default.jpg')
    cocina_title = models.TextField(max_length=1000, default='hola', null=True, blank=True)
    cocina_description = models.TextField(max_length=1000, default='hola', null=True, blank=True)
    wc = models.ImageField(upload_to='img/room', default='img/room/default.jpg', null=True, blank=True)
    wc_title = models.TextField(max_length=1000, default='hola', null=True, blank=True)
    wc_description = models.TextField(max_length=1000, default='hola', null=True, blank=True)
    terraza = models.ImageField(upload_to='img/room', default='img/room/default.jpg', null=True, blank=True)
    terraza_title = models.TextField(max_length=1000, default='hola', null=True, blank=True)
    terraza_descripcion = models.TextField(max_length=1000, default='hola', null=True, blank=True)
    image3 = models.ImageField(upload_to='img/room', default='img/room/default.jpg', null=True, blank=True)
    image4 = models.ImageField(upload_to='img/room', default='img/room/default.jpg', null=True, blank=True)
    image5 = models.ImageField(upload_to='img/room', default='img/room/default.jpg', null=True, blank=True)
    image6 = models.ImageField(upload_to='img/room', default='img/room/default.jpg', null=True, blank=True)
    subtitle = models.CharField(max_length=300, default='Estamos trabajando aquí')
    description = models.TextField(max_length=1000, default='Estamos trabajando aquí')



    def __str__(self):
        return f'{self.nombre}'

    def get_absolute_url(self):
        return reverse('hotel:roomandflats', args=[str(self.id)])

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
    propiedad = models.ForeignKey(Flat, related_name='habitaciones', null=True, blank=True, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=100, default='hola')
    subtitle = models.CharField(max_length=100, default='hola')
    capacity = models.IntegerField(default=1)
    tv = models.BooleanField(default=True)
    metros = models.CharField(default=10, max_length=50)
    aire_acondicionado = models.BooleanField(default=False)
    calefaccion = models.BooleanField(default=True)
    bed = models.CharField(choices=BED, max_length=100, default='ONE')
    armario = models.BooleanField(default=True)
    escritorio = models.BooleanField(default=True)
    disponible = models.BooleanField(db_default=False)
    bathroom = models.CharField(choices=BATHROOM, max_length=100, default='No')
    share_kitchen = models.BooleanField(default=True)
    terrace = models.BooleanField(default=False)
    share_garden = models.BooleanField(default=True)
    descripcion = models.TextField(blank=True)
    image = models.ImageField(upload_to='img/room', default='img/room/default.jpg')
    image1 = models.ImageField(upload_to='img/room', default='img/room/default.jpg')
    image_armario = models.ImageField(upload_to='img/room', default='img/room/default.jpg')
    precio = models.IntegerField(db_default=500)

    def alquilada(self):
        return self.contratos.filter(fecha_fin__isnull=True).exists()

    def rendimiento_mensual_actual(self):
        contrato = self.contrato.filter(fecha_fin__isnull=True).first()
        return contrato.precio_mensual if contrato else 0

    def rendimiento_anual_estimado(self):
        contratos = self.contratos.all()
        total = 0
        for contrato in contratos:
            inicio = contrato.fecha_inicio
            fin = contrato.fecha_fin or date.today()
            meses = (fin.year - inicio.year) * 12 + (fin.month - inicio.month) + 1
            total += contrato.precio_mensual * meses
        return total

    def __str__(self):
        return self.nombre

class Inquilino(models.Model):
    user = models.OneToOneField(User,
                                on_delete=models.SET_NULL,
                                null=True, blank=True,
                                related_name='inquilino')
    nombre = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    dni = models.CharField(max_length=10, null=True,  blank=True)
    direccion = models.CharField(max_length=200, null=True, blank=True)
    telefono = models.IntegerField(null=True,  blank=True)
    nacionalidad = models.CharField(max_length=200, default='Española')

    def __str__(self):
        return self.nombre





class ContratoAlquiler(models.Model):
    habitacion = models.ForeignKey(Habitacion, related_name='contratos', on_delete=models.CASCADE)
    inquilino = models.ForeignKey(Inquilino, related_name='contratos', on_delete=models.CASCADE)
    fecha_inicio = models.DateField(default=timezone.now)
    fecha_fin = models.DateField(null=True, blank=True)
    precio_mensual = models.DecimalField(max_digits=10, decimal_places=2)
    fianza = models.DecimalField(max_digits=6, decimal_places=2, null=True,  blank=True)
    activo = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.fecha_inicio and not self.fecha_fin:
            self.fecha_fin = self.fecha_inicio + relativedelta(month=6)
        super().save(*args, **kwargs)


    def finalizar(self):
        self.activo = False
        self.fecha_fin = timezone.now().date()
        self.save()

    def __str__(self):
        return f"{self.inquilino.nombre} alquila {self.habitacion.nombre} desde {self.fecha_inicio}"



class Gasto(models.Model):

    CATEGORIAS = [
        ("limpieza", "Limpieza"),
        ("suministros", "Suministros"),
        ("reparacion", "Reparación"),
        ("mobiliario", "Mobiliario"),
        ("comunidad", "Comunidad"),
        ("impuestos", "Impuestos"),
        ("otros", "Otros"),
    ]

    propiedad = models.ForeignKey(
        Flat,
        on_delete=models.CASCADE,
        related_name="gastos"
    )

    habitacion = models.ForeignKey(
        Habitacion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="gastos"
    )

    concepto = models.CharField(max_length=150)

    categoria = models.CharField(
        max_length=30,
        choices=CATEGORIAS,
        default="otros"
    )

    importe = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    fecha = models.DateField(default=timezone.now)

    pagado = models.BooleanField(default=False)

    notas = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.propiedad} - {self.concepto} - {self.importe} €"




