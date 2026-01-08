from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinValueValidator
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from decimal import Decimal

# Validador para cédula ecuatoriana (10 dígitos)
cedula_validator = RegexValidator(
    regex=r'^\d{10}$',
    message='La cédula debe tener exactamente 10 dígitos numéricos.'
)

# Lista de categorías de productos de primera necesidad (IVA 0% en Ecuador)
CATEGORIAS_PRIMERA_NECESIDAD = [
    'arroz', 'pan', 'leche', 'huevos', 'aceite', 'azucar', 'sal', 'harina',
    'legumbres', 'frejol', 'lenteja', 'frutas', 'verduras', 'carne', 'pollo',
    'pescado', 'agua', 'medicinas', 'avena', 'fideos', 'atun', 'sardina'
]


class Persona(models.Model):
    """Clase base abstracta para Empleado y Cliente usando POO"""
    cedula = models.CharField(
        max_length=10,
        unique=True,
        validators=[cedula_validator],
        verbose_name='Cédula'
    )
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    apellido = models.CharField(max_length=100, verbose_name='Apellido')
    celular = models.CharField(max_length=15, verbose_name='Número de Celular')
    correo = models.EmailField(verbose_name='Correo Electrónico')

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"


class Empleado(Persona):
    """Modelo Empleado que hereda de Persona"""
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
    """Modelo Cliente que hereda de Persona"""
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
        """Obtiene o crea el cliente consumidor final"""
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
    """Modelo para productos del inventario"""
    codigo = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Código Único'
    )
    nombre = models.CharField(max_length=200, verbose_name='Nombre del Producto')
    descripcion = models.TextField(max_length=500, verbose_name='Descripción')
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
        """Retorna 0 si es primera necesidad, 15 si no"""
        return Decimal('0') if self.es_primera_necesidad else Decimal('0.15')

    def calcular_precio_con_iva(self, cantidad=1):
        """Calcula el precio total incluyendo IVA"""
        subtotal = self.precio_unitario * cantidad
        iva = subtotal * self.iva_porcentaje
        return subtotal + iva


class Factura(models.Model):
    """Modelo para las facturas"""
    numero = models.CharField(max_length=20, unique=True, verbose_name='Número de Factura')
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
    fecha = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Emisión')
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
            # Generar número de factura automático
            ultima = Factura.objects.order_by('-id').first()
            if ultima:
                ultimo_num = int(ultima.numero.split('-')[1])
                self.numero = f"FAC-{str(ultimo_num + 1).zfill(8)}"
            else:
                self.numero = "FAC-00000001"
        super().save(*args, **kwargs)

    def calcular_totales(self):
        """Recalcula todos los totales de la factura"""
        detalles = self.detalles.all()

        self.subtotal_sin_iva = Decimal('0.00')
        self.subtotal_con_iva = Decimal('0.00')

        for detalle in detalles:
            if detalle.producto.es_primera_necesidad:
                self.subtotal_sin_iva += detalle.total_linea
            else:
                self.subtotal_con_iva += detalle.total_linea

        # El subtotal_con_iva incluye el IVA 15% calculado
        self.valor_iva = self.subtotal_con_iva * Decimal('0.15')
        self.subtotal_con_iva = self.subtotal_con_iva + self.valor_iva  # Ya incluye IVA
        self.total = self.subtotal_sin_iva + self.subtotal_con_iva
        self.save()


class DetalleFactura(models.Model):
    """Modelo para los detalles/líneas de una factura"""
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
        # Calcular total de línea
        self.total_linea = self.precio_unitario * self.cantidad
        super().save(*args, **kwargs)


# Signals para manejar el stock
@receiver(post_save, sender=DetalleFactura)
def reducir_stock(sender, instance, created, **kwargs):
    """Reduce el stock del producto cuando se crea un detalle de factura"""
    if created:
        producto = instance.producto
        producto.stock -= instance.cantidad
        producto.save()


@receiver(post_delete, sender=DetalleFactura)
def restaurar_stock(sender, instance, **kwargs):
    """Restaura el stock si se elimina un detalle de factura"""
    producto = instance.producto
    producto.stock += instance.cantidad
    producto.save()

