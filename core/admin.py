from django.contrib import admin
from .models import Producto, Promocion, Cliente, Categoria, Marca, Proveedor
from import_export.admin import ImportExportModelAdmin
from .resources import ProductoResource
from .models import PromocionTicker

@admin.register(Producto)
class ProductoAdmin(ImportExportModelAdmin): # Habilita Import/Export
    resource_class = ProductoResource
    list_display = (
        "nombre", "clave", "categoria", "marca", "proveedor", 
        "departamento", "precio", "existencia", "color", 
        "imagen", "creado",
    )
    # Importante: usar __nombre para campos ForeignKey en search_fields
    search_fields = (
        "nombre", "clave", "categoria__nombre", 
        "marca__nombre", "proveedor__nombre"
    )
    # Filtros laterales para facilitar la navegación
    list_filter = ("categoria", "marca", "proveedor", "departamento")

@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre",)

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ("nombre", "contacto")
    search_fields = ("nombre",)

@admin.register(Cliente)
class ClienteAdmin(ImportExportModelAdmin): 
    list_display = ("nombre", "correo", "telefono", "rfc", "ciudad")
    search_fields = ("nombre", "correo", "rfc")

@admin.register(Promocion)   
class PromocionAdmin(admin.ModelAdmin): 
    list_display = ("titulo", "descuento", "vigente_hasta")

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "descripcion")
    search_fields = ("nombre",)

admin.site.register(PromocionTicker)