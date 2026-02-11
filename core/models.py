from django.db import models
from django.contrib.auth.models import User

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ["nombre"]
    def __str__(self): return self.nombre

class Marca(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.nombre

class Proveedor(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    contacto = models.CharField(max_length=150, blank=True, null=True)
    def __str__(self): return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    clave = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    existencia = models.IntegerField(default=0)
    
    # Relaciones
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name="productos")
    marca = models.ForeignKey(Marca, on_delete=models.SET_NULL, null=True, blank=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True)
    
    color = models.CharField(max_length=50, blank=True, null=True)
    departamento = models.CharField(max_length=100, blank=True, null=True)
    imagen = models.ImageField(upload_to="productos/", blank=True, null=True)
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} ({self.categoria})"

class Promocion(models.Model):
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    descuento = models.DecimalField(max_digits=5, decimal_places=2, help_text="Porcentaje de descuento")
    imagen = models.ImageField(upload_to='promociones/', blank=True, null=True)
    vigente_hasta = models.DateField()

    def __str__(self):
        return self.titulo


class Cliente(models.Model): 
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField(max_length=200) 
    correo = models.EmailField(unique=True) 
    telefono = models.CharField(max_length=20, blank=True, null=True) 
    direccion = models.TextField(blank=True, null=True) 
    estado = models.CharField(max_length=100, blank=True, null=True)
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    codigo_postal = models.CharField(max_length=10, blank=True, null=True)
    rfc = models.CharField(max_length=13, unique=True)
    fecha_registro = models.DateTimeField(auto_now_add=True, null=True, blank=True) 
    
    def __str__(self): 
        return f"{self.nombre} ({self.rfc})"


class Cotizacion(models.Model): 
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cotizaciones"
    ) 
    fecha = models.DateTimeField(auto_now_add=True) 
    total = models.DecimalField(max_digits=10, decimal_places=2)
    convertida_en_pedido = models.BooleanField(default=False)
        
    def __str__(self): 
        return f"Cotización #{self.id} - {self.cliente or 'Cliente Anónimo'}"


class CotizacionItem(models.Model): 
    cotizacion = models.ForeignKey(Cotizacion, related_name="items", on_delete=models.CASCADE) 
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE) 
    cantidad = models.PositiveIntegerField(default=1) 
    subtotal = models.DecimalField(max_digits=12, decimal_places=2) 
    
    def __str__(self): 
        return f"{self.producto.nombre} x {self.cantidad}"

class Pedido(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="pedidos")
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=[
        ("pendiente", "Pendiente"),
        ("procesado", "Procesado"),
        ("entregado", "Entregado"),
    ], default="pendiente")
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente.nombre}"


class PedidoItem(models.Model):
    pedido = models.ForeignKey(Pedido, related_name="items", on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"

class PromocionTicker(models.Model):
    texto = models.CharField(max_length=255, help_text="Escribe la oferta (ej: 20% de descuento en pinturas)")
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.texto






