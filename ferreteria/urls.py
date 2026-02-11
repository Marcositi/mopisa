from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from core import views
from core.views import (
    inicio, 
    productos,          
    producto_detalle,
    lista_promociones, 
    promocion_detalle,
    cotizar_productos,
    detalle_cotizacion, 
    crear_cliente, 
    cotizaciones_cliente, 
    eliminar_cotizacion,
    pedidos, 
    detalle_pedido, 
    eliminar_pedido, 
    carrito_view,
    inventario_view
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Página principal
    path('', inicio, name='inicio'),

    # Productos y promociones
    path('promociones/', lista_promociones, name='promociones'),
    path('promociones/<int:promocion_id>/', promocion_detalle, name='promocion_detalle'),
    
    # PASO 2: Ruta unificada con filtros (Categoría, Marca, Proveedor)
    path("productos/", productos, name="productos"), 
    
    path("producto/<int:producto_id>/", producto_detalle, name="producto_detalle"),

    # Inventario
    path('inventario/', inventario_view, name='inventario'),

    # Cotizaciones
    path("cotizador/", cotizar_productos, name="cotizador"),
    path("cotizacion/<int:cotizacion_id>/", detalle_cotizacion, name="detalle_cotizacion"),
    
    # Cliente
    path("clientes/nuevo/", crear_cliente, name="crear_cliente"),
    
    # Login y logout
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),

    # cotizaciones por cliente
    path('cotizaciones/cliente/', cotizaciones_cliente, name='cotizaciones_cliente'),
    
    # eliminar cotización
    path('cotizacion/<int:pk>/eliminar/', eliminar_cotizacion, name='eliminar_cotizacion'),
    path("pedidos/", pedidos, name="pedidos"),
    path("pedidos/<int:pedido_id>/", detalle_pedido, name="detalle_pedido"),
    path("pedidos/<int:pedido_id>/eliminar/", eliminar_pedido, name="eliminar_pedido"),
    
    # Carrito y Pedidos
    path("producto/<int:producto_id>/agregar/", views.agregar_carrito, name="agregar_carrito"),
    path("pedido/<int:pedido_id>/confirmar/", views.confirmar_pedido, name="confirmar_pedido"),
    path('carrito/', carrito_view, name='carrito'), 
    path('carrito/eliminar/<int:producto_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('cotizacion/editar/<int:cotizacion_id>/', views.editar_cotizacion, name='editar_cotizacion'),
    path('inventario/', views.inventario_view, name='inventario'),
    path('cotizacion/convertir/<int:cotizacion_id>/', views.convertir_a_pedido, name='convertir_a_pedido'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)