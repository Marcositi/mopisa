from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Producto, Promocion, Cotizacion, CotizacionItem, Cliente, Pedido, PedidoItem, Marca, Proveedor, Categoria, PromocionTicker
from decimal import Decimal
from django.contrib import messages
from django.db.models import Q
from .forms import ClienteForm
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db import transaction
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# --- FUNCIONES DE PERMISOS ---
def es_vendedor_o_admin(user): 
    return user.is_superuser or user.groups.filter(name='Vendedores').exists()

def es_admin(user):
    return user.is_staff or user.is_superuser

# --- VISTAS GENERALES ---
def inicio(request):
    promociones = PromocionTicker.objects.filter(activo=True)
    # ... tus otras variables (categorias, productos, etc)
    return render(request, 'inicio.html', {'promociones': promociones})

@user_passes_test(es_admin, login_url="no_autorizado")
@login_required
def inventario_view(request):
    query = request.GET.get('q', '').strip()
    cat_id = request.GET.get('categoria', '').strip()
    categorias = Categoria.objects.all()

    if not query and not cat_id:
        productos = Producto.objects.none()
    else:
        productos = Producto.objects.all()
        if query:
            productos = productos.filter(
                Q(descripcion__icontains=query) | 
                Q(clave__icontains=query) |
                Q(departamento__icontains=query)
            )
        if cat_id:
            productos = productos.filter(categoria_id=cat_id)

    return render(request, 'inventario.html', {
        'productos': productos,
        'categorias': categorias
    })

# --- VISTAS DE PRODUCTOS ---
def productos(request):
    query = request.GET.get('q', '')
    categoria_nombre = request.GET.get('categoria', '')
    marca_nombre = request.GET.get('marca', '')
    proveedor_nombre = request.GET.get('proveedor', '')

    productos_list = Producto.objects.all()

    if query:
        productos_list = productos_list.filter(
            Q(nombre__icontains=query) | 
            Q(descripcion__icontains=query) |
            Q(clave__icontains=query)
        )
    if categoria_nombre:
        productos_list = productos_list.filter(categoria__nombre=categoria_nombre)
    if marca_nombre:
        productos_list = productos_list.filter(marca__nombre=marca_nombre)
    if proveedor_nombre:
        productos_list = productos_list.filter(proveedor__nombre=proveedor_nombre)

    paginator = Paginator(productos_list, 12) 
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
        'categoria': categoria_nombre,
        'marca': marca_nombre,
        'proveedor': proveedor_nombre,
        'categorias': Categoria.objects.all(),
        'marcas': Marca.objects.all(),
        'proveedores': Proveedor.objects.all(),
    }
    return render(request, 'productos.html', context)

def producto_detalle(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    return render(request, 'producto_detalle.html', {'producto': producto})

# --- PROMOCIONES ---
def lista_promociones(request): 
    promociones = Promocion.objects.all() 
    return render(request, 'promociones.html', {'promociones': promociones})

def promocion_detalle(request, promocion_id): 
    promocion = get_object_or_404(Promocion, id=promocion_id)  
    return render(request, 'promocion_detalle.html', {'promocion': promocion})

# --- COTIZADOR ---
def cotizar_productos(request):
    query = request.GET.get("q")
    productos_res = Producto.objects.none()

    if query:
        productos_res = Producto.objects.filter(
            Q(nombre__icontains=query) | Q(clave__icontains=query)
        )

    if "cotizacion_items" not in request.session:
        request.session["cotizacion_items"] = {}

    if request.method == "POST":
        carrito = request.session["cotizacion_items"]
        for prod in productos_res:
            cantidad_val = request.POST.get(f"cantidad_{prod.id}", 0)
            if cantidad_val:
                cantidad = int(cantidad_val)
                if cantidad > 0:
                    carrito[str(prod.id)] = carrito.get(str(prod.id), 0) + cantidad

        request.session["cotizacion_items"] = carrito
        request.session.modified = True

        if "agregar" in request.POST:
            messages.success(request, "Productos agregados al carrito.")
            return redirect("cotizador")

        if "generar" in request.POST:
            cliente = Cliente.objects.filter(usuario=request.user).first() if request.user.is_authenticated else None
            if request.user.is_authenticated and not cliente:
                messages.error(request, "No tienes un cliente dado de alta.")
                return redirect("crear_cliente")

            id_viejo = request.session.get("editando_cotizacion_id")
            if id_viejo:
                Cotizacion.objects.filter(id=id_viejo).delete()
                del request.session["editando_cotizacion_id"]

            cotizacion = Cotizacion.objects.create(cliente=cliente, total=0)
            total = Decimal("0.00")
            for p_id, cant in carrito.items():
                try:
                    p = Producto.objects.get(id=p_id)
                    sub = p.precio * cant
                    CotizacionItem.objects.create(cotizacion=cotizacion, producto=p, cantidad=cant, subtotal=sub)
                    total += sub
                except Producto.DoesNotExist: continue

            cotizacion.total = total
            cotizacion.save()
            request.session["cotizacion_items"] = {}
            request.session.modified = True
            messages.success(request, f"Cotización #{cotizacion.id} guardada.")
            return redirect("detalle_cotizacion", cotizacion_id=cotizacion.id)

    return render(request, "cotizacion.html", {"productos": productos_res})

# --- CLIENTES Y CARRITO ---
def crear_cliente(request):
    if request.method == "POST":
        rfc = request.POST.get("rfc")
        if Cliente.objects.filter(rfc=rfc).exists(): 
            messages.error(request, "Ya existe un cliente con ese RFC.") 
            return render(request, "crear_cliente.html")
        
        user = User.objects.create_user(
            username=request.POST.get("username"), 
            email=request.POST.get("correo"), 
            password=request.POST.get("password")
        )
        Cliente.objects.create(
            nombre=request.POST.get("nombre"),
            correo=request.POST.get("correo"),
            telefono=request.POST.get("telefono"),
            direccion=request.POST.get("direccion"),
            rfc=rfc,
            usuario=user
        )
        messages.success(request, "Cliente creado correctamente.")
        return redirect("login")
    return render(request, "crear_cliente.html")

def carrito_view(request):
    carrito = request.session.get("cotizacion_items", {})
    items_list = []
    total = 0
    for p_id, cant in carrito.items():
        p = get_object_or_404(Producto, id=p_id)
        sub = p.precio * cant
        items_list.append({"producto": p, "cantidad": cant, "subtotal": sub})
        total += sub
    return render(request, "carrito.html", {"productos": items_list, "total": total})

def eliminar_del_carrito(request, producto_id):
    carrito = request.session.get('cotizacion_items', {})
    if str(producto_id) in carrito:
        del carrito[str(producto_id)]
        request.session['cotizacion_items'] = carrito
        request.session.modified = True
        messages.success(request, "Eliminado.")
    return redirect('carrito')

# --- PEDIDOS ---
@login_required
def pedidos(request):
    if request.user.is_staff or request.user.is_superuser:
        # Los admins ven todo lo que no sea borrador
        pedidos_list = Pedido.objects.exclude(estado="pendiente").order_by("-fecha")
    else:
        # Intentamos obtener el perfil del cliente de forma segura
        cliente_perfil = Cliente.objects.filter(usuario=request.user).first()
        
        if not cliente_perfil:
            # Si Marcos no tiene perfil de Cliente, lo mandamos a crearlo
            messages.warning(request, "Por favor, completa tus datos de cliente para ver tus pedidos.")
            return redirect("crear_cliente")
        
        # Filtramos los pedidos del cliente encontrado
        pedidos_list = Pedido.objects.filter(cliente=cliente_perfil).order_by("-fecha")
    
    return render(request, "pedidos.html", {"pedidos": pedidos_list})
@login_required
def detalle_pedido(request, pedido_id):
    if request.user.is_staff or request.user.is_superuser:
        # Los admins pueden ver cualquier pedido
        pedido = get_object_or_404(Pedido, id=pedido_id)
    else:
        # Para clientes, buscamos primero su perfil
        cliente_perfil = get_object_or_404(Cliente, usuario=request.user)
        # Luego buscamos el pedido que le pertenezca a ese perfil específico
        pedido = get_object_or_404(Pedido, id=pedido_id, cliente=cliente_perfil)
    
    return render(request, "detalle_pedido.html", {"pedido": pedido})

@login_required
def convertir_a_pedido(request, cotizacion_id):
    if request.method == "POST":
        cliente_instancia = get_object_or_404(Cliente, usuario=request.user)
        cotizacion = get_object_or_404(Cotizacion, id=cotizacion_id, cliente=cliente_instancia)
        
        try:
            with transaction.atomic():
                # 1. Crear el Pedido
                nuevo_pedido = Pedido.objects.create(
                    cliente=cliente_instancia, 
                    total=cotizacion.total,
                    estado="procesado"
                )

                # 2. Copiar los productos
                for item in cotizacion.items.all():
                    PedidoItem.objects.create(
                        pedido=nuevo_pedido,
                        producto=item.producto,
                        cantidad=item.cantidad,
                        precio_unitario=item.producto.precio
                    )

                # 3. Marcar cotización como convertida (la oculta de la lista)
                cotizacion.convertida_en_pedido = True
                cotizacion.save()

                # --- LÓGICA DE NOTIFICACIÓN EN TIEMPO REAL ---
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    'notifications',  # El grupo que definiste en tu Consumer
                    {
                        'type': 'send_notification', # Debe coincidir con el método en tu Consumer
                        'titulo': '¡Nuevo Pedido Confirmado! 📦',
                        'mensaje': f'La cotización #{cotizacion.id} ha sido convertida',
                        'total': str(cotizacion.total),
                        'cliente': cliente_instancia.usuario.get_full_name() or cliente_instancia.usuario.username
                    }
                )

            messages.success(request, f"¡Pedido #{nuevo_pedido.id} generado con éxito!")
            return redirect('pedidos')

        except Exception as e:
            messages.error(request, f"Error: {e}")
            return redirect('cotizaciones_cliente')
        
# --- OTRAS VISTAS ---
def detalle_cotizacion(request, cotizacion_id):
    cotizacion = get_object_or_404(Cotizacion, id=cotizacion_id)
    return render(request, "detalle_cotizacion.html", {"cotizacion": cotizacion})

def cotizaciones_cliente(request):
    if request.user.is_authenticated:
        # Filtramos por el usuario actual Y que la cotización NO esté convertida
        cotizaciones = Cotizacion.objects.filter(
            cliente__usuario=request.user, 
            convertida_en_pedido=False
        ).order_by('-fecha') # Las más recientes primero
    else:
        cotizaciones = Cotizacion.objects.none()
        
    return render(request, "cotizaciones_cliente.html", {"cotizaciones": cotizaciones})
def eliminar_cotizacion(request, pk):
    cotizacion = get_object_or_404(Cotizacion, pk=pk)
    if request.method == "POST":
        cotizacion.delete()
        messages.success(request, "Cotización eliminada.")
    return redirect('cotizaciones_cliente')

@login_required
def eliminar_pedido(request, pedido_id):
    if request.user.is_staff or request.user.is_superuser:
        pedido = get_object_or_404(Pedido, id=pedido_id)
    else:
        pedido = get_object_or_404(Pedido, id=pedido_id, cliente__usuario=request.user)
    
    if request.method == "POST":
        pedido.delete()
        messages.success(request, "Pedido eliminado correctamente.")
        return redirect("pedidos")
    return render(request, "confirmar_eliminar.html", {"objeto": pedido})

def editar_cotizacion(request, cotizacion_id):
    cotizacion = get_object_or_404(Cotizacion, id=cotizacion_id)
    carrito = {}
    for item in cotizacion.cotizacionitem_set.all():
        carrito[str(item.producto.id)] = item.cantidad
    
    request.session["cotizacion_items"] = carrito
    request.session["editando_cotizacion_id"] = cotizacion.id 
    request.session.modified = True
    
    messages.info(request, f"Editando Cotización #{cotizacion.id}. Al guardar, la anterior se actualizará.")
    return redirect('carrito')

@login_required(login_url="login")
def agregar_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    try:
        cliente = Cliente.objects.get(usuario=request.user)
    except Cliente.DoesNotExist:
        messages.error(request, "Debes completar tu perfil de cliente primero.")
        return redirect("crear_cliente")

    pedido, creado = Pedido.objects.get_or_create(cliente=cliente, estado="pendiente", defaults={"total": 0})
    detalle, creado_detalle = PedidoItem.objects.get_or_create(
        pedido=pedido, producto=producto,
        defaults={"cantidad": 1, "precio_unitario": producto.precio}
    )
    if not creado_detalle:
        detalle.cantidad += 1
        detalle.save()

    pedido.total = sum(item.subtotal() for item in pedido.pedidoitem_set.all())
    pedido.save()
    messages.success(request, f"{producto.nombre} añadido al carrito.")
    return redirect("productos")

@login_required
def confirmar_pedido(request, pedido_id):
    # 1. Obtenemos el perfil del cliente logueado
    cliente_perfil = get_object_or_404(Cliente, usuario=request.user)
    
    # 2. Buscamos el pedido asegurándonos que le pertenezca a este cliente
    # Quitamos filtros de estado para que el 404 no salte si ya está procesado
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=cliente_perfil)
    
    # 3. Cambiamos el estado
    pedido.estado = "procesado"
    pedido.save()
    
    messages.success(request, f"¡Pedido #{pedido.id} confirmado con éxito!")
    return redirect("pedidos")