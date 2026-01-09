from django.contrib import admin
from django.contrib.auth.models import User, Group
from .models import Empleado, Cliente, Producto, Factura, DetalleFactura


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ['cedula', 'nombre', 'apellido', 'cargo', 'celular', 'activo']
    list_filter = ['cargo', 'activo']
    search_fields = ['cedula', 'nombre', 'apellido']


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['cedula', 'nombre', 'apellido', 'celular', 'correo', 'es_consumidor_final']
    list_filter = ['es_consumidor_final']
    search_fields = ['cedula', 'nombre', 'apellido']


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'marca', 'precio_unitario', 'stock', 'es_primera_necesidad', 'activo']
    list_filter = ['es_primera_necesidad', 'activo', 'marca']
    search_fields = ['codigo', 'nombre', 'marca']


class DetalleFacturaInline(admin.TabularInline):
    model = DetalleFactura
    extra = 0
    readonly_fields = ['total_linea']


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ['numero', 'cliente', 'empleado', 'fecha', 'total']
    list_filter = ['fecha', 'empleado']
    search_fields = ['numero', 'cliente__cedula', 'cliente__nombre']
    inlines = [DetalleFacturaInline]
    readonly_fields = ['numero', 'subtotal_sin_iva', 'subtotal_con_iva', 'valor_iva', 'total']


def crear_datos_iniciales():
    from decimal import Decimal

    grupo_admin, _ = Group.objects.get_or_create(name='Admin')
    grupo_cajero, _ = Group.objects.get_or_create(name='Cajero')

    if not User.objects.filter(username='admin').exists():
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@unimark.com',
            password='admin123'
        )
        admin_user.groups.add(grupo_admin)

    if not User.objects.filter(username='cajero').exists():
        cajero_user = User.objects.create_user(
            username='cajero',
            email='cajero@unimark.com',
            password='cajero123'
        )
        cajero_user.groups.add(grupo_cajero)

    empleados_data = [
        {
            'cedula': '1712345678',
            'nombre': 'Carlos',
            'apellido': 'Mendoza',
            'celular': '0991234567',
            'correo': 'carlos.mendoza@unimark.com',
            'cargo': 'administrativo'
        },
        {
            'cedula': '1723456789',
            'nombre': 'Maria',
            'apellido': 'Garcia',
            'celular': '0982345678',
            'correo': 'maria.garcia@unimark.com',
            'cargo': 'cajero'
        },
    ]

    for emp_data in empleados_data:
        if not Empleado.objects.filter(cedula=emp_data['cedula']).exists():
            empleado = Empleado.objects.create(**emp_data)
            if emp_data['cargo'] == 'cajero':
                try:
                    cajero_user = User.objects.get(username='cajero')
                    empleado.usuario = cajero_user
                    empleado.save()
                except User.DoesNotExist:
                    pass

    Cliente.get_consumidor_final()

    clientes_data = [
        {
            'cedula': '1701234567',
            'nombre': 'Juan',
            'apellido': 'Perez',
            'celular': '0998765432',
            'correo': 'juan.perez@email.com'
        },
        {
            'cedula': '1709876543',
            'nombre': 'Ana',
            'apellido': 'Lopez',
            'celular': '0987654321',
            'correo': 'ana.lopez@email.com'
        },
    ]

    for cli_data in clientes_data:
        if not Cliente.objects.filter(cedula=cli_data['cedula']).exists():
            Cliente.objects.create(**cli_data)

    productos_data = [
        {
            'codigo': 'ARR001',
            'nombre': 'Arroz Conejo 1kg',
            'descripcion': 'Arroz blanco de grano largo, ideal para todo tipo de preparaciones',
            'marca': 'Conejo',
            'precio_unitario': Decimal('1.25'),
            'stock': 100,
            'es_primera_necesidad': True
        },
        {
            'codigo': 'LEC001',
            'nombre': 'Leche Vita Entera 1L',
            'descripcion': 'Leche entera pasteurizada, rica en calcio y vitaminas',
            'marca': 'Vita',
            'precio_unitario': Decimal('1.10'),
            'stock': 80,
            'es_primera_necesidad': True
        },
        {
            'codigo': 'HUE001',
            'nombre': 'Huevos Indaves x12',
            'descripcion': 'Cubeta de 12 huevos frescos de gallina',
            'marca': 'Indaves',
            'precio_unitario': Decimal('2.50'),
            'stock': 50,
            'es_primera_necesidad': True
        },
        {
            'codigo': 'PAN001',
            'nombre': 'Pan Supan Familiar',
            'descripcion': 'Pan de molde blanco, paquete familiar de 500g',
            'marca': 'Supan',
            'precio_unitario': Decimal('1.80'),
            'stock': 40,
            'es_primera_necesidad': True
        },
        {
            'codigo': 'ACE001',
            'nombre': 'Aceite La Favorita 1L',
            'descripcion': 'Aceite vegetal de palma, ideal para freir',
            'marca': 'La Favorita',
            'precio_unitario': Decimal('2.75'),
            'stock': 60,
            'es_primera_necesidad': True
        },
        {
            'codigo': 'GAL001',
            'nombre': 'Galletas Oreo x6',
            'descripcion': 'Galletas de chocolate con relleno de crema, paquete de 6 unidades',
            'marca': 'Oreo',
            'precio_unitario': Decimal('1.50'),
            'stock': 45,
            'es_primera_necesidad': False
        },
        {
            'codigo': 'GAS001',
            'nombre': 'Coca Cola 500ml',
            'descripcion': 'Bebida gaseosa sabor cola, botella personal',
            'marca': 'Coca Cola',
            'precio_unitario': Decimal('0.85'),
            'stock': 120,
            'es_primera_necesidad': False
        },
        {
            'codigo': 'JAB001',
            'nombre': 'Jabon Dove Original',
            'descripcion': 'Jabon de tocador con crema humectante, barra de 90g',
            'marca': 'Dove',
            'precio_unitario': Decimal('1.20'),
            'stock': 70,
            'es_primera_necesidad': False
        },
        {
            'codigo': 'SHA001',
            'nombre': 'Shampoo Head & Shoulders 375ml',
            'descripcion': 'Shampoo anticaspa para cabello normal',
            'marca': 'Head & Shoulders',
            'precio_unitario': Decimal('5.50'),
            'stock': 35,
            'es_primera_necesidad': False
        },
        {
            'codigo': 'CHO001',
            'nombre': 'Chocolate Jet 50g',
            'descripcion': 'Barra de chocolate con leche, tamano personal',
            'marca': 'Jet',
            'precio_unitario': Decimal('0.75'),
            'stock': 90,
            'es_primera_necesidad': False
        },
    ]

    for prod_data in productos_data:
        if not Producto.objects.filter(codigo=prod_data['codigo']).exists():
            Producto.objects.create(**prod_data)

    print("Datos iniciales creados exitosamente.")
    print("Usuario Admin: admin / admin123")
    print("Usuario Cajero: cajero / cajero123")

