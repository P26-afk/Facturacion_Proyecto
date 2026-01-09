from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('gestion/empleados/', views.lista_empleados, name='lista_empleados'),
    path('gestion/empleados/crear/', views.crear_empleado, name='crear_empleado'),
    path('gestion/empleados/editar/<int:pk>/', views.editar_empleado, name='editar_empleado'),
    path('gestion/empleados/eliminar/<int:pk>/', views.eliminar_empleado, name='eliminar_empleado'),

    path('gestion/productos/', views.lista_productos, name='lista_productos'),
    path('gestion/productos/crear/', views.crear_producto, name='crear_producto'),
    path('gestion/productos/editar/<int:pk>/', views.editar_producto, name='editar_producto'),
    path('gestion/productos/eliminar/<int:pk>/', views.eliminar_producto, name='eliminar_producto'),

    path('gestion/clientes/', views.lista_clientes, name='lista_clientes'),
    path('gestion/clientes/editar/<int:pk>/', views.editar_cliente, name='editar_cliente'),
    path('gestion/clientes/eliminar/<int:pk>/', views.eliminar_cliente, name='eliminar_cliente'),

    path('facturacion/', views.facturacion, name='facturacion'),
    path('facturacion/buscar-producto/', views.buscar_producto, name='buscar_producto'),
    path('facturacion/buscar-cliente/', views.buscar_cliente, name='buscar_cliente'),
    path('facturacion/crear-cliente/', views.crear_cliente, name='crear_cliente'),
    path('facturacion/procesar/', views.procesar_factura, name='procesar_factura'),
    path('facturacion/descargar/<int:pk>/', views.descargar_factura, name='descargar_factura'),
    path('facturacion/historial/', views.historial_facturas, name='historial_facturas'),
    path('facturacion/detalle/<int:pk>/', views.detalle_factura, name='detalle_factura'),
]

