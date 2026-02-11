from .models import Producto

def carrito_context(request):
    """
    Context processor que devuelve el número de productos en el carrito
    y el total acumulado.
    """
    carrito = request.session.get("cotizacion_items", {})
    total_items = sum(carrito.values())
    total_precio = 0

    for producto_id, cantidad in carrito.items():
        try:
            producto = Producto.objects.get(id=producto_id)
            total_precio += producto.precio * cantidad
        except Producto.DoesNotExist:
            continue

    return {
        "carrito_count": total_items,
        "carrito_total": total_precio,
    }
