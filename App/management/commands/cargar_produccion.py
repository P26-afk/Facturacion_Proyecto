import random
import string
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from App.models import Empleado, Cliente, Producto
from decimal import Decimal


def generar_codigo_unico(prefijo, longitud=6):
    """Genera un codigo unico aleatorio para productos"""
    caracteres = string.ascii_uppercase + string.digits
    while True:
        codigo = prefijo + ''.join(random.choices(caracteres, k=longitud))
        if not Producto.objects.filter(codigo=codigo).exists():
            return codigo


class Command(BaseCommand):
    help = 'Carga datos de produccion para el sistema Unimark'

    def handle(self, *args, **options):
        self.stdout.write('=' * 60)
        self.stdout.write('CARGANDO DATOS DE PRODUCCION PARA UNIMARK')
        self.stdout.write('=' * 60)

        # Crear grupos
        grupo_admin, _ = Group.objects.get_or_create(name='Admin')
        grupo_cajero, _ = Group.objects.get_or_create(name='Cajero')
        self.stdout.write(self.style.SUCCESS('[OK] Grupos creados'))

        # ============== USUARIOS ==============
        self.stdout.write('\n--- CREANDO USUARIOS ---')

        # Usuario administrador
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@unimark.com',
                password='Admin2024*',
                first_name='Administrador',
                last_name='Sistema'
            )
            admin_user.groups.add(grupo_admin)
            self.stdout.write(self.style.SUCCESS('[OK] Usuario admin creado'))

        # Usuarios cajeros
        cajeros_usuarios = [
            {'username': 'cajero1', 'email': 'cajero1@unimark.com', 'password': 'Cajero2024*', 'first_name': 'Maria', 'last_name': 'Garcia'},
            {'username': 'cajero2', 'email': 'cajero2@unimark.com', 'password': 'Cajero2024*', 'first_name': 'Carlos', 'last_name': 'Lopez'},
            {'username': 'cajero3', 'email': 'cajero3@unimark.com', 'password': 'Cajero2024*', 'first_name': 'Ana', 'last_name': 'Martinez'},
        ]

        usuarios_cajero = []
        for cajero_data in cajeros_usuarios:
            if not User.objects.filter(username=cajero_data['username']).exists():
                user = User.objects.create_user(**cajero_data)
                user.groups.add(grupo_cajero)
                usuarios_cajero.append(user)
                self.stdout.write(self.style.SUCCESS(f'[OK] Usuario {cajero_data["username"]} creado'))
            else:
                usuarios_cajero.append(User.objects.get(username=cajero_data['username']))

        # ============== EMPLEADOS ==============
        self.stdout.write('\n--- CREANDO EMPLEADOS ---')

        empleados_data = [
            # Administrativos
            {'cedula': '1712345678', 'nombre': 'Roberto', 'apellido': 'Sanchez Vera', 'celular': '0991234567', 'correo': 'roberto.sanchez@unimark.com', 'cargo': 'administrativo'},
            {'cedula': '1723456789', 'nombre': 'Patricia', 'apellido': 'Mora Jimenez', 'celular': '0982345678', 'correo': 'patricia.mora@unimark.com', 'cargo': 'administrativo'},
            # Cajeros
            {'cedula': '1734567890', 'nombre': 'Maria', 'apellido': 'Garcia Ortiz', 'celular': '0973456789', 'correo': 'maria.garcia@unimark.com', 'cargo': 'cajero'},
            {'cedula': '1745678901', 'nombre': 'Carlos', 'apellido': 'Lopez Ruiz', 'celular': '0964567890', 'correo': 'carlos.lopez@unimark.com', 'cargo': 'cajero'},
            {'cedula': '1756789012', 'nombre': 'Ana', 'apellido': 'Martinez Vega', 'celular': '0955678901', 'correo': 'ana.martinez@unimark.com', 'cargo': 'cajero'},
            # Percheros
            {'cedula': '1767890123', 'nombre': 'Luis', 'apellido': 'Fernandez Castro', 'celular': '0946789012', 'correo': 'luis.fernandez@unimark.com', 'cargo': 'perchero'},
            {'cedula': '1778901234', 'nombre': 'Sofia', 'apellido': 'Ramirez Ponce', 'celular': '0937890123', 'correo': 'sofia.ramirez@unimark.com', 'cargo': 'perchero'},
            # Descargueros
            {'cedula': '1789012345', 'nombre': 'Jorge', 'apellido': 'Torres Mendez', 'celular': '0928901234', 'correo': 'jorge.torres@unimark.com', 'cargo': 'descarguero'},
            {'cedula': '1790123456', 'nombre': 'Miguel', 'apellido': 'Herrera Luna', 'celular': '0919012345', 'correo': 'miguel.herrera@unimark.com', 'cargo': 'descarguero'},
            # Seguridad
            {'cedula': '1701234567', 'nombre': 'Pedro', 'apellido': 'Gomez Salazar', 'celular': '0990123456', 'correo': 'pedro.gomez@unimark.com', 'cargo': 'seguridad'},
            {'cedula': '1702345678', 'nombre': 'Andres', 'apellido': 'Vargas Pineda', 'celular': '0981234567', 'correo': 'andres.vargas@unimark.com', 'cargo': 'seguridad'},
            # Conserje
            {'cedula': '1703456789', 'nombre': 'Rosa', 'apellido': 'Delgado Moran', 'celular': '0972345678', 'correo': 'rosa.delgado@unimark.com', 'cargo': 'conserje'},
            # Secretario
            {'cedula': '1704567890', 'nombre': 'Carmen', 'apellido': 'Reyes Aguirre', 'celular': '0963456789', 'correo': 'carmen.reyes@unimark.com', 'cargo': 'secretario'},
            # Oficina
            {'cedula': '1705678901', 'nombre': 'Fernando', 'apellido': 'Castillo Bravo', 'celular': '0954567890', 'correo': 'fernando.castillo@unimark.com', 'cargo': 'oficina'},
        ]

        for i, emp_data in enumerate(empleados_data):
            if not Empleado.objects.filter(cedula=emp_data['cedula']).exists():
                empleado = Empleado.objects.create(**emp_data)
                # Asignar usuarios a cajeros
                if emp_data['cargo'] == 'cajero' and i - 2 < len(usuarios_cajero):
                    empleado.usuario = usuarios_cajero[i - 2]
                    empleado.save()
                self.stdout.write(self.style.SUCCESS(f'[OK] Empleado {emp_data["nombre"]} {emp_data["apellido"]} - {emp_data["cargo"]}'))

        # ============== CLIENTES ==============
        self.stdout.write('\n--- CREANDO CLIENTES ---')

        # Cliente consumidor final
        Cliente.get_consumidor_final()
        self.stdout.write(self.style.SUCCESS('[OK] Consumidor Final creado'))

        clientes_data = [
            {'cedula': '1711111111', 'nombre': 'Juan', 'apellido': 'Perez Alvarado', 'celular': '0998765432', 'correo': 'juan.perez@email.com'},
            {'cedula': '1722222222', 'nombre': 'Laura', 'apellido': 'Gonzalez Rios', 'celular': '0987654321', 'correo': 'laura.gonzalez@email.com'},
            {'cedula': '1733333333', 'nombre': 'Ricardo', 'apellido': 'Mendoza Cruz', 'celular': '0976543210', 'correo': 'ricardo.mendoza@email.com'},
            {'cedula': '1744444444', 'nombre': 'Diana', 'apellido': 'Suarez Paredes', 'celular': '0965432109', 'correo': 'diana.suarez@email.com'},
            {'cedula': '1755555555', 'nombre': 'Oscar', 'apellido': 'Rojas Espinoza', 'celular': '0954321098', 'correo': 'oscar.rojas@email.com'},
            {'cedula': '1766666666', 'nombre': 'Gabriela', 'apellido': 'Flores Nunez', 'celular': '0943210987', 'correo': 'gabriela.flores@email.com'},
            {'cedula': '1777777777', 'nombre': 'Eduardo', 'apellido': 'Silva Guerrero', 'celular': '0932109876', 'correo': 'eduardo.silva@email.com'},
            {'cedula': '1788888888', 'nombre': 'Valentina', 'apellido': 'Morales Lara', 'celular': '0921098765', 'correo': 'valentina.morales@email.com'},
            {'cedula': '1799999999', 'nombre': 'Alejandro', 'apellido': 'Castro Rivas', 'celular': '0910987654', 'correo': 'alejandro.castro@email.com'},
            {'cedula': '1700000001', 'nombre': 'Camila', 'apellido': 'Ortega Campos', 'celular': '0909876543', 'correo': 'camila.ortega@email.com'},
            {'cedula': '1700000002', 'nombre': 'Sebastian', 'apellido': 'Navarro Solis', 'celular': '0998765431', 'correo': 'sebastian.navarro@email.com'},
            {'cedula': '1700000003', 'nombre': 'Daniela', 'apellido': 'Romero Paz', 'celular': '0987654320', 'correo': 'daniela.romero@email.com'},
            {'cedula': '1700000004', 'nombre': 'Nicolas', 'apellido': 'Medina Ceron', 'celular': '0976543209', 'correo': 'nicolas.medina@email.com'},
            {'cedula': '1700000005', 'nombre': 'Isabella', 'apellido': 'Herrera Zambrano', 'celular': '0965432108', 'correo': 'isabella.herrera@email.com'},
            {'cedula': '1700000006', 'nombre': 'Mateo', 'apellido': 'Vargas Coronel', 'celular': '0954321097', 'correo': 'mateo.vargas@email.com'},
        ]

        for cli_data in clientes_data:
            if not Cliente.objects.filter(cedula=cli_data['cedula']).exists():
                Cliente.objects.create(**cli_data)
                self.stdout.write(self.style.SUCCESS(f'[OK] Cliente {cli_data["nombre"]} {cli_data["apellido"]}'))

        # ============== PRODUCTOS ==============
        self.stdout.write('\n--- CREANDO PRODUCTOS ---')

        # PRODUCTOS DE PRIMERA NECESIDAD (IVA 0%)
        productos_primera_necesidad = [
            # ARROZ
            {'nombre': 'Arroz Conejo 1kg', 'descripcion': 'Arroz blanco grano largo premium', 'marca': 'Conejo', 'precio': '1.25', 'stock': 200},
            {'nombre': 'Arroz Conejo 2kg', 'descripcion': 'Arroz blanco grano largo premium', 'marca': 'Conejo', 'precio': '2.45', 'stock': 150},
            {'nombre': 'Arroz Gustadina 1kg', 'descripcion': 'Arroz blanco seleccionado', 'marca': 'Gustadina', 'precio': '1.15', 'stock': 180},
            {'nombre': 'Arroz Rey 1kg', 'descripcion': 'Arroz blanco economico', 'marca': 'Rey', 'precio': '1.05', 'stock': 220},
            {'nombre': 'Arroz Integral 500g', 'descripcion': 'Arroz integral nutritivo', 'marca': 'Naturandes', 'precio': '1.80', 'stock': 80},

            # LECHE
            {'nombre': 'Leche Vita Entera 1L', 'descripcion': 'Leche entera pasteurizada', 'marca': 'Vita', 'precio': '1.10', 'stock': 300},
            {'nombre': 'Leche Vita Descremada 1L', 'descripcion': 'Leche descremada pasteurizada', 'marca': 'Vita', 'precio': '1.15', 'stock': 150},
            {'nombre': 'Leche Rey Entera 1L', 'descripcion': 'Leche entera UHT', 'marca': 'Rey Leche', 'precio': '1.05', 'stock': 250},
            {'nombre': 'Leche Andina 1L', 'descripcion': 'Leche entera de calidad', 'marca': 'Andina', 'precio': '1.08', 'stock': 200},
            {'nombre': 'Leche en Polvo Anchor 400g', 'descripcion': 'Leche en polvo instantanea', 'marca': 'Anchor', 'precio': '4.50', 'stock': 100},

            # HUEVOS
            {'nombre': 'Huevos Indaves x12', 'descripcion': 'Cubeta de 12 huevos frescos', 'marca': 'Indaves', 'precio': '2.50', 'stock': 150},
            {'nombre': 'Huevos Indaves x30', 'descripcion': 'Cubeta de 30 huevos frescos', 'marca': 'Indaves', 'precio': '5.80', 'stock': 80},
            {'nombre': 'Huevos Oro x12', 'descripcion': 'Huevos de gallina criolla', 'marca': 'Oro', 'precio': '2.75', 'stock': 100},

            # PAN
            {'nombre': 'Pan Supan Familiar 500g', 'descripcion': 'Pan de molde blanco', 'marca': 'Supan', 'precio': '1.80', 'stock': 120},
            {'nombre': 'Pan Supan Integral 500g', 'descripcion': 'Pan de molde integral', 'marca': 'Supan', 'precio': '2.10', 'stock': 80},
            {'nombre': 'Pan Bimbo Blanco 600g', 'descripcion': 'Pan de molde suave', 'marca': 'Bimbo', 'precio': '2.50', 'stock': 100},
            {'nombre': 'Pan Bimbo Integral 600g', 'descripcion': 'Pan integral con fibra', 'marca': 'Bimbo', 'precio': '2.80', 'stock': 70},

            # ACEITE
            {'nombre': 'Aceite La Favorita 1L', 'descripcion': 'Aceite vegetal de palma', 'marca': 'La Favorita', 'precio': '2.75', 'stock': 180},
            {'nombre': 'Aceite La Favorita 500ml', 'descripcion': 'Aceite vegetal de palma', 'marca': 'La Favorita', 'precio': '1.50', 'stock': 150},
            {'nombre': 'Aceite Girasol 1L', 'descripcion': 'Aceite de girasol puro', 'marca': 'El Cocinero', 'precio': '3.20', 'stock': 100},
            {'nombre': 'Aceite Oliva Extra Virgen 500ml', 'descripcion': 'Aceite de oliva premium', 'marca': 'Carbonell', 'precio': '8.50', 'stock': 50},

            # AZUCAR
            {'nombre': 'Azucar San Carlos 1kg', 'descripcion': 'Azucar blanca refinada', 'marca': 'San Carlos', 'precio': '1.10', 'stock': 200},
            {'nombre': 'Azucar San Carlos 2kg', 'descripcion': 'Azucar blanca refinada', 'marca': 'San Carlos', 'precio': '2.15', 'stock': 150},
            {'nombre': 'Azucar Morena 1kg', 'descripcion': 'Azucar morena natural', 'marca': 'Valdez', 'precio': '1.35', 'stock': 100},

            # SAL
            {'nombre': 'Sal Crisal 1kg', 'descripcion': 'Sal refinada yodada', 'marca': 'Crisal', 'precio': '0.65', 'stock': 250},
            {'nombre': 'Sal Marina 500g', 'descripcion': 'Sal marina natural', 'marca': 'Del Mar', 'precio': '1.20', 'stock': 80},

            # HARINA
            {'nombre': 'Harina Ya 1kg', 'descripcion': 'Harina de trigo todo uso', 'marca': 'Ya', 'precio': '1.25', 'stock': 150},
            {'nombre': 'Harina Tomebamba 1kg', 'descripcion': 'Harina de trigo fortificada', 'marca': 'Tomebamba', 'precio': '1.30', 'stock': 120},

            # LEGUMBRES
            {'nombre': 'Frejol Negro 500g', 'descripcion': 'Frejol negro seleccionado', 'marca': 'Don Diego', 'precio': '1.80', 'stock': 100},
            {'nombre': 'Frejol Rojo 500g', 'descripcion': 'Frejol rojo de calidad', 'marca': 'Don Diego', 'precio': '1.75', 'stock': 100},
            {'nombre': 'Lenteja 500g', 'descripcion': 'Lenteja grande seleccionada', 'marca': 'Don Diego', 'precio': '1.50', 'stock': 120},
            {'nombre': 'Garbanzo 500g', 'descripcion': 'Garbanzo premium', 'marca': 'Don Diego', 'precio': '2.00', 'stock': 80},
            {'nombre': 'Arveja Seca 500g', 'descripcion': 'Arveja seca de calidad', 'marca': 'Don Diego', 'precio': '1.60', 'stock': 90},

            # FIDEOS/PASTAS
            {'nombre': 'Fideo Oriental Tallarin 400g', 'descripcion': 'Fideo tipo tallarin', 'marca': 'Oriental', 'precio': '0.95', 'stock': 200},
            {'nombre': 'Fideo Oriental Cabello 400g', 'descripcion': 'Fideo cabello de angel', 'marca': 'Oriental', 'precio': '0.95', 'stock': 180},
            {'nombre': 'Espagueti Doria 400g', 'descripcion': 'Pasta espagueti clasica', 'marca': 'Doria', 'precio': '1.20', 'stock': 150},
            {'nombre': 'Macarron Doria 400g', 'descripcion': 'Pasta tipo macarron', 'marca': 'Doria', 'precio': '1.20', 'stock': 130},

            # ATUN Y SARDINAS
            {'nombre': 'Atun Real en Aceite 160g', 'descripcion': 'Atun en aceite vegetal', 'marca': 'Real', 'precio': '1.85', 'stock': 200},
            {'nombre': 'Atun Real en Agua 160g', 'descripcion': 'Atun en agua light', 'marca': 'Real', 'precio': '1.80', 'stock': 150},
            {'nombre': 'Atun Van Camps 160g', 'descripcion': 'Atun lomo solido', 'marca': 'Van Camps', 'precio': '2.10', 'stock': 180},
            {'nombre': 'Sardina Real en Tomate 425g', 'descripcion': 'Sardina en salsa de tomate', 'marca': 'Real', 'precio': '2.25', 'stock': 120},
            {'nombre': 'Sardina Tinapa en Aceite 156g', 'descripcion': 'Sardina en aceite', 'marca': 'Tinapa', 'precio': '1.50', 'stock': 100},

            # CARNES Y POLLO (precios aproximados)
            {'nombre': 'Pechuga de Pollo 1kg', 'descripcion': 'Pechuga de pollo fresca', 'marca': 'Pronaca', 'precio': '5.80', 'stock': 50},
            {'nombre': 'Muslo de Pollo 1kg', 'descripcion': 'Muslo de pollo fresco', 'marca': 'Pronaca', 'precio': '4.50', 'stock': 60},
            {'nombre': 'Carne Molida Res 500g', 'descripcion': 'Carne molida de res', 'marca': 'Mr. Pollo', 'precio': '4.20', 'stock': 40},

            # FRUTAS Y VERDURAS
            {'nombre': 'Tomate Rinon 1kg', 'descripcion': 'Tomate fresco seleccionado', 'marca': 'Del Campo', 'precio': '1.50', 'stock': 80},
            {'nombre': 'Cebolla Perla 1kg', 'descripcion': 'Cebolla perla fresca', 'marca': 'Del Campo', 'precio': '1.20', 'stock': 100},
            {'nombre': 'Papa Chola 2kg', 'descripcion': 'Papa chola de calidad', 'marca': 'Del Campo', 'precio': '2.00', 'stock': 120},
            {'nombre': 'Platano Maduro 1kg', 'descripcion': 'Platano maduro fresco', 'marca': 'Del Campo', 'precio': '1.00', 'stock': 80},
            {'nombre': 'Platano Verde 1kg', 'descripcion': 'Platano verde fresco', 'marca': 'Del Campo', 'precio': '0.90', 'stock': 90},

            # AGUA
            {'nombre': 'Agua Dasani 500ml', 'descripcion': 'Agua purificada sin gas', 'marca': 'Dasani', 'precio': '0.50', 'stock': 300},
            {'nombre': 'Agua Dasani 1L', 'descripcion': 'Agua purificada sin gas', 'marca': 'Dasani', 'precio': '0.75', 'stock': 200},
            {'nombre': 'Agua Tesalia 500ml', 'descripcion': 'Agua mineral natural', 'marca': 'Tesalia', 'precio': '0.55', 'stock': 250},
            {'nombre': 'Bidon Agua 6L', 'descripcion': 'Bidon de agua purificada', 'marca': 'Pure Water', 'precio': '1.50', 'stock': 100},

            # AVENA
            {'nombre': 'Avena Quaker 500g', 'descripcion': 'Avena en hojuelas', 'marca': 'Quaker', 'precio': '2.20', 'stock': 120},
            {'nombre': 'Avena Molida 500g', 'descripcion': 'Avena molida instantanea', 'marca': 'Don Pancho', 'precio': '1.80', 'stock': 100},
        ]

        # PRODUCTOS CON IVA 15%
        productos_con_iva = [
            # BEBIDAS GASEOSAS
            {'nombre': 'Coca Cola 500ml', 'descripcion': 'Bebida gaseosa cola', 'marca': 'Coca Cola', 'precio': '0.85', 'stock': 300},
            {'nombre': 'Coca Cola 1.5L', 'descripcion': 'Bebida gaseosa cola familiar', 'marca': 'Coca Cola', 'precio': '1.75', 'stock': 150},
            {'nombre': 'Coca Cola 3L', 'descripcion': 'Bebida gaseosa cola grande', 'marca': 'Coca Cola', 'precio': '2.80', 'stock': 100},
            {'nombre': 'Sprite 500ml', 'descripcion': 'Bebida gaseosa lima limon', 'marca': 'Sprite', 'precio': '0.85', 'stock': 200},
            {'nombre': 'Fanta Naranja 500ml', 'descripcion': 'Bebida gaseosa naranja', 'marca': 'Fanta', 'precio': '0.85', 'stock': 180},
            {'nombre': 'Pepsi 500ml', 'descripcion': 'Bebida gaseosa cola', 'marca': 'Pepsi', 'precio': '0.80', 'stock': 200},

            # JUGOS
            {'nombre': 'Jugo del Valle Naranja 1L', 'descripcion': 'Jugo de naranja', 'marca': 'Del Valle', 'precio': '1.50', 'stock': 120},
            {'nombre': 'Jugo del Valle Durazno 1L', 'descripcion': 'Jugo de durazno', 'marca': 'Del Valle', 'precio': '1.50', 'stock': 100},
            {'nombre': 'Jugo Sunny Naranja 200ml', 'descripcion': 'Jugo de naranja personal', 'marca': 'Sunny', 'precio': '0.50', 'stock': 200},
            {'nombre': 'Tampico Citrus 500ml', 'descripcion': 'Bebida citrica refrescante', 'marca': 'Tampico', 'precio': '0.75', 'stock': 150},

            # GALLETAS Y SNACKS
            {'nombre': 'Galletas Oreo x6', 'descripcion': 'Galletas de chocolate con crema', 'marca': 'Oreo', 'precio': '1.50', 'stock': 150},
            {'nombre': 'Galletas Oreo x12', 'descripcion': 'Galletas de chocolate familiar', 'marca': 'Oreo', 'precio': '2.80', 'stock': 100},
            {'nombre': 'Galletas Maria 400g', 'descripcion': 'Galletas clasicas Maria', 'marca': 'Nestle', 'precio': '1.80', 'stock': 120},
            {'nombre': 'Galletas Club Social 6 pack', 'descripcion': 'Galletas saladas', 'marca': 'Club Social', 'precio': '1.20', 'stock': 150},
            {'nombre': 'Ruffles Original 150g', 'descripcion': 'Papas fritas onduladas', 'marca': 'Ruffles', 'precio': '2.50', 'stock': 100},
            {'nombre': 'Doritos Nacho 150g', 'descripcion': 'Tortillas de maiz con queso', 'marca': 'Doritos', 'precio': '2.50', 'stock': 100},
            {'nombre': 'Cheetos 120g', 'descripcion': 'Snack de maiz con queso', 'marca': 'Cheetos', 'precio': '1.80', 'stock': 120},
            {'nombre': 'Papas Lays Clasicas 150g', 'descripcion': 'Papas fritas clasicas', 'marca': 'Lays', 'precio': '2.30', 'stock': 100},

            # CHOCOLATES Y DULCES
            {'nombre': 'Chocolate Jet 50g', 'descripcion': 'Barra de chocolate con leche', 'marca': 'Jet', 'precio': '0.75', 'stock': 200},
            {'nombre': 'Chocolate Manicho 28g', 'descripcion': 'Chocolate con mani', 'marca': 'Manicho', 'precio': '0.50', 'stock': 250},
            {'nombre': 'Chocolate Galak 30g', 'descripcion': 'Chocolate blanco', 'marca': 'Nestle', 'precio': '0.60', 'stock': 180},
            {'nombre': 'Caramelos Frunas 100g', 'descripcion': 'Caramelos masticables', 'marca': 'Frunas', 'precio': '0.80', 'stock': 150},
            {'nombre': 'Chicle Trident 18g', 'descripcion': 'Chicle sin azucar', 'marca': 'Trident', 'precio': '0.75', 'stock': 200},
            {'nombre': 'Chupete Bon Bon Bum', 'descripcion': 'Chupete con chicle', 'marca': 'Colombina', 'precio': '0.25', 'stock': 300},

            # HIGIENE PERSONAL
            {'nombre': 'Jabon Dove Original 90g', 'descripcion': 'Jabon de tocador humectante', 'marca': 'Dove', 'precio': '1.20', 'stock': 150},
            {'nombre': 'Jabon Protex 110g', 'descripcion': 'Jabon antibacterial', 'marca': 'Protex', 'precio': '1.35', 'stock': 130},
            {'nombre': 'Shampoo Head & Shoulders 375ml', 'descripcion': 'Shampoo anticaspa', 'marca': 'Head & Shoulders', 'precio': '5.50', 'stock': 80},
            {'nombre': 'Shampoo Sedal 340ml', 'descripcion': 'Shampoo con ceramidas', 'marca': 'Sedal', 'precio': '4.20', 'stock': 90},
            {'nombre': 'Shampoo Pantene 400ml', 'descripcion': 'Shampoo restauracion', 'marca': 'Pantene', 'precio': '6.00', 'stock': 70},
            {'nombre': 'Acondicionador Sedal 340ml', 'descripcion': 'Acondicionador con ceramidas', 'marca': 'Sedal', 'precio': '4.50', 'stock': 80},
            {'nombre': 'Pasta Dental Colgate 75ml', 'descripcion': 'Pasta dental triple accion', 'marca': 'Colgate', 'precio': '1.80', 'stock': 150},
            {'nombre': 'Pasta Dental Colgate 150ml', 'descripcion': 'Pasta dental triple accion grande', 'marca': 'Colgate', 'precio': '3.20', 'stock': 100},
            {'nombre': 'Cepillo Dental Colgate', 'descripcion': 'Cepillo dental medio', 'marca': 'Colgate', 'precio': '1.50', 'stock': 120},
            {'nombre': 'Desodorante Rexona 150ml', 'descripcion': 'Desodorante aerosol', 'marca': 'Rexona', 'precio': '4.50', 'stock': 100},
            {'nombre': 'Desodorante Axe 150ml', 'descripcion': 'Desodorante aerosol masculino', 'marca': 'Axe', 'precio': '5.20', 'stock': 80},

            # LIMPIEZA DEL HOGAR
            {'nombre': 'Detergente Deja 1kg', 'descripcion': 'Detergente en polvo', 'marca': 'Deja', 'precio': '2.80', 'stock': 150},
            {'nombre': 'Detergente Fab 1kg', 'descripcion': 'Detergente multiusos', 'marca': 'Fab', 'precio': '3.00', 'stock': 130},
            {'nombre': 'Suavizante Suavitel 500ml', 'descripcion': 'Suavizante de ropa', 'marca': 'Suavitel', 'precio': '2.50', 'stock': 120},
            {'nombre': 'Cloro Clorox 1L', 'descripcion': 'Blanqueador desinfectante', 'marca': 'Clorox', 'precio': '1.80', 'stock': 150},
            {'nombre': 'Desinfectante Fabuloso 1L', 'descripcion': 'Limpiador multiusos', 'marca': 'Fabuloso', 'precio': '2.50', 'stock': 130},
            {'nombre': 'Lavavajilla Lava 500g', 'descripcion': 'Lavavajilla en crema', 'marca': 'Lava', 'precio': '1.50', 'stock': 150},
            {'nombre': 'Esponja Scotch Brite', 'descripcion': 'Esponja para lavar platos', 'marca': 'Scotch Brite', 'precio': '0.80', 'stock': 200},
            {'nombre': 'Papel Higienico Scott x4', 'descripcion': 'Papel higienico doble hoja', 'marca': 'Scott', 'precio': '2.80', 'stock': 150},
            {'nombre': 'Papel Higienico Familia x12', 'descripcion': 'Papel higienico familiar', 'marca': 'Familia', 'precio': '6.50', 'stock': 80},
            {'nombre': 'Servilletas Elite x100', 'descripcion': 'Servilletas de papel', 'marca': 'Elite', 'precio': '1.20', 'stock': 150},
            {'nombre': 'Toallas de Cocina Scott x3', 'descripcion': 'Toallas absorbentes', 'marca': 'Scott', 'precio': '3.50', 'stock': 100},
            {'nombre': 'Bolsas de Basura x10', 'descripcion': 'Bolsas para basura grandes', 'marca': 'Reforzadas', 'precio': '1.50', 'stock': 120},

            # CAFE Y TE
            {'nombre': 'Cafe Nescafe Clasico 100g', 'descripcion': 'Cafe instantaneo', 'marca': 'Nescafe', 'precio': '4.50', 'stock': 100},
            {'nombre': 'Cafe Nescafe Clasico 200g', 'descripcion': 'Cafe instantaneo grande', 'marca': 'Nescafe', 'precio': '8.00', 'stock': 60},
            {'nombre': 'Cafe Buen Dia 170g', 'descripcion': 'Cafe tostado molido', 'marca': 'Buen Dia', 'precio': '3.80', 'stock': 80},
            {'nombre': 'Te Hornimans x25', 'descripcion': 'Te en bolsitas', 'marca': 'Hornimans', 'precio': '1.50', 'stock': 120},
            {'nombre': 'Te Aromatico Surtido x20', 'descripcion': 'Te aromatico variado', 'marca': 'Hornimans', 'precio': '1.80', 'stock': 100},

            # LACTEOS PROCESADOS
            {'nombre': 'Yogurt Toni 1L', 'descripcion': 'Yogurt natural', 'marca': 'Toni', 'precio': '2.80', 'stock': 100},
            {'nombre': 'Yogurt Toni Frutilla 180g', 'descripcion': 'Yogurt de frutilla', 'marca': 'Toni', 'precio': '0.85', 'stock': 150},
            {'nombre': 'Queso Mozzarella 500g', 'descripcion': 'Queso mozzarella fresco', 'marca': 'Kiosko', 'precio': '4.50', 'stock': 50},
            {'nombre': 'Queso Crema 250g', 'descripcion': 'Queso crema untable', 'marca': 'Kiosko', 'precio': '2.80', 'stock': 70},
            {'nombre': 'Mantequilla Reyleche 250g', 'descripcion': 'Mantequilla con sal', 'marca': 'Reyleche', 'precio': '2.50', 'stock': 80},
            {'nombre': 'Margarina La Fabril 500g', 'descripcion': 'Margarina para cocinar', 'marca': 'La Fabril', 'precio': '1.80', 'stock': 100},

            # ENLATADOS Y CONSERVAS
            {'nombre': 'Salsa de Tomate Maggi 400g', 'descripcion': 'Salsa de tomate natural', 'marca': 'Maggi', 'precio': '1.50', 'stock': 150},
            {'nombre': 'Mayonesa Maggi 400g', 'descripcion': 'Mayonesa cremosa', 'marca': 'Maggi', 'precio': '2.80', 'stock': 120},
            {'nombre': 'Mostaza French 250g', 'descripcion': 'Mostaza clasica', 'marca': 'Frenchs', 'precio': '2.20', 'stock': 100},
            {'nombre': 'Salsa BBQ 300ml', 'descripcion': 'Salsa barbacoa', 'marca': 'Heinz', 'precio': '3.50', 'stock': 80},
            {'nombre': 'Vinagre Blanco 500ml', 'descripcion': 'Vinagre de cocina', 'marca': 'El Sabor', 'precio': '1.20', 'stock': 100},
            {'nombre': 'Aceitunas Verdes 240g', 'descripcion': 'Aceitunas verdes en frasco', 'marca': 'Snob', 'precio': '3.20', 'stock': 60},
            {'nombre': 'Maiz Dulce 300g', 'descripcion': 'Maiz dulce en lata', 'marca': 'Del Monte', 'precio': '1.80', 'stock': 100},
            {'nombre': 'Arvejas en Lata 300g', 'descripcion': 'Arvejas tiernas', 'marca': 'Del Monte', 'precio': '1.50', 'stock': 100},

            # CEREALES
            {'nombre': 'Cereal Corn Flakes 500g', 'descripcion': 'Hojuelas de maiz', 'marca': 'Kelloggs', 'precio': '4.50', 'stock': 80},
            {'nombre': 'Cereal Zucaritas 400g', 'descripcion': 'Hojuelas azucaradas', 'marca': 'Kelloggs', 'precio': '4.80', 'stock': 70},
            {'nombre': 'Cereal Chocapic 400g', 'descripcion': 'Cereal de chocolate', 'marca': 'Nestle', 'precio': '5.00', 'stock': 60},

            # BEBIDAS ENERGETICAS
            {'nombre': 'Gatorade 500ml', 'descripcion': 'Bebida hidratante', 'marca': 'Gatorade', 'precio': '1.50', 'stock': 150},
            {'nombre': 'Powerade 500ml', 'descripcion': 'Bebida isotonica', 'marca': 'Powerade', 'precio': '1.40', 'stock': 130},
            {'nombre': 'Red Bull 250ml', 'descripcion': 'Bebida energizante', 'marca': 'Red Bull', 'precio': '2.50', 'stock': 100},
            {'nombre': 'Monster Energy 473ml', 'descripcion': 'Bebida energizante', 'marca': 'Monster', 'precio': '2.80', 'stock': 80},

            # LICORES (solo algunos basicos)
            {'nombre': 'Cerveza Pilsener 600ml', 'descripcion': 'Cerveza tipo pilsener', 'marca': 'Pilsener', 'precio': '1.80', 'stock': 200},
            {'nombre': 'Cerveza Club Verde 330ml', 'descripcion': 'Cerveza premium', 'marca': 'Club', 'precio': '1.50', 'stock': 150},
        ]

        # Crear productos de primera necesidad
        for prod_data in productos_primera_necesidad:
            if not Producto.objects.filter(nombre=prod_data['nombre']).exists():
                codigo = generar_codigo_unico('PN')
                Producto.objects.create(
                    codigo=codigo,
                    nombre=prod_data['nombre'],
                    descripcion=prod_data['descripcion'],
                    marca=prod_data['marca'],
                    precio_unitario=Decimal(prod_data['precio']),
                    stock=prod_data['stock'],
                    es_primera_necesidad=True
                )
                self.stdout.write(self.style.SUCCESS(f'[OK] {prod_data["nombre"]} (IVA 0%) - Codigo: {codigo}'))

        # Crear productos con IVA
        for prod_data in productos_con_iva:
            if not Producto.objects.filter(nombre=prod_data['nombre']).exists():
                codigo = generar_codigo_unico('PR')
                Producto.objects.create(
                    codigo=codigo,
                    nombre=prod_data['nombre'],
                    descripcion=prod_data['descripcion'],
                    marca=prod_data['marca'],
                    precio_unitario=Decimal(prod_data['precio']),
                    stock=prod_data['stock'],
                    es_primera_necesidad=False
                )
                self.stdout.write(self.style.SUCCESS(f'[OK] {prod_data["nombre"]} (IVA 15%) - Codigo: {codigo}'))

        # ============== RESUMEN ==============
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write('RESUMEN DE DATOS CREADOS')
        self.stdout.write('=' * 60)
        self.stdout.write(f'Empleados: {Empleado.objects.count()}')
        self.stdout.write(f'Clientes: {Cliente.objects.count()}')
        self.stdout.write(f'Productos Primera Necesidad (IVA 0%): {Producto.objects.filter(es_primera_necesidad=True).count()}')
        self.stdout.write(f'Productos con IVA (15%): {Producto.objects.filter(es_primera_necesidad=False).count()}')
        self.stdout.write(f'Total Productos: {Producto.objects.count()}')
        self.stdout.write('=' * 60)
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('CREDENCIALES DE ACCESO:'))
        self.stdout.write(self.style.WARNING('  Administrador: admin / Admin2024*'))
        self.stdout.write(self.style.WARNING('  Cajero 1: cajero1 / Cajero2024*'))
        self.stdout.write(self.style.WARNING('  Cajero 2: cajero2 / Cajero2024*'))
        self.stdout.write(self.style.WARNING('  Cajero 3: cajero3 / Cajero2024*'))
        self.stdout.write('')

