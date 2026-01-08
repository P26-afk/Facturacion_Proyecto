from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from App.models import Empleado, Cliente, Producto
from decimal import Decimal


class Command(BaseCommand):
    help = 'Carga los datos iniciales para el sistema Unimark'

    def handle(self, *args, **options):
        self.stdout.write('Creando datos iniciales para Unimark...')

        # Crear grupos
        grupo_admin, _ = Group.objects.get_or_create(name='Admin')
        grupo_cajero, _ = Group.objects.get_or_create(name='Cajero')
        self.stdout.write(self.style.SUCCESS('✓ Grupos creados'))

        # Crear usuario admin si no existe
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@unimark.com',
                password='admin123'
            )
            admin_user.groups.add(grupo_admin)
            self.stdout.write(self.style.SUCCESS('✓ Usuario admin creado (admin/admin123)'))
        else:
            self.stdout.write('- Usuario admin ya existe')

        # Crear usuario cajero si no existe
        cajero_user = None
        if not User.objects.filter(username='cajero').exists():
            cajero_user = User.objects.create_user(
                username='cajero',
                email='cajero@unimark.com',
                password='cajero123'
            )
            cajero_user.groups.add(grupo_cajero)
            self.stdout.write(self.style.SUCCESS('✓ Usuario cajero creado (cajero/cajero123)'))
        else:
            cajero_user = User.objects.get(username='cajero')
            self.stdout.write('- Usuario cajero ya existe')

        # Crear empleados
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
                'nombre': 'María',
                'apellido': 'García',
                'celular': '0982345678',
                'correo': 'maria.garcia@unimark.com',
                'cargo': 'cajero'
            },
        ]

        for emp_data in empleados_data:
            if not Empleado.objects.filter(cedula=emp_data['cedula']).exists():
                empleado = Empleado.objects.create(**emp_data)
                if emp_data['cargo'] == 'cajero' and cajero_user:
                    empleado.usuario = cajero_user
                    empleado.save()
                self.stdout.write(self.style.SUCCESS(f'✓ Empleado {emp_data["nombre"]} creado'))
            else:
                self.stdout.write(f'- Empleado {emp_data["nombre"]} ya existe')

        # Crear cliente consumidor final
        Cliente.get_consumidor_final()
        self.stdout.write(self.style.SUCCESS('✓ Consumidor Final creado'))

        # Crear algunos clientes de prueba
        clientes_data = [
            {
                'cedula': '1701234567',
                'nombre': 'Juan',
                'apellido': 'Pérez',
                'celular': '0998765432',
                'correo': 'juan.perez@email.com'
            },
            {
                'cedula': '1709876543',
                'nombre': 'Ana',
                'apellido': 'López',
                'celular': '0987654321',
                'correo': 'ana.lopez@email.com'
            },
        ]

        for cli_data in clientes_data:
            if not Cliente.objects.filter(cedula=cli_data['cedula']).exists():
                Cliente.objects.create(**cli_data)
                self.stdout.write(self.style.SUCCESS(f'✓ Cliente {cli_data["nombre"]} creado'))
            else:
                self.stdout.write(f'- Cliente {cli_data["nombre"]} ya existe')

        # Crear productos (5 primera necesidad IVA 0%, 5 con IVA 15%)
        productos_data = [
            # Primera necesidad (IVA 0%)
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
                'descripcion': 'Aceite vegetal de palma, ideal para freír',
                'marca': 'La Favorita',
                'precio_unitario': Decimal('2.75'),
                'stock': 60,
                'es_primera_necesidad': True
            },
            # Con IVA 15%
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
                'nombre': 'Jabón Dove Original',
                'descripcion': 'Jabón de tocador con crema humectante, barra de 90g',
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
                'descripcion': 'Barra de chocolate con leche, tamaño personal',
                'marca': 'Jet',
                'precio_unitario': Decimal('0.75'),
                'stock': 90,
                'es_primera_necesidad': False
            },
        ]

        for prod_data in productos_data:
            if not Producto.objects.filter(codigo=prod_data['codigo']).exists():
                Producto.objects.create(**prod_data)
                iva = "0%" if prod_data['es_primera_necesidad'] else "15%"
                self.stdout.write(self.style.SUCCESS(f'✓ Producto {prod_data["nombre"]} creado (IVA {iva})'))
            else:
                self.stdout.write(f'- Producto {prod_data["nombre"]} ya existe')

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('¡Datos iniciales cargados exitosamente!'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write('')
        self.stdout.write('Credenciales de acceso:')
        self.stdout.write(self.style.WARNING('  Admin: admin / admin123'))
        self.stdout.write(self.style.WARNING('  Cajero: cajero / cajero123'))
        self.stdout.write('')

