from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinValueValidator
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from decimal import Decimal

cedula_validator = RegexValidator(
    regex=r'^\d{10}$',
    message='La cedula debe tener exactamente 10 digitos numericos.'
)

CATEGORIAS_PRIMERA_NECESIDAD = [
    'arroz', 'pan', 'leche', 'huevos', 'aceite', 'azucar', 'sal', 'harina',
    'legumbres', 'frejol', 'lenteja', 'frutas', 'verduras', 'carne', 'pollo',
    'pescado', 'agua', 'medicinas', 'avena', 'fideos', 'atun', 'sardina'
]


class Persona(models.Model):
    cedula = models.CharField(
        max_length=10,
        unique=True,
        validators=[cedula_validator],
        verbose_name='Cedula'
    )
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    apellido = models.CharField(max_length=100, verbose_name='Apellido')
    celular = models.CharField(max_length=15, verbose_name='Numero de Celular')
    correo = models.EmailField(verbose_name='Correo Electronico')

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"


class Empleado(Persona):
    CARGO_CHOICES = [
        ('cajero', 'Cajero'),
        ('perchero', 'Perchero'),
        ('oficina', 'Oficina'),
        ('descarguero', 'Descarguero'),
        ('conserje', 'Conserje'),
        ('administrativo', 'Administrativo'),
        ('seguridad', 'Seguridad'),
        ('secretario', 'Secretario'),
    ]

    cargo = models.CharField(max_length=20, choices=CARGO_CHOICES, verbose_name='Cargo')
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Usuario del Sistema'
    )
    activo = models.BooleanField(default=True, verbose_name='Activo')
    fecha_ingreso = models.DateField(auto_now_add=True, verbose_name='Fecha de Ingreso')

    class Meta:
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'
        ordering = ['apellido', 'nombre']

    def __str__(self):
        return f"{self.nombre_completo} - {self.get_cargo_display()}"


class Cliente(Persona):
    es_consumidor_final = models.BooleanField(
        default=False,
        verbose_name='Es Consumidor Final'
    )
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Registro')

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['apellido', 'nombre']

    def __str__(self):
        if self.es_consumidor_final:
            return "Consumidor Final"
        return f"{self.nombre_completo}"

    @classmethod
    def get_consumidor_final(cls):
        cliente, created = cls.objects.get_or_create(
            cedula='9999999999',
            defaults={
                'nombre': 'Consumidor',
                'apellido': 'Final',
                'celular': '0000000000',
                'correo': 'consumidor@final.com',
                'es_consumidor_final': True
            }
        )
        return cliente


class Producto(models.Model):
    codigo = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Codigo Unico'
    )
    nombre = models.CharField(max_length=200, verbose_name='Nombre del Producto')
    descripcion = models.TextField(max_length=500, verbose_name='Descripcion')
    marca = models.CharField(max_length=100, verbose_name='Marca')
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Precio Unitario'
    )
    stock = models.PositiveIntegerField(default=0, verbose_name='Stock Disponible')
    es_primera_necesidad = models.BooleanField(
        default=False,
        verbose_name='Es Primera Necesidad (IVA 0%)'
    )
    activo = models.BooleanField(default=True, verbose_name='Activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    @property
    def tiene_stock(self):
        return self.stock > 0

    @property
    def iva_porcentaje(self):
        return Decimal('0') if self.es_primera_necesidad else Decimal('0.15')

    def calcular_precio_con_iva(self, cantidad=1):
        subtotal = self.precio_unitario * cantidad
        iva = subtotal * self.iva_porcentaje
        return subtotal + iva


class Factura(models.Model):
    numero = models.CharField(max_length=20, unique=True, verbose_name='Numero de Factura')
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        verbose_name='Cliente'
    )
    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.PROTECT,
        verbose_name='Empleado que factura'
    )
    fecha = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Emision')
    subtotal_sin_iva = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Subtotal Sin IVA'
    )
    subtotal_con_iva = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Subtotal Con IVA'
    )
    valor_iva = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Valor IVA (15%)'
    )
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total a Pagar'
    )

    class Meta:
        verbose_name = 'Factura'
        verbose_name_plural = 'Facturas'
        ordering = ['-fecha']

    def __str__(self):
        return f"Factura {self.numero} - {self.cliente}"

    def save(self, *args, **kwargs):
        if not self.numero:
            ultima = Factura.objects.order_by('-id').first()
            if ultima:
                ultimo_num = int(ultima.numero.split('-')[1])
                self.numero = f"FAC-{str(ultimo_num + 1).zfill(8)}"
            else:
                self.numero = "FAC-00000001"
        super().save(*args, **kwargs)

    def calcular_totales(self):
        detalles = self.detalles.all()

        self.subtotal_sin_iva = Decimal('0.00')
        self.subtotal_con_iva = Decimal('0.00')

        for detalle in detalles:
            if detalle.producto.es_primera_necesidad:
                self.subtotal_sin_iva += detalle.total_linea
            else:
                self.subtotal_con_iva += detalle.total_linea

        self.valor_iva = self.subtotal_con_iva * Decimal('0.15')
        self.subtotal_con_iva = self.subtotal_con_iva + self.valor_iva
        self.total = self.subtotal_sin_iva + self.subtotal_con_iva
        self.save()


class DetalleFactura(models.Model):
    factura = models.ForeignKey(
        Factura,
        on_delete=models.CASCADE,
        related_name='detalles',
        verbose_name='Factura'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        verbose_name='Producto'
    )
    cantidad = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Cantidad'
    )
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Precio Unitario'
    )
    total_linea = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Total Línea'
    )

    class Meta:
        verbose_name = 'Detalle de Factura'
        verbose_name_plural = 'Detalles de Factura'

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"

    def save(self, *args, **kwargs):
        self.total_linea = self.precio_unitario * self.cantidad
        super().save(*args, **kwargs)


@receiver(post_save, sender=DetalleFactura)
def reducir_stock(sender, instance, created, **kwargs):
    if created:
        producto = instance.producto
        producto.stock -= instance.cantidad
        producto.save()


@receiver(post_delete, sender=DetalleFactura)
def restaurar_stock(sender, instance, **kwargs):
    producto = instance.producto
    producto.stock += instance.cantidad
    producto.save()

