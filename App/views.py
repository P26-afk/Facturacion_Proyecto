from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.views.decorators.http import require_POST, require_GET
from decimal import Decimal
import json
import textwrap
from .models import Empleado, Cliente, Producto, Factura, DetalleFactura

NOMBRE_LOCAL = "UNIMARK"
MENSAJE_LOCAL = ("En Unimark encontraras productos de calidad a precios "
                 "justos y atencion rapida y amable. Visitanos hoy y descubre "
                 "por que nuestros clientes confian en nosotros.")


def es_admin(user):
    return user.groups.filter(name='Admin').exists() or user.is_superuser


def es_cajero(user):
    return user.groups.filter(name='Cajero').exists()


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenido {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuario o contrasena incorrectos.')

    return render(request, 'login.html')


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Has cerrado sesion correctamente.')
    return redirect('login')


@login_required
def dashboard(request):
    if es_admin(request.user):
        from django.utils import timezone
        from django.db.models import Sum
        hoy = timezone.now().date()

        facturas_hoy_qs = Factura.objects.filter(fecha__date=hoy)
        ventas_hoy = facturas_hoy_qs.aggregate(total=Sum('total'))['total'] or Decimal('0.00')
        facturas_hoy = facturas_hoy_qs.count()
        clientes_hoy = facturas_hoy_qs.values('cliente').distinct().count()

        context = {
            'total_empleados': Empleado.objects.filter(activo=True).count(),
            'total_productos': Producto.objects.filter(activo=True).count(),
            'total_clientes': Cliente.objects.count(),
            'total_facturas': Factura.objects.count(),
            'productos_bajo_stock': Producto.objects.filter(stock__lte=5, activo=True)[:10],
            'ultimas_facturas': Factura.objects.all().order_by('-fecha')[:5],
            'ventas_hoy': ventas_hoy,
            'facturas_hoy': facturas_hoy,
            'clientes_hoy': clientes_hoy,
            'es_admin': True,
        }
        return render(request, 'admin/dashboard.html', context)
    elif es_cajero(request.user):
        return redirect('facturacion')
    else:
        messages.error(request, 'No tienes permisos para acceder al sistema.')
        return redirect('login')


# Empleados

@login_required
def lista_empleados(request):
    if not es_admin(request.user):
        messages.error(request, 'No tienes permisos para esta accion.')
        return redirect('dashboard')

    empleados = Empleado.objects.all()
    return render(request, 'admin/empleados.html', {'empleados': empleados})


@login_required
def crear_empleado(request):
    if not es_admin(request.user):
        messages.error(request, 'No tienes permisos para esta accion.')
        return redirect('dashboard')

    if request.method == 'POST':
        try:
            cedula = request.POST.get('cedula')
            nombre = request.POST.get('nombre')
            apellido = request.POST.get('apellido')
            celular = request.POST.get('celular')
            correo = request.POST.get('correo')
            cargo = request.POST.get('cargo')
            crear_usuario = request.POST.get('crear_usuario') == 'on'

            if len(cedula) != 10 or not cedula.isdigit():
                messages.error(request, 'La cedula debe tener exactamente 10 digitos.')
                return redirect('crear_empleado')

            if Empleado.objects.filter(cedula=cedula).exists():
                messages.error(request, 'Ya existe un empleado con esta cedula.')
                return redirect('crear_empleado')

            empleado = Empleado.objects.create(
                cedula=cedula,
                nombre=nombre,
                apellido=apellido,
                celular=celular,
                correo=correo,
                cargo=cargo
            )

            if crear_usuario and cargo == 'cajero':
                username = f"{nombre.lower()}.{apellido.lower()}"
                user = User.objects.create_user(
                    username=username,
                    email=correo,
                    password=cedula
                )
                grupo_cajero, _ = Group.objects.get_or_create(name='Cajero')
                user.groups.add(grupo_cajero)
                empleado.usuario = user
                empleado.save()
                messages.info(request, f'Usuario creado: {username} (contrasena: cedula)')

            messages.success(request, 'Empleado creado exitosamente.')
            return redirect('lista_empleados')

        except Exception as e:
            messages.error(request, f'Error al crear empleado: {str(e)}')

    return render(request, 'admin/empleado_form.html', {
        'cargos': Empleado.CARGO_CHOICES,
        'accion': 'Crear'
    })


@login_required
def editar_empleado(request, pk):
    if not es_admin(request.user):
        messages.error(request, 'No tienes permisos para esta accion.')
        return redirect('dashboard')

    empleado = get_object_or_404(Empleado, pk=pk)

    if request.method == 'POST':
        try:
            empleado.nombre = request.POST.get('nombre')
            empleado.apellido = request.POST.get('apellido')
            empleado.celular = request.POST.get('celular')
            empleado.correo = request.POST.get('correo')
            empleado.cargo = request.POST.get('cargo')
            empleado.activo = request.POST.get('activo') == 'on'
            empleado.save()

            messages.success(request, 'Empleado actualizado exitosamente.')
            return redirect('lista_empleados')

        except Exception as e:
            messages.error(request, f'Error al actualizar empleado: {str(e)}')

    return render(request, 'admin/empleado_form.html', {
        'empleado': empleado,
        'cargos': Empleado.CARGO_CHOICES,
        'accion': 'Editar'
    })


@login_required
def eliminar_empleado(request, pk):
    if not es_admin(request.user):
        messages.error(request, 'No tienes permisos para esta accion.')
        return redirect('dashboard')

    empleado = get_object_or_404(Empleado, pk=pk)
    empleado.activo = False
    empleado.save()

    if empleado.usuario:
        empleado.usuario.is_active = False
        empleado.usuario.save()

    messages.success(request, 'Empleado desactivado exitosamente.')
    return redirect('lista_empleados')


# Productos

@login_required
def lista_productos(request):
    if not es_admin(request.user):
        messages.error(request, 'No tienes permisos para esta accion.')
        return redirect('dashboard')

    productos = Producto.objects.all()
    return render(request, 'admin/productos.html', {'productos': productos})


@login_required
def crear_producto(request):
    if not es_admin(request.user):
        messages.error(request, 'No tienes permisos para esta accion.')
        return redirect('dashboard')

    if request.method == 'POST':
        try:
            codigo = request.POST.get('codigo')
            nombre = request.POST.get('nombre')
            descripcion = request.POST.get('descripcion')
            marca = request.POST.get('marca')
            precio_unitario = Decimal(request.POST.get('precio_unitario'))
            stock = int(request.POST.get('stock'))
            es_primera_necesidad = request.POST.get('es_primera_necesidad') == 'on'

            if Producto.objects.filter(codigo=codigo).exists():
                messages.error(request, 'Ya existe un producto con este codigo.')
                return redirect('crear_producto')

            Producto.objects.create(
                codigo=codigo,
                nombre=nombre,
                descripcion=descripcion,
                marca=marca,
                precio_unitario=precio_unitario,
                stock=stock,
                es_primera_necesidad=es_primera_necesidad
            )

            messages.success(request, 'Producto creado exitosamente.')
            return redirect('lista_productos')

        except Exception as e:
            messages.error(request, f'Error al crear producto: {str(e)}')

    return render(request, 'admin/producto_form.html', {'accion': 'Crear'})


@login_required
def editar_producto(request, pk):
    if not es_admin(request.user):
        messages.error(request, 'No tienes permisos para esta accion.')
        return redirect('dashboard')

    producto = get_object_or_404(Producto, pk=pk)

    if request.method == 'POST':
        try:
            producto.nombre = request.POST.get('nombre')
            producto.descripcion = request.POST.get('descripcion')
            producto.marca = request.POST.get('marca')
            producto.precio_unitario = Decimal(request.POST.get('precio_unitario'))
            producto.stock = int(request.POST.get('stock'))
            producto.es_primera_necesidad = request.POST.get('es_primera_necesidad') == 'on'
            producto.activo = request.POST.get('activo') == 'on'
            producto.save()

            messages.success(request, 'Producto actualizado exitosamente.')
            return redirect('lista_productos')

        except Exception as e:
            messages.error(request, f'Error al actualizar producto: {str(e)}')

    return render(request, 'admin/producto_form.html', {
        'producto': producto,
        'accion': 'Editar'
    })


@login_required
def eliminar_producto(request, pk):
    if not es_admin(request.user):
        messages.error(request, 'No tienes permisos para esta accion.')
        return redirect('dashboard')

    producto = get_object_or_404(Producto, pk=pk)
    producto.activo = False
    producto.save()

    messages.success(request, 'Producto desactivado exitosamente.')
    return redirect('lista_productos')


# Clientes

@login_required
def lista_clientes(request):
    if not es_admin(request.user):
        messages.error(request, 'No tienes permisos para esta accion.')
        return redirect('dashboard')

    clientes = Cliente.objects.all()
    return render(request, 'admin/clientes.html', {'clientes': clientes})


@login_required
def editar_cliente(request, pk):
    if not es_admin(request.user):
        messages.error(request, 'No tienes permisos para esta accion.')
        return redirect('dashboard')

    cliente = get_object_or_404(Cliente, pk=pk)

    if request.method == 'POST':
        try:
            cliente.nombre = request.POST.get('nombre')
            cliente.apellido = request.POST.get('apellido')
            cliente.celular = request.POST.get('celular')
            cliente.correo = request.POST.get('correo')
            cliente.save()

            messages.success(request, 'Cliente actualizado exitosamente.')
            return redirect('lista_clientes')

        except Exception as e:
            messages.error(request, f'Error al actualizar cliente: {str(e)}')

    return render(request, 'admin/cliente_form.html', {
        'cliente': cliente,
        'accion': 'Editar'
    })


@login_required
def eliminar_cliente(request, pk):
    if not es_admin(request.user):
        messages.error(request, 'No tienes permisos para esta accion.')
        return redirect('dashboard')

    cliente = get_object_or_404(Cliente, pk=pk)

    if cliente.es_consumidor_final:
        messages.error(request, 'No se puede eliminar el Consumidor Final.')
        return redirect('lista_clientes')

    cliente.delete()
    messages.success(request, 'Cliente eliminado exitosamente.')
    return redirect('lista_clientes')


# Facturacion

@login_required
def facturacion(request):
    if not (es_cajero(request.user) or es_admin(request.user)):
        messages.error(request, 'No tienes permisos para esta accion.')
        return redirect('dashboard')

    productos = Producto.objects.filter(activo=True, stock__gt=0)
    return render(request, 'cajero/facturacion.html', {
        'productos': productos,
        'nombre_local': NOMBRE_LOCAL
    })


@login_required
@require_GET
def buscar_producto(request):
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'productos': []})

    productos = Producto.objects.filter(
        Q(nombre__icontains=query) | Q(codigo__icontains=query),
        activo=True,
        stock__gt=0
    )[:10]

    data = [{
        'id': p.id,
        'codigo': p.codigo,
        'nombre': p.nombre,
        'marca': p.marca,
        'precio': str(p.precio_unitario),
        'stock': p.stock,
        'es_primera_necesidad': p.es_primera_necesidad,
        'iva': '0%' if p.es_primera_necesidad else '15%'
    } for p in productos]

    return JsonResponse({'productos': data})


@login_required
@require_GET
def buscar_cliente(request):
    cedula = request.GET.get('cedula', '')

    if cedula == '9999999999':
        cliente = Cliente.get_consumidor_final()
        return JsonResponse({
            'encontrado': True,
            'cliente': {
                'id': cliente.id,
                'cedula': cliente.cedula,
                'nombre': cliente.nombre,
                'apellido': cliente.apellido,
                'celular': cliente.celular,
                'correo': cliente.correo,
                'es_consumidor_final': True
            }
        })

    try:
        cliente = Cliente.objects.get(cedula=cedula)
        return JsonResponse({
            'encontrado': True,
            'cliente': {
                'id': cliente.id,
                'cedula': cliente.cedula,
                'nombre': cliente.nombre,
                'apellido': cliente.apellido,
                'celular': cliente.celular,
                'correo': cliente.correo,
                'es_consumidor_final': cliente.es_consumidor_final
            }
        })
    except Cliente.DoesNotExist:
        return JsonResponse({'encontrado': False})


@login_required
@require_POST
def crear_cliente(request):
    if not es_cajero(request.user):
        return JsonResponse({
            'success': False,
            'error': 'Solo los cajeros pueden crear nuevos clientes.'
        })

    try:
        data = json.loads(request.body)
        cedula = data.get('cedula')

        if len(cedula) != 10 or not cedula.isdigit():
            return JsonResponse({
                'success': False,
                'error': 'La cedula debe tener exactamente 10 digitos.'
            })

        if Cliente.objects.filter(cedula=cedula).exists():
            return JsonResponse({
                'success': False,
                'error': 'Ya existe un cliente con esta cedula.'
            })

        cliente = Cliente.objects.create(
            cedula=cedula,
            nombre=data.get('nombre'),
            apellido=data.get('apellido'),
            celular=data.get('celular'),
            correo=data.get('correo')
        )

        return JsonResponse({
            'success': True,
            'cliente': {
                'id': cliente.id,
                'cedula': cliente.cedula,
                'nombre': cliente.nombre,
                'apellido': cliente.apellido,
                'celular': cliente.celular,
                'correo': cliente.correo
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_POST
def procesar_factura(request):
    try:
        data = json.loads(request.body)
        cliente_id = data.get('cliente_id')
        items = data.get('items', [])

        if not items:
            return JsonResponse({
                'success': False,
                'error': 'No hay productos en la factura.'
            })

        cliente = get_object_or_404(Cliente, pk=cliente_id)

        try:
            empleado = Empleado.objects.get(usuario=request.user)
        except Empleado.DoesNotExist:
            empleado = Empleado.objects.filter(cargo='administrativo').first()
            if not empleado:
                return JsonResponse({
                    'success': False,
                    'error': 'No se encontro empleado asociado.'
                })

        factura = Factura.objects.create(
            cliente=cliente,
            empleado=empleado
        )

        for item in items:
            producto = get_object_or_404(Producto, pk=item['producto_id'])
            cantidad = int(item['cantidad'])

            if producto.stock < cantidad:
                factura.delete()
                return JsonResponse({
                    'success': False,
                    'error': f'Stock insuficiente para {producto.nombre}. Disponible: {producto.stock}'
                })

            DetalleFactura.objects.create(
                factura=factura,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=producto.precio_unitario
            )

        factura.calcular_totales()

        return JsonResponse({
            'success': True,
            'factura_id': factura.id,
            'numero': factura.numero,
            'total': str(factura.total)
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def descargar_factura(request, pk):
    factura = get_object_or_404(Factura, pk=pk)

    linea = "=" * 50
    linea_simple = "-" * 50

    contenido = f"""
{linea}
{"UNIMARK":^50}
{linea}

FACTURA N: {factura.numero}
FECHA: {factura.fecha.strftime('%d/%m/%Y %H:%M')}

{linea_simple}
DATOS DEL CLIENTE
{linea_simple}
Cedula: {factura.cliente.cedula}
Nombre: {factura.cliente.nombre_completo}
Telefono: {factura.cliente.celular}
Correo: {factura.cliente.correo}

{linea_simple}
"""

    width = len(linea)
    mensaje_lineas = textwrap.wrap(MENSAJE_LOCAL, width=width, break_long_words=False, break_on_hyphens=False)
    mensaje_formateado = "\n".join([ml.center(width) for ml in mensaje_lineas]) + "\n"

    contenido += mensaje_formateado
    contenido += f"{linea_simple}\n\n"

    contenido += "{:<20} {:>6} {:>10} {:>10}\n{}\n".format("PRODUCTO", "CANT", "P.UNIT", "TOTAL", linea_simple)

    for detalle in factura.detalles.all():
        nombre = detalle.producto.nombre[:20]
        iva_tag = "(0%)" if detalle.producto.es_primera_necesidad else "(15%)"
        contenido += f"{nombre:<20} {detalle.cantidad:>6} ${detalle.precio_unitario:>9.2f} ${detalle.total_linea:>9.2f} {iva_tag}\n"

    contenido += f"""
{linea_simple}

{"Subtotal (IVA 0%):":<30} ${factura.subtotal_sin_iva:>15.2f}
{"Subtotal (IVA 15%):":<30} ${factura.subtotal_con_iva:>15.2f}
{linea}
{"TOTAL A PAGAR:":<30} ${factura.total:>15.2f}
{linea}

Atendido por: {factura.empleado.nombre_completo}

Gracias por su compra!
Vuelva pronto a UNIMARK
"""

    response = HttpResponse(contenido, content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="factura_{factura.numero}.txt"'
    return response


@login_required
def historial_facturas(request):
    facturas = Factura.objects.all().order_by('-fecha')
    return render(request, 'cajero/historial.html', {'facturas': facturas})


@login_required
def detalle_factura(request, pk):
    factura = get_object_or_404(Factura, pk=pk)
    return render(request, 'cajero/detalle_factura.html', {
        'factura': factura,
        'nombre_local': NOMBRE_LOCAL,
        'mensaje_local': MENSAJE_LOCAL
    })
