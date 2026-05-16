from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Carrito, LineaCarrito, Pedido, LineaPedido
from products.models import Producto


# ============================================================
# VER CARRITO
# Muestra todos los productos que el usuario tiene
# en su carrito con cantidades y totales.
# ============================================================
@login_required
def ver_carrito(request):
    # get_or_create: si no tiene carrito lo crea automáticamente
    # Complejidad O(1) para obtener el carrito por usuario
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    lineas = carrito.lineas.select_related('producto').all()

    return render(request, 'orders/carrito.html', {
        'carrito': carrito,
        'lineas': lineas,
    })


# ============================================================
# AGREGAR AL CARRITO
# Agrega un producto al carrito. Si ya existe,
# incrementa la cantidad en 1.
# ============================================================
@login_required
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id, estado='activo')

    if not producto.tiene_stock():
        messages.error(request, f'"{producto.nombre}" no tiene stock disponible.')
        return redirect('detalle_producto', pk=producto_id)

    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)

    # get_or_create: si la línea existe la obtiene, si no la crea
    linea, creada = LineaCarrito.objects.get_or_create(
        carrito=carrito,
        producto=producto
    )

    if not creada:
        # El producto ya estaba en el carrito, solo aumentar cantidad
        if linea.cantidad < producto.stock:
            linea.cantidad += 1
            linea.save()
        else:
            messages.warning(request, 'No hay más stock disponible.')
            return redirect('ver_carrito')

    messages.success(request, f'"{producto.nombre}" agregado al carrito.')
    return redirect('ver_carrito')


# ============================================================
# ACTUALIZAR CANTIDAD EN EL CARRITO
# Aumenta o disminuye la cantidad de un producto.
# Si la cantidad llega a 0 elimina la línea.
# ============================================================
@login_required
def actualizar_cantidad(request, linea_id, accion):
    """
    accion puede ser 'aumentar' o 'disminuir'.
    Si stock llega a 0 con disminuir, elimina la línea.
    """
    linea = get_object_or_404(
        LineaCarrito,
        pk=linea_id,
        carrito__usuario=request.user
    )

    if accion == 'aumentar':
        # Verificar que no supere el stock disponible
        if linea.cantidad < linea.producto.stock:
            linea.cantidad += 1
            linea.save()
        else:
            messages.warning(request, 'No hay más stock disponible.')

    elif accion == 'disminuir':
        if linea.cantidad > 1:
            linea.cantidad -= 1
            linea.save()
        else:
            # Si ya está en 1 y baja, eliminar la línea
            linea.delete()
            messages.success(request, 'Producto eliminado del carrito.')

    return redirect('ver_carrito')

# ============================================================
# ELIMINAR DEL CARRITO
# Elimina una línea completa del carrito.
# ============================================================
@login_required
def eliminar_del_carrito(request, linea_id):
    linea = get_object_or_404(LineaCarrito, pk=linea_id, carrito__usuario=request.user)
    nombre = linea.producto.nombre
    linea.delete()
    messages.success(request, f'"{nombre}" eliminado del carrito.')
    return redirect('ver_carrito')


# ============================================================
# CONFIRMAR PEDIDO
# Convierte el carrito en un pedido formal.
# Guarda el snapshot de cada producto (nombre y precio)
# por si cambian en el futuro.
# ============================================================
@login_required
def confirmar_pedido(request):
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    lineas = carrito.lineas.select_related('producto').all()

    # Validar que el carrito no esté vacío
    if not lineas.exists():
        messages.error(request, 'Tu carrito está vacío.')
        return redirect('ver_carrito')

    if request.method == 'POST':
        direccion = request.POST.get('direccion_entrega', '').strip()

        if not direccion:
            messages.error(request, 'Debes ingresar una dirección de entrega.')
            return redirect('confirmar_pedido')

        # Calcular el total del pedido — O(n) donde n = líneas del carrito
        total = carrito.calcular_total()

        # Crear el pedido
        pedido = Pedido.objects.create(
            usuario=request.user,
            direccion_entrega=direccion,
            total=total
        )

        # Crear las líneas del pedido como snapshot de cada producto
        for linea in lineas:
            LineaPedido.objects.create(
                pedido=pedido,
                producto=linea.producto,
                nombre_producto=linea.producto.nombre,  # snapshot del nombre
                precio_unitario=linea.producto.precio,  # snapshot del precio
                cantidad=linea.cantidad
            )

        # Confirmar el pedido y descontar stock
        pedido.pagar()

        # Vaciar el carrito después de confirmar
        carrito.vaciar()

        messages.success(request, f'¡Pedido #{pedido.pk} confirmado! Pronto llegará a tu puerta.')
        return redirect('mis_pedidos')

    # GET: mostrar resumen antes de confirmar
    return render(request, 'orders/confirmar.html', {
        'carrito': carrito,
        'lineas': lineas,
    })


# ============================================================
# MIS PEDIDOS
# Historial de pedidos del usuario logueado.
# ============================================================
@login_required
def mis_pedidos(request):
    pedidos = Pedido.objects.filter(
        usuario=request.user
    ).prefetch_related('lineas')

    return render(request, 'orders/mis_pedidos.html', {'pedidos': pedidos})