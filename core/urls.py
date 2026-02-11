from django.contrib.auth import views as auth_views
from django.urls import path
from . import views


urlpatterns = [
    path('', views.inicio, name='inicio'), 
    path('productos/', views.lista_productos, name='productos'),
    path('productos/<int:producto_id>/', views.producto_detalle, name='producto_detalle'), 
    path('promociones/', views.lista_promociones, name='promociones'), 
    path('promociones/<int:promo_id>/', views.promocion_detalle, name='promocion_detalle'),
    path("clientes/nuevo/", views.crear_cliente, name="crear_cliente"),
    path("cotizador/", views.cotizar_productos, name="cotizador"), 
    path("cotizacion/<int:cotizacion_id>/", views.detalle_cotizacion, name="detalle_cotizacion"),
    path("cotizaciones/", views.cotizaciones_cliente, name="cotizaciones_cliente"),
    path('cotizacion/<int:pk>/eliminar/', views.eliminar_cotizacion, name='eliminar_cotizacion'),
    path("accounts/login/", auth_views.LoginView.as_view(
        template_name="login.html",
        redirect_authenticated_user=True
        ), name="login"), 
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"), 
    path("cotizacion/<int:pk>/print/", views.cotizacion_print_view, name="cotizacion_print"), 
    path('cotizacion/convertir/<int:cotizacion_id>/', views.convertir_a_pedido, name='convertir_a_pedido'),
]
