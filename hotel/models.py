from dateutil.relativedelta import relativedelta
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date
from django.utils.timezone import now
import uuid
from datetime import timedelta
import re
from django.utils import timezone
from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError
class Visit(models.Model):
    ip = models.GenericIPAddressField()

    path = models.CharField(
        max_length=200,
    )

    user_agent = models.TextField(
        blank=True,
    )

    timestamp = models.DateTimeField(
        default=now,
        db_index=True,
    )

    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    region = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    country = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    country_code = models.CharField(
        max_length=2,
        blank=True,
        null=True,
    )

    def __str__(self):
        location = ", ".join(
            part
            for part in [
                self.city,
                self.region,
                self.country,
            ]
            if part
        )

        return (
            f"{self.ip} - "
            f"{location or 'Ubicación desconocida'} - "
            f"{self.path}"
        )


class Flat(models.Model):
    ROOM_CATEGORIES = [
        ('ONE',
         'Disfruta de este moderno apartamento de un dormitorio, diseñado para ofrecer confort y estilo. Cuenta con aire acondicionado, una luminosa zona de estar y un baño totalmente equipado.\n Terraza privada ideal para relajarte o trabajar al aire libre.\n Ubicación estratégica, cerca del Aeropuerto de Madrid-Barajas y IFEMA. ¡Reserva tu estancia y vive Madrid con el máximo confort!'),
        ('TWO',
         'Amplio y cómodo apartamento de tres dormitorios, ideal para estancias prolongadas. Su diseño moderno y funcional ofrece un ambiente acogedor, cocina totalmente equipada y baño completo. Calefacción para el invierno. \n Ubicación estratégica, cerca del Aeropuerto de Madrid-Barajas y IFEMA, con excelentes conexiones al centro de la ciudad. ¡Reserva ahora y disfruta de Madrid con comodidad y estilo!'),
        ('3AC',
         'Amplio y moderno apartamento de tres dormitorios. Su diseño elegante y funcional ofrece una luminosa sala de estar, cocina totalmente equipada y baño completo. \n  Aire acondicionado para un confort ideal todo el año. \n  Ubicación estratégica, con excelentes conexiones y todos los servicios cercanos ¡Reserva tu estancia y disfruta de la comodidad con estilo!'),
        ('PLUS', 'Antigua casa española de carácter auténtico, rodeada por la calma de un jardín sencillo presidido por un olivo centenario. Sus dos cocinas y espacios luminosos la convierten en un lugar ideal tanto para el teletrabajo como para disfrutar de largas comidas al aire libre, en un ambiente sereno y acogedor de inspiración mediterránea.')
    ]
    TIPO_ALQUILER = [
        ('habitaciones', 'Alquiler por habitaciones'),
        ('completo', 'Alquiler piso completo')
    ]

    TIPO_REPARTO_GASTOS = [
        ("IGUAL", "A partes iguales"),
        ("POR_TIPO_HABITACION", "Según tipo de habitación"),
    ]

    reparto_gastos = models.CharField(
        max_length=30,
        choices=TIPO_REPARTO_GASTOS,
        default="IGUAL",
        verbose_name="Sistema de reparto de gastos"
    )

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
    BATHROOM = [
        ('ONE',
         'En suite'),
        ('TWO',
         'Compartido'),
    ]
    BED = [
        ('ONE',
         'Doble'),
        ('TWO',
         'Simple'),
    ]
    grupo_cocina = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="Grupo de cocina",
        help_text=(
            "Habitaciones con el mismo texto comparten cocina. "
            "Ejemplo: HARO_COCINA_1."
        ),
    )

    grupo_bano = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="Grupo de baño",
        help_text=(
            "Habitaciones con el mismo texto comparten baño. "
            "Ejemplo: HARO_BANO_PLANTA_BAJA."
        ),
    )

    propiedad = models.ForeignKey(Flat, related_name='habitaciones', null=True, blank=True, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=100, default='hola')
    subtitle = models.CharField(max_length=500, default='hola')
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
    image2 = models.ImageField(upload_to='img/room', default='img/room/default.jpg')
    image3 = models.ImageField(upload_to='img/room', default='img/room/default.jpg')
    image4 = models.ImageField(upload_to='img/room', default='img/room/default.jpg')
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


    @property
    def proceso_formalizacion_activo(self):
        return self.procesos_formalizacion.filter(
            estado__in=[
                "PENDIENTE",
                "INICIADO",
            ]
        ).order_by("-fecha_creacion").first()

    @property
    def contrato_activo(self):
        return self.contratos.filter(
            activo=True
        ).order_by("-fecha_inicio").first()

    @property
    def contrato_futuro(self):
        hoy = timezone.localdate()

        return self.contratos.filter(
            fecha_inicio__gt=hoy
        ).order_by("fecha_inicio").first()

    @property
    def estado_ocupacion(self):
        if self.contrato_activo:
            return "OCUPADA"

        if self.contrato_futuro:
            return "RESERVADA"

        return "LIBRE"

    def __str__(self):
        if self.propiedad:
            return f"{self.nombre} · {self.propiedad.nombre}"

        return self.nombre

    @property
    def otras_inquilinas_vivienda(self):
        if not self.propiedad_id:
            return 0

        return max(
            self.propiedad.habitaciones.count() - 1,
            0,
        )

    @property
    def otras_inquilinas_cocina(self):
        if not self.propiedad_id:
            return 0

        if self.grupo_cocina:
            return (
                Habitacion.objects
                .filter(
                    propiedad_id=self.propiedad_id,
                    grupo_cocina=self.grupo_cocina,
                )
                .exclude(pk=self.pk)
                .count()
            )

        # Si no definimos un grupo especial,
        # suponemos que todas comparten la misma cocina.
        return self.otras_inquilinas_vivienda

    @property
    def otras_inquilinas_bano(self):
        if not self.propiedad_id:
            return 0

        # Según tus choices actuales:
        # ONE = En suite
        # TWO = Compartido
        if self.bathroom != "TWO":
            return 0

        if self.grupo_bano:
            return (
                Habitacion.objects
                .filter(
                    propiedad_id=self.propiedad_id,
                    grupo_bano=self.grupo_bano,
                )
                .exclude(pk=self.pk)
                .count()
            )

        return self.otras_inquilinas_vivienda


class Inquilino(models.Model):
    user = models.OneToOneField(User,
                                on_delete=models.SET_NULL,
                                null=True, blank=True,
                                related_name='inquilino')
    nombre = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    dni = models.CharField(max_length=10, null=True,  blank=True)
    direccion = models.CharField(max_length=200, null=True, blank=True)
    telefono = models.CharField(
        max_length=25,
        null=True,
        blank=True,
        verbose_name="Teléfono / WhatsApp",
        help_text="Incluye el prefijo internacional, por ejemplo +34 o +57.",
    )
    nacionalidad = models.CharField(max_length=200, default='Española')

    @property
    def telefono_whatsapp(self):
        """
        Devuelve el teléfono en el formato exigido por WhatsApp:
        únicamente código de país y número, sin espacios ni +.
        """
        if not self.telefono:
            return ""

        telefono = self.telefono.strip()

        if telefono.startswith("00"):
            telefono = telefono[2:]

        return re.sub(r"\D", "", telefono)

    def __str__(self):
        return self.nombre


class ContratoAlquiler(models.Model):

    habitacion = models.ForeignKey(
        Habitacion,
        related_name="contratos",
        on_delete=models.CASCADE,
    )

    inquilino = models.ForeignKey(
        Inquilino,
        related_name="contratos",
        on_delete=models.CASCADE,
    )

    fecha_inicio = models.DateField(
        default=timezone.now,
    )

    fecha_fin = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de finalización",
    )

    precio_mensual = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    fianza = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
    )

    activo = models.BooleanField(
        default=True,
    )

    @property
    def tiene_aval(self):
        return hasattr(self, "aval")

    def save(self, *args, **kwargs):
        if self.fecha_inicio and not self.fecha_fin:
            self.fecha_fin = (
                    self.fecha_inicio
                    + relativedelta(months=6)
                    - timedelta(days=1)
            )

        super().save(*args, **kwargs)

        self.actualizar_disponibilidad_habitacion()

    def delete(self, *args, **kwargs):
        habitacion_id = self.habitacion_id

        resultado = super().delete(
            *args,
            **kwargs,
        )

        if habitacion_id:
            hay_contrato_activo = (
                ContratoAlquiler.objects
                .filter(
                    habitacion_id=habitacion_id,
                    activo=True,
                )
                .exists()
            )

            Habitacion.objects.filter(
                pk=habitacion_id
            ).update(
                disponible=not hay_contrato_activo
            )

        return resultado

    def actualizar_disponibilidad_habitacion(self):
        if not self.habitacion_id:
            return

        hay_contrato_activo = (
            ContratoAlquiler.objects
            .filter(
                habitacion_id=self.habitacion_id,
                activo=True,
            )
            .exists()
        )

        Habitacion.objects.filter(
            pk=self.habitacion_id
        ).update(
            disponible=not hay_contrato_activo
        )

    def finalizar(self):
        self.activo = False
        self.fecha_fin = timezone.localdate()

        self.save(
            update_fields=[
                "activo",
                "fecha_fin",
            ]
        )

    def __str__(self):
        return (
            f"{self.inquilino.nombre} alquila "
            f"{self.habitacion.nombre} desde "
            f"{self.fecha_inicio:%d/%m/%Y}"
        )


class AvalContrato(models.Model):
    contrato = models.OneToOneField(
        "ContratoAlquiler",
        on_delete=models.CASCADE,
        related_name="aval"
    )

    nombre_completo = models.CharField(max_length=150)
    dni_nie = models.CharField(max_length=20)
    domicilio = models.CharField(max_length=200, blank=True)


    def __str__(self):
        return f"Aval de {self.contrato}"


class Proyecto(models.Model):

    TIPOS = [
        ("aparthotel", "Aparthotel"),
        ("vivienda", "Vivienda"),
        ("reforma", "Reforma"),
        ("otro", "Otro"),
    ]

    ESTADOS = [
        ("planificacion", "Planificación"),
        ("desarrollo", "En desarrollo"),
        ("operativo", "Operativo"),
        ("pausado", "Pausado"),
        ("finalizado", "Finalizado"),
    ]

    PAISES = [
        ("ES", "España"),
        ("AR", "Argentina"),
    ]

    nombre = models.CharField(
        max_length=120,
    )

    pais = models.CharField(
        max_length=2,
        choices=PAISES,
    )

    ciudad = models.CharField(
        max_length=120,
        blank=True,
    )

    provincia = models.CharField(
        max_length=120,
        blank=True,
    )

    tipo = models.CharField(
        max_length=30,
        choices=TIPOS,
        default="otro",
    )

    estado = models.CharField(
        max_length=30,
        choices=ESTADOS,
        default="planificacion",
    )

    activo = models.BooleanField(
        default=True,
    )

    descripcion = models.TextField(
        blank=True,
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            "pais",
            "nombre",
        ]

        verbose_name = "Proyecto"
        verbose_name_plural = "Proyectos"

    def __str__(self):
        ubicacion = self.provincia or self.ciudad

        if ubicacion:
            return f"{self.nombre} · {ubicacion}"

        return self.nombre


class Gasto(models.Model):

    CATEGORIAS = [
        ("suministros", "Suministros"),
        ("comunidad", "Comunidad"),
        ("impuestos", "Impuestos y tasas"),
        ("reparaciones", "Reparaciones y mantenimiento"),
        ("mejoras", "Mejoras e inversión"),
        ("gestion", "Gestión y servicios profesionales"),
        ("gestion_remota", "Gestión remota"),
        ("hipotecas_seguros", "Hipotecas y seguros"),
        ("otros", "Otros"),
    ]

    TIPOS_SUMINISTRO = [
        ("electricidad", "Electricidad"),
        ("agua", "Agua"),
        ("gas", "Gas"),
        ("internet", "Internet"),
        ("telefonia", "Telefonía"),
        ("otros", "Otros suministros"),
    ]

    UNIDADES_CONSUMO = [
        ("kwh", "kWh"),
        ("m3", "m³"),
        ("litros", "Litros"),
        ("unidades", "Unidades"),
    ]

    PAISES = [
        ("ES", "España"),
        ("AR", "Argentina"),
    ]

    # Se conserva temporalmente para no romper vistas,
    # migraciones y movimientos históricos.
    TIPOS = [
        ("recurrente", "Recurrente"),
        ("extraordinario", "Extraordinario"),
        ("inversion", "Inversión"),
        ("gestion", "Gestión"),
    ]

    AMBITOS = [
        ("empresa", "Sociedad y gestión general"),
        ("propiedad", "Una propiedad"),
        ("proyecto", "Un proyecto"),
    ]

    DESTINOS_GESTORIA = [
        ("gestoria", "Enviar a gestoría"),
        ("interno", "Solo control interno"),
    ]

    MONEDAS = [
        ("EUR", "Euro"),
        ("ARS", "Peso argentino"),
    ]

    moneda = models.CharField(
        max_length=3,
        choices=MONEDAS,
        default="EUR",
    )

    cotizacion_usd = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True,
        help_text=(
            "Pesos argentinos equivalentes a un dólar."
        ),
    )

    importe_usd = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )

    fecha_cotizacion = models.DateField(
        null=True,
        blank=True,
    )

    fuente_cotizacion = models.CharField(
        max_length=120,
        blank=True,
    )

    pais = models.CharField(
        max_length=2,
        choices=PAISES,
        default="ES",
        db_index=True,
    )

    ambito = models.CharField(
        max_length=20,
        choices=AMBITOS,
        default="propiedad",
    )

    propiedad = models.ForeignKey(
        Flat,
        on_delete=models.PROTECT,
        related_name="gastos",
        null=True,
        blank=True,
    )

    habitacion = models.ForeignKey(
        Habitacion,
        on_delete=models.SET_NULL,
        related_name="gastos",
        null=True,
        blank=True,
    )

    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.SET_NULL,
        related_name="gastos",
        null=True,
        blank=True,
    )

    categoria = models.CharField(
        max_length=30,
        choices=CATEGORIAS,
        default="otros",
    )

    tipo_suministro = models.CharField(
        max_length=20,
        choices=TIPOS_SUMINISTRO,
        blank=True,
        verbose_name="Tipo de suministro",
    )

    consumo = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Consumo",
        help_text=(
            "Opcional. Permite analizar el consumo real "
            "de electricidad, agua o gas."
        ),
    )

    unidad_consumo = models.CharField(
        max_length=20,
        choices=UNIDADES_CONSUMO,
        blank=True,
        verbose_name="Unidad de consumo",
    )

    tipo = models.CharField(
        max_length=20,
        choices=TIPOS,
        default="extraordinario",
    )

    proveedor = models.CharField(
        max_length=150,
        blank=True,
    )

    concepto = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Descripción opcional",
        help_text=(
            "Añade una explicación solamente cuando "
            "la categoría y el proveedor no sean suficientes."
        ),
    )

    importe = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    fecha = models.DateField(
        default=timezone.localdate,
    )

    pagado = models.BooleanField(
        default=True,
    )

    destino_gestoria = models.CharField(
        max_length=20,
        choices=DESTINOS_GESTORIA,
        default="gestoria",
        verbose_name="Destino del justificante",
    )

    justificante = models.FileField(
        upload_to="gastos/justificantes/%Y/%m/",
        null=True,
        blank=True,
    )

    notas = models.TextField(
        blank=True,
    )

    gasto_recurrente = models.ForeignKey(
        "GastoRecurrente",
        on_delete=models.SET_NULL,
        related_name="gastos_generados",
        null=True,
        blank=True,
    )

    periodo_recurrente = models.DateField(
        null=True,
        blank=True,
        help_text=(
            "Primer día del periodo al que corresponde "
            "el gasto recurrente."
        ),
    )

    generado_automaticamente = models.BooleanField(
        default=False,
    )

    anulado = models.BooleanField(
        default=False,
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            "-fecha",
            "-fecha_creacion",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "gasto_recurrente",
                    "periodo_recurrente",
                ],
                condition=models.Q(
                    gasto_recurrente__isnull=False,
                    periodo_recurrente__isnull=False,
                ),
                name="gasto_recurrente_periodo_unico",
            ),
        ]

        indexes = [
            models.Index(
                fields=["fecha"],
            ),
            models.Index(
                fields=["pais", "fecha"],
            ),
            models.Index(
                fields=["propiedad", "fecha"],
            ),
            models.Index(
                fields=["habitacion", "fecha"],
            ),
            models.Index(
                fields=["proyecto", "fecha"],
            ),
            models.Index(
                fields=["categoria", "fecha"],
            ),
            models.Index(
                fields=["tipo_suministro", "fecha"],
            ),
            models.Index(
                fields=["tipo", "fecha"],
            ),
            models.Index(
                fields=["ambito", "fecha"],
            ),
            models.Index(
                fields=["pagado", "fecha"],
            ),
            models.Index(
                fields=["destino_gestoria", "fecha"],
            ),
            models.Index(
                fields=["anulado", "fecha"],
            ),
        ]

        verbose_name = "Gasto"
        verbose_name_plural = "Gastos"

    def clean(self):
        super().clean()

        errores = {}

        if (
            self.importe is not None
            and self.importe <= 0
        ):
            errores["importe"] = (
                "El importe debe ser superior a cero."
            )

        if self.ambito == "empresa":

            if self.propiedad_id:
                errores["propiedad"] = (
                    "Un gasto general no debe tener propiedad."
                )

            if self.habitacion_id:
                errores["habitacion"] = (
                    "Un gasto general no debe tener habitación."
                )

            if self.proyecto_id:
                errores["proyecto"] = (
                    "Un gasto general no debe tener proyecto."
                )

        elif self.ambito == "propiedad":

            if not self.propiedad_id:
                errores["propiedad"] = (
                    "Selecciona una propiedad."
                )

            if self.proyecto_id:
                errores["proyecto"] = (
                    "Un gasto de propiedad no debe tener proyecto."
                )

            if (
                self.habitacion_id
                and self.propiedad_id
                and self.habitacion.propiedad_id
                != self.propiedad_id
            ):
                errores["habitacion"] = (
                    "La habitación no pertenece a la propiedad."
                )

        elif self.ambito == "proyecto":

            if not self.proyecto_id:
                errores["proyecto"] = (
                    "Selecciona un proyecto."
                )

            if self.propiedad_id:
                errores["propiedad"] = (
                    "Un gasto de proyecto no debe tener propiedad."
                )

            if self.habitacion_id:
                errores["habitacion"] = (
                    "Un gasto de proyecto no debe tener habitación."
                )

            if (
                self.proyecto_id
                and self.proyecto.pais != self.pais
            ):
                errores["proyecto"] = (
                    "El proyecto no pertenece al país seleccionado."
                )

        else:
            errores["ambito"] = (
                "Selecciona el ámbito del gasto."
            )

        if self.categoria != "suministros":

            if self.tipo_suministro:
                errores["tipo_suministro"] = (
                    "El tipo de suministro solamente se utiliza "
                    "en la categoría Suministros."
                )

            if self.consumo is not None:
                errores["consumo"] = (
                    "El consumo solamente se utiliza "
                    "en gastos de suministros."
                )

            if self.unidad_consumo:
                errores["unidad_consumo"] = (
                    "La unidad solamente se utiliza "
                    "en gastos de suministros."
                )

        if (
            self.consumo is not None
            and self.consumo <= 0
        ):
            errores["consumo"] = (
                "El consumo debe ser superior a cero."
            )

        if (
            self.consumo is not None
            and not self.unidad_consumo
        ):
            errores["unidad_consumo"] = (
                "Selecciona la unidad del consumo."
            )

        if (
            self.unidad_consumo
            and self.consumo is None
        ):
            errores["consumo"] = (
                "Introduce el consumo correspondiente."
            )

        if (
            self.generado_automaticamente
            and not self.gasto_recurrente_id
        ):
            errores["gasto_recurrente"] = (
                "Un gasto generado automáticamente debe estar "
                "relacionado con un gasto recurrente."
            )

        if (
            self.gasto_recurrente_id
            and not self.periodo_recurrente
        ):
            errores["periodo_recurrente"] = (
                "Indica el periodo del gasto recurrente."
            )

        if errores:
            raise ValidationError(errores)

    @property
    def titulo(self):
        partes = []

        if self.proveedor:
            partes.append(self.proveedor)

        partes.append(
            self.get_categoria_display()
        )

        if self.tipo_suministro:
            partes.append(
                self.get_tipo_suministro_display()
            )

        if self.concepto:
            partes.append(self.concepto)

        return " · ".join(partes)

    @property
    def destino(self):
        if self.ambito == "empresa":
            return (
                f"{self.get_pais_display()} · "
                "Sociedad y gestión general"
            )

        if (
            self.ambito == "proyecto"
            and self.proyecto
        ):
            return (
                f"{self.get_pais_display()} · "
                f"{self.proyecto}"
            )

        if (
            self.ambito == "propiedad"
            and self.propiedad
        ):
            if self.habitacion:
                return (
                    f"{self.propiedad} · "
                    f"{self.habitacion}"
                )

            return str(self.propiedad)

        return "Sin asignar"

    @property
    def es_recurrente(self):
        return self.gasto_recurrente_id is not None

    def __str__(self):
        return (
            f"{self.titulo} · "
            f"{self.importe} €"
        )


class GastoRecurrente(models.Model):

    FRECUENCIAS = [
        ("mensual", "Mensual"),
        ("bimestral", "Cada dos meses"),
        ("trimestral", "Trimestral"),
        ("semestral", "Semestral"),
        ("anual", "Anual"),
    ]

    nombre = models.CharField(
        max_length=150,
    )

    pais = models.CharField(
        max_length=2,
        choices=Gasto.PAISES,
        default="ES",
        db_index=True,
    )

    ambito = models.CharField(
        max_length=20,
        choices=Gasto.AMBITOS,
        default="propiedad",
    )

    propiedad = models.ForeignKey(
        Flat,
        on_delete=models.PROTECT,
        related_name="gastos_recurrentes",
        null=True,
        blank=True,
    )

    habitacion = models.ForeignKey(
        Habitacion,
        on_delete=models.SET_NULL,
        related_name="gastos_recurrentes",
        null=True,
        blank=True,
    )

    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.SET_NULL,
        related_name="gastos_recurrentes",
        null=True,
        blank=True,
    )

    categoria = models.CharField(
        max_length=30,
        choices=Gasto.CATEGORIAS,
        default="otros",
    )

    tipo_suministro = models.CharField(
        max_length=20,
        choices=Gasto.TIPOS_SUMINISTRO,
        blank=True,
        verbose_name="Tipo de suministro",
    )

    # Se conserva temporalmente para compatibilidad
    # con las vistas existentes.
    tipo = models.CharField(
        max_length=20,
        choices=Gasto.TIPOS,
        default="recurrente",
    )

    importe = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    proveedor = models.CharField(
        max_length=150,
        blank=True,
    )

    concepto = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Descripción opcional",
    )

    frecuencia = models.CharField(
        max_length=20,
        choices=FRECUENCIAS,
        default="mensual",
    )

    dia_generacion = models.PositiveSmallIntegerField(
        default=1,
    )

    mes_generacion = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
    )

    fecha_inicio = models.DateField(
        default=timezone.localdate,
    )

    fecha_fin = models.DateField(
        null=True,
        blank=True,
    )

    pagado_por_defecto = models.BooleanField(
        default=True,
    )

    requiere_justificante = models.BooleanField(
        default=False,
    )

    destino_gestoria = models.CharField(
        max_length=20,
        choices=Gasto.DESTINOS_GESTORIA,
        default="gestoria",
    )

    activo = models.BooleanField(
        default=True,
    )

    notas = models.TextField(
        blank=True,
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            "-activo",
            "nombre",
        ]

        indexes = [
            models.Index(
                fields=["pais", "activo"],
            ),
            models.Index(
                fields=["propiedad", "activo"],
            ),
            models.Index(
                fields=["proyecto", "activo"],
            ),
            models.Index(
                fields=["categoria", "activo"],
            ),
            models.Index(
                fields=["tipo_suministro", "activo"],
            ),
        ]

        verbose_name = "Gasto recurrente"
        verbose_name_plural = "Gastos recurrentes"

    def clean(self):
        super().clean()

        errores = {}

        if (
                self.importe is not None
                and self.importe <= 0
        ):
            errores["importe"] = (
                "El importe habitual debe ser superior a cero."
            )

        if self.ambito == "empresa":
            if self.propiedad_id:
                errores["propiedad"] = (
                    "Un gasto general no debe tener propiedad."
                )

            if self.habitacion_id:
                errores["habitacion"] = (
                    "Un gasto general no debe tener habitación."
                )

            if self.proyecto_id:
                errores["proyecto"] = (
                    "Un gasto general no debe tener proyecto."
                )

        elif self.ambito == "propiedad":
            if not self.propiedad_id:
                errores["propiedad"] = (
                    "Selecciona una propiedad."
                )

            if self.proyecto_id:
                errores["proyecto"] = (
                    "Un gasto de propiedad no debe tener proyecto."
                )

            if (
                    self.habitacion_id
                    and self.propiedad_id
                    and self.habitacion.propiedad_id
                    != self.propiedad_id
            ):
                errores["habitacion"] = (
                    "La habitación no pertenece a la propiedad."
                )

        elif self.ambito == "proyecto":
            if not self.proyecto_id:
                errores["proyecto"] = (
                    "Selecciona un proyecto."
                )

            if self.propiedad_id:
                errores["propiedad"] = (
                    "Un gasto de proyecto no debe tener propiedad."
                )

            if self.habitacion_id:
                errores["habitacion"] = (
                    "Un gasto de proyecto no debe tener habitación."
                )

            if (
                    self.proyecto_id
                    and self.proyecto.pais != self.pais
            ):
                errores["proyecto"] = (
                    "El proyecto no pertenece al país seleccionado."
                )

        else:
            errores["ambito"] = (
                "Selecciona el ámbito del gasto recurrente."
            )

        if self.categoria == "suministros":
            if not self.tipo_suministro:
                errores["tipo_suministro"] = (
                    "Selecciona el tipo de suministro."
                )
        else:
            self.tipo_suministro = ""

        if (
                self.fecha_fin
                and self.fecha_inicio
                and self.fecha_fin < self.fecha_inicio
        ):
            errores["fecha_fin"] = (
                "La fecha final no puede ser anterior "
                "a la fecha de inicio."
            )

        if errores:
            raise ValidationError(errores)

    def save(self, *args, **kwargs):
        if not self.fecha_inicio:
            self.fecha_inicio = timezone.localdate()

        # La fecha inicial determina automáticamente cuándo se genera.
        self.dia_generacion = self.fecha_inicio.day

        if self.frecuencia == "anual":
            self.mes_generacion = self.fecha_inicio.month
        else:
            self.mes_generacion = None

        if self.categoria != "suministros":
            self.tipo_suministro = ""

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.nombre} · "
            f"{self.get_frecuencia_display()} · "
            f"{self.importe} €"
        )


class GastoPendiente(models.Model):

    ESTADOS = [
        ("pendiente", "Pendiente de completar"),
        ("completado", "Completado"),
        ("omitido", "Omitido"),
    ]

    gasto_recurrente = models.ForeignKey(
        GastoRecurrente,
        on_delete=models.CASCADE,
        related_name="pendientes",
    )

    periodo = models.DateField()

    fecha_programada = models.DateField()

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default="pendiente",
    )

    gasto_creado = models.OneToOneField(
        Gasto,
        on_delete=models.SET_NULL,
        related_name="origen_pendiente",
        null=True,
        blank=True,
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
    )

    fecha_completado = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = [
            "fecha_programada",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "gasto_recurrente",
                    "periodo",
                ],
                name="pendiente_recurrente_periodo_unico",
            ),
        ]

        verbose_name = "Gasto pendiente"
        verbose_name_plural = "Gastos pendientes"

    def __str__(self):
        return (
            f"{self.gasto_recurrente.nombre} · "
            f"{self.periodo:%m/%Y}"
        )


class Proveedor(models.Model):
    nombre = models.CharField(
        max_length=150,
        unique=True,
    )

    categoria_predeterminada = models.CharField(
        max_length=40,
        choices=Gasto.CATEGORIAS,
        blank=True,
    )

    activo = models.BooleanField(
        default=True,
    )

    def __str__(self):
        return self.nombre


class Iteminventario(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class Inventario(models.Model):
    habitacion = models.ForeignKey(Habitacion, on_delete=models.CASCADE)
    item = models.ForeignKey(Iteminventario, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    observaciones = models.CharField(max_length=200, blank=True)


class ProcesoFormalizacion(models.Model):

    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        INICIADO = "INICIADO", "En proceso"
        FORMALIZADO = "FORMALIZADO", "Formalizado"
        CADUCADO = "CADUCADO", "Caducado"
        CANCELADO = "CANCELADO", "Cancelado"

    class TipoPrimeraRenta(models.TextChoices):
        MES_COMPLETO = "MES_COMPLETO", "Mes completo"
        PROPORCIONAL = "PROPORCIONAL", "Parte proporcional"

    habitacion = models.ForeignKey(
        "Habitacion",
        on_delete=models.CASCADE,
        related_name="procesos_formalizacion",
        null=True,
        blank=True
    )

    inquilino = models.ForeignKey(
        "Inquilino",
        on_delete=models.CASCADE,
        related_name="procesos_formalizacion",
        null=True,
        blank=True,
    )

    contrato = models.OneToOneField(
        "ContratoAlquiler",
        on_delete=models.SET_NULL,
        related_name="proceso_formalizacion",
        null=True,
        blank=True,
    )

    token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )

    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
    )

    fecha_inicio = models.DateTimeField(
        null=True,
        blank=True,
    )

    fecha_limite = models.DateTimeField(
        null=True,
        blank=True,
    )

    fecha_inicio_contrato = models.DateField(
        null=True,
        blank=True,
    )

    duracion_meses = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    precio_mensual = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )

    fianza = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )

    tipo_primera_renta = models.CharField(
        max_length=20,
        choices=TipoPrimeraRenta.choices,
        default=TipoPrimeraRenta.PROPORCIONAL,
    )

    importe_primera_renta = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )

    contrato_descargado = models.BooleanField(
        default=False,
    )

    fecha_descarga = models.DateTimeField(
        null=True,
        blank=True,
    )

    contrato_firmado_recibido = models.BooleanField(
        default=False,
    )

    fecha_contrato_firmado = models.DateTimeField(
        null=True,
        blank=True,
    )

    fianza_recibida = models.BooleanField(
        default=False,
    )

    renta_recibida = models.BooleanField(
        default=False,
    )

    fecha_formalizacion = models.DateTimeField(
        null=True,
        blank=True,
    )

    observaciones = models.TextField(
        blank=True,
    )

    tiene_aval = models.BooleanField(
        default=False,
    )

    aval_nombre_completo = models.CharField(
        max_length=150,
        blank=True,
    )

    aval_dni_nie = models.CharField(
        max_length=20,
        blank=True,
    )

    aval_domicilio = models.CharField(
        max_length=200,
        blank=True,
    )

    @property
    def importe_total_inicial(self):
        if (
            self.importe_primera_renta is None
            or self.fianza is None
        ):
            return None

        return self.importe_primera_renta + self.fianza

    @property
    def esta_caducado(self):
        return (
            self.estado in {
                self.Estado.PENDIENTE,
                self.Estado.INICIADO,
            }
            and self.fecha_limite is not None
            and timezone.now() >= self.fecha_limite
        )

    @property
    def requisitos_completos(self):
        return (
            self.contrato_firmado_recibido
            and self.fianza_recibida
            and self.renta_recibida
        )

    def actualizar_estado(self):
        if self.estado in {
            self.Estado.CANCELADO,
            self.Estado.FORMALIZADO,
            self.Estado.CADUCADO,
        }:
            return

        if self.esta_caducado:
            self.estado = self.Estado.CADUCADO
            self.save(update_fields=["estado"])


    def __str__(self):
        habitacion = (
            self.habitacion.nombre
            if self.habitacion
            else "Sin habitación"
        )

        propiedad = (
            self.habitacion.propiedad.nombre
            if self.habitacion
               and self.habitacion.propiedad
            else "Sin propiedad"
        )

        inquilino = (
            str(self.inquilino)
            if self.inquilino
            else "Sin inquilino"
        )

        return (
            f"{habitacion} · {propiedad} · "
            f"{inquilino} · {self.get_estado_display()}"
        )


from django.db import models


class MultimediaHabitacion(models.Model):

    habitacion = models.ForeignKey(
        "Habitacion",
        on_delete=models.CASCADE,
        related_name="galeria",
    )

    imagen = models.ImageField(
        upload_to="habitaciones/galeria/imagenes/",
        null=True,
        blank=True,
    )

    video = models.FileField(
        upload_to="habitaciones/galeria/videos/",
        null=True,
        blank=True,
    )

    titulo = models.CharField(
        max_length=120,
        blank=True,
    )

    orden = models.PositiveIntegerField(
        default=0,
    )

    visible = models.BooleanField(
        default=True,
    )

    def clean(self):
        super().clean()

        if not self.imagen and not self.video:
            raise ValidationError(
                "Debes añadir una imagen o un vídeo."
            )

        if self.imagen and self.video:
            raise ValidationError(
                "Cada elemento debe contener una imagen o un vídeo, no ambos."
            )

        if self.video and self.video.size > 12 * 1024 * 1024:
            raise ValidationError({
                "video": "El vídeo no puede superar los 12 MB.",
            })

    @property
    def es_video(self):
        return bool(self.video)

    class Meta:
        ordering = ["orden", "pk"]
        verbose_name = "Elemento de galería"
        verbose_name_plural = "Galería de habitaciones"

    def __str__(self):
        tipo = "Vídeo" if self.video else "Imagen"

        return f"{self.habitacion.nombre} · {tipo} · {self.orden}"


class Planta(models.Model):

    ESTADOS = [
        ('activa', 'Actualmente en la vivienda'),
        ('fallecida', 'Fallecida'),
        ('retirada', 'Retirada'),
    ]

    habitacion = models.ForeignKey(
        'Habitacion',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='plantas'
    )

    piso = models.ForeignKey(
        'Flat',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='plantas'
    )

    nombre = models.CharField(
        max_length=100
    )

    especie = models.CharField(
        max_length=150,
        blank=True,
        help_text='Ej: Monstera deliciosa'
    )

    ubicacion = models.CharField(
        max_length=150,
        blank=True,
        help_text='Ej: Terraza, salón, entrada, junto a la ventana...'
    )

    descripcion = models.TextField(
        blank=True,
        help_text='Presentación o personalidad de la planta'
    )

    cuidados = models.TextField(
        blank=True,
        help_text='Indicaciones básicas de cuidado'
    )

    fecha_llegada = models.DateField(
        null=True,
        blank=True
    )

    fecha_fallecimiento = models.DateField(
        null=True,
        blank=True
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='activa'
    )

    generacion = models.PositiveIntegerField(
        default=1,
        help_text='Petra I, Petra II, Petra III...'
    )

    foto = models.ImageField(
        upload_to='plantas/',
        blank=True,
        null=True
    )

    slug = models.SlugField(
        unique=True,
        blank=True
    )

    publica = models.BooleanField(
        default=True
    )

    creada = models.DateTimeField(
        auto_now_add=True
    )

    actualizada = models.DateTimeField(
        auto_now=True
    )

    def clean(self):
        if self.habitacion and self.piso:
            raise ValidationError(
                'La planta debe pertenecer a una habitación o a un piso, no a ambos.'
            )

        if not self.habitacion and not self.piso:
            raise ValidationError(
                'La planta debe pertenecer a una habitación o a un piso.'
            )

    def save(self, *args, **kwargs):
        self.full_clean()

        if not self.slug:
            base = slugify(self.nombre)
            slug = base
            contador = 2

            while Planta.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{contador}'
                contador += 1

            self.slug = slug

        super().save(*args, **kwargs)

    @property
    def nombre_completo(self):
        numeros_romanos = {
            1: 'I',
            2: 'II',
            3: 'III',
            4: 'IV',
            5: 'V',
            6: 'VI',
            7: 'VII',
            8: 'VIII',
            9: 'IX',
            10: 'X',
        }

        numero = numeros_romanos.get(
            self.generacion,
            str(self.generacion)
        )

        return f'{self.nombre} {numero}'

    @property
    def lugar(self):
        if self.habitacion:
            return self.habitacion

        if self.piso:
            return self.piso

        return None

    @property
    def es_compartida(self):
        return bool(self.piso)

    def __str__(self):
        if self.habitacion:
            return f'{self.nombre_completo} · {self.habitacion}'

        if self.piso:
            return f'{self.nombre_completo} · {self.piso}'

        return self.nombre_completo


class EventoPlanta(models.Model):

    TIPOS = [
        ('llegada', 'Llegada'),
        ('estancia', 'Estancia'),
        ('incidente', 'Incidente'),
        ('fallecimiento', 'Fallecimiento'),
        ('reemplazo', 'Reemplazo'),
        ('otro', 'Otro'),
    ]

    planta = models.ForeignKey(
        Planta,
        on_delete=models.CASCADE,
        related_name='eventos'
    )

    tipo = models.CharField(
        max_length=30,
        choices=TIPOS,
        default='otro'
    )

    fecha = models.DateField(
        null=True,
        blank=True
    )

    titulo = models.CharField(
        max_length=200
    )

    descripcion = models.TextField(
        blank=True
    )

    publico = models.BooleanField(
        default=True
    )

    creado = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['-fecha', '-creado']

    def __str__(self):
        return f'{self.planta.nombre_completo}: {self.titulo}'


class ComentarioPlanta(models.Model):

    planta = models.ForeignKey(
        Planta,
        on_delete=models.CASCADE,
        related_name='comentarios'
    )

    nombre = models.CharField(
        max_length=120
    )

    mensaje = models.TextField()

    fecha_inicio_estancia = models.DateField(
        null=True,
        blank=True
    )

    fecha_fin_estancia = models.DateField(
        null=True,
        blank=True
    )

    foto = models.ImageField(
        upload_to='plantas/comentarios/',
        blank=True,
        null=True
    )

    aprobado = models.BooleanField(
        default=False
    )

    creado = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['-creado']

    def __str__(self):
        return f'{self.nombre} · {self.planta.nombre_completo}'

class Proveedor(models.Model):

    PAISES = [
        ("ES", "España"),
        ("AR", "Argentina"),
    ]

    nombre = models.CharField(
        max_length=150,
    )

    pais = models.CharField(
        max_length=2,
        choices=PAISES,
        default="ES",
        db_index=True,
    )

    activo = models.BooleanField(
        default=True,
        db_index=True,
    )

    class Meta:
        ordering = [
            "pais",
            "nombre",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "pais",
                    "nombre",
                ],
                name="proveedor_unico_por_pais",
            ),
        ]

        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"

    def __str__(self):
        return (
            f"{self.nombre} · "
            f"{self.get_pais_display()}"
        )

class PartidaProyecto(models.Model):

    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name="partidas",
    )

    nombre = models.CharField(
        max_length=150,
    )

    presupuesto_usd = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    descripcion = models.TextField(
        blank=True,
    )

    activa = models.BooleanField(
        default=True,
    )

    orden = models.PositiveIntegerField(
        default=0,
    )

    class Meta:
        ordering = [
            "orden",
            "nombre",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "proyecto",
                    "nombre",
                ],
                name=(
                    "partida_unica_por_proyecto"
                ),
            ),
        ]

        verbose_name = (
            "Partida presupuestaria"
        )

        verbose_name_plural = (
            "Partidas presupuestarias"
        )

    def __str__(self):
        return (
            f"{self.proyecto.nombre} · "
            f"{self.nombre}"
        )

class IngresoPropiedad(models.Model):

    propiedad = models.ForeignKey(
        Flat,
        on_delete=models.CASCADE,
        related_name="ingresos",
    )

    concepto = models.CharField(
        max_length=150,
        blank=True,
    )

    importe = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    fecha = models.DateField(
        default=timezone.localdate,
    )

    pagador = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Nombre o referencia del pagador",
    )

    notas = models.TextField(
        blank=True,
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            "-fecha",
            "-fecha_creacion",
        ]

        verbose_name = "Ingreso de propiedad"
        verbose_name_plural = "Ingresos de propiedades"

        indexes = [
            models.Index(
                fields=[
                    "propiedad",
                    "fecha",
                ],
            ),
        ]

    def clean(self):
        super().clean()

        if (
            self.importe is not None
            and self.importe <= 0
        ):
            raise ValidationError(
                {
                    "importe": (
                        "El importe debe ser "
                        "superior a cero."
                    ),
                }
            )

    def __str__(self):
        concepto = (
            self.concepto
            or "Ingreso"
        )

        return (
            f"{self.propiedad} · "
            f"{concepto} · "
            f"{self.importe} €"
        )