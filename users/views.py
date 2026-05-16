from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistroForm, EditarPerfilForm,SolicitudVendedorForm
from .models import Perfil, Vendedor, Cliente
from products.models import Producto, Categoria
from orders.models import LineaPedido, Pedido

# ============================================================
# VISTA DE REGISTRO
# Muestra el formulario y procesa el registro de nuevos usuarios.
# Crea automáticamente el Perfil, Cliente y Vendedor si aplica.
# ============================================================
def registro(request):

    # Si el usuario ya está logueado, redirigir al inicio
    if request.user.is_authenticated:
        return redirect('inicio')

    if request.method == 'POST':
        # Llenar el formulario con los datos enviados
        form = RegistroForm(request.POST)

        if form.is_valid():
            # Guardar el usuario en la base de datos
            user = form.save()

            # Crear el Perfil asociado al nuevo usuario
            Perfil.objects.create(
                usuario=user,
                telefono=form.cleaned_data.get('telefono', '')
            )

            # Crear el Cliente (todo usuario puede comprar)
            Cliente.objects.create(usuario=user)

            # Si eligió ser vendedor, crear también ese perfil
            if form.cleaned_data.get('ser_vendedor'):
                Vendedor.objects.create(
                    usuario=user,
                    nombre_tienda=form.cleaned_data.get('nombre_tienda')
                )

            # Iniciar sesión automáticamente después del registro
            login(request, user)

            # Mensaje de bienvenida que aparece en la siguiente página
            messages.success(request, f'¡Bienvenido a ZenuMarket, {user.first_name}!')
            return redirect('inicio')
    else:
        # Si es GET, mostrar el formulario vacío
        form = RegistroForm()

    return render(request, 'users/registro.html', {'form': form})


# ============================================================
# VISTA DE LOGIN
# Autentica al usuario con username y contraseña.
# ============================================================
def login_view(request):

    if request.user.is_authenticated:
        return redirect('inicio')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # authenticate verifica si el usuario y contraseña son correctos
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'¡Hola de nuevo, {user.first_name or user.username}!')
            return redirect('inicio')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'users/login.html')


# ============================================================
# VISTA DE LOGOUT
# Cierra la sesión y redirige al login.
# ============================================================
def logout_view(request):
    logout(request)
    messages.info(request, 'Sesión cerrada correctamente.')
    return redirect('login')


# ============================================================
# VISTA DE PERFIL
# Muestra y permite editar los datos del usuario logueado.
# @login_required redirige al login si el usuario no está autenticado.
# ============================================================
@login_required
def perfil(request):
    # Obtener o crear el perfil del usuario actual
    perfil_usuario, _ = Perfil.objects.get_or_create(usuario=request.user)

    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, instance=perfil_usuario)

        if form.is_valid():
            # Actualizar los campos del modelo User
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()

            # Guardar los cambios del perfil
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('perfil')
    else:
        # Prellenar el formulario con los datos actuales
        form = EditarPerfilForm(
            instance=perfil_usuario,
            initial={
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
            }
        )

    # Verificar si el usuario es vendedor para mostrarlo en el perfil
    es_vendedor = Vendedor.objects.filter(usuario=request.user).exists()

    return render(request, 'users/perfil.html', {
        'form': form,
        'es_vendedor': es_vendedor
    })


# ============================================================
# VISTA — SOLICITAR SER VENDEDOR
# Muestra el formulario para registrarse como vendedor.
# El vendedor queda en estado "pendiente" hasta que
# el administrador lo apruebe desde el panel admin.
# ============================================================
@login_required
def solicitar_vendedor(request):

    # Si ya es vendedor, redirigir según su estado
    try:
        vendedor = Vendedor.objects.get(usuario=request.user)
        if vendedor.estado == 'activo':
            return redirect('dashboard_vendedor')
        elif vendedor.estado == 'pendiente':
            # Ya solicitó, mostrar pantalla de espera
            return render(request, 'users/vendedor_pendiente.html', {
                'vendedor': vendedor
            })
    except Vendedor.DoesNotExist:
        pass

    if request.method == 'POST':
        form = SolicitudVendedorForm(request.POST)
        if form.is_valid():
            vendedor = form.save(commit=False)
            vendedor.usuario = request.user
            vendedor.estado = 'pendiente'  # siempre empieza pendiente
            vendedor.save()
            messages.success(
                request,
                '¡Solicitud enviada! Revisaremos tu información y te notificaremos pronto.'
            )
            return redirect('vendedor_pendiente')
    else:
        form = SolicitudVendedorForm()

    return render(request, 'users/solicitar_vendedor.html', {'form': form})


# ============================================================
# VISTA — PENDIENTE DE APROBACIÓN
# Página informativa mientras el admin revisa la solicitud.
# ============================================================
@login_required
def vendedor_pendiente(request):
    try:
        vendedor = Vendedor.objects.get(usuario=request.user)
    except Vendedor.DoesNotExist:
        return redirect('solicitar_vendedor')

    if vendedor.estado == 'activo':
        return redirect('dashboard_vendedor')

    return render(request, 'users/vendedor_pendiente.html', {'vendedor': vendedor})


# ============================================================
# DECORADOR PERSONALIZADO — verificar que sea vendedor activo
# Reutilizable en todas las vistas del panel del vendedor.
# ============================================================
def vendedor_activo_required(view_func):
    """
    Decorator personalizado: verifica que el usuario
    sea un vendedor con estado activo antes de entrar
    a cualquier vista del panel.
    Patrón Decorator de GoF aplicado manualmente.
    """
    @login_required
    def wrapper(request, *args, **kwargs):
        try:
            vendedor = Vendedor.objects.get(
                usuario=request.user,
                estado='activo'
            )
            request.vendedor = vendedor  # disponible en la vista
            return view_func(request, *args, **kwargs)
        except Vendedor.DoesNotExist:
            messages.error(
                request,
                'Necesitas ser un vendedor verificado para acceder a esta sección.'
            )
            return redirect('solicitar_vendedor')
    return wrapper


# ============================================================
# VISTA — DASHBOARD DEL VENDEDOR
# Resumen general: productos, ventas y pedidos recientes.
# ============================================================
@vendedor_activo_required
def dashboard_vendedor(request):
    vendedor = request.vendedor

    # Métricas del vendedor — O(n) donde n = productos del vendedor
    productos = Producto.objects.filter(vendedor=vendedor)
    total_productos = productos.count()
    productos_activos = productos.filter(estado='activo').count()
    productos_agotados = productos.filter(estado='agotado').count()

    # Pedidos que contienen productos de este vendedor
    # LineaPedido conecta Pedido con Producto
    lineas = LineaPedido.objects.filter(
        producto__vendedor=vendedor
    ).select_related('pedido', 'producto').order_by('-pedido__fecha')[:10]

    # Calcular ingresos totales del vendedor
    # O(n) donde n = líneas de pedido del vendedor
    ingresos_totales = sum(
        linea.subtotal() for linea in
        LineaPedido.objects.filter(producto__vendedor=vendedor)
    )

    return render(request, 'users/dashboard_vendedor.html', {
        'vendedor': vendedor,
        'total_productos': total_productos,
        'productos_activos': productos_activos,
        'productos_agotados': productos_agotados,
        'lineas_recientes': lineas,
        'ingresos_totales': ingresos_totales,
    })


# ============================================================
# VISTA — MIS PRODUCTOS (panel vendedor)
# Lista todos los productos del vendedor con opciones
# para editar, activar, desactivar o ver stock.
# ============================================================
@vendedor_activo_required
def mis_productos_panel(request):
    vendedor = request.vendedor
    productos = Producto.objects.filter(
        vendedor=vendedor
    ).order_by('-fecha_creacion')

    return render(request, 'users/mis_productos_panel.html', {
        'vendedor': vendedor,
        'productos': productos,
    })


# ============================================================
# VISTA — EDITAR PRODUCTO
# Permite al vendedor modificar sus propios productos.
# Valida que el producto pertenezca al vendedor logueado.
# ============================================================
@vendedor_activo_required
def editar_producto(request, pk):
    vendedor = request.vendedor

    # get_object_or_404: si el producto no existe o no es del vendedor → 404
    producto = get_object_or_404(Producto, pk=pk, vendedor=vendedor)

    # Importar el formulario de productos
    from products.forms import ProductoForm

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, f'"{producto.nombre}" actualizado correctamente.')
            return redirect('mis_productos_panel')
    else:
        form = ProductoForm(instance=producto)

    return render(request, 'users/editar_producto.html', {
        'form': form,
        'producto': producto,
        'vendedor': vendedor,
    })


# ============================================================
# VISTA — MIS PEDIDOS (panel vendedor)
# Muestra los pedidos que incluyen productos del vendedor.
# El vendedor puede cambiar el estado de cada pedido.
# ============================================================
@vendedor_activo_required
def mis_pedidos_vendedor(request):
    vendedor = request.vendedor

    # Obtener los pedidos únicos que tienen productos de este vendedor
    pedidos_ids = LineaPedido.objects.filter(
        producto__vendedor=vendedor
    ).values_list('pedido_id', flat=True).distinct()

    pedidos = Pedido.objects.filter(
        id__in=pedidos_ids
    ).prefetch_related('lineas').order_by('-fecha')

    return render(request, 'users/mis_pedidos_vendedor.html', {
        'vendedor': vendedor,
        'pedidos': pedidos,
    })


# ============================================================
# VISTA — ACTUALIZAR ESTADO DEL PEDIDO
# El vendedor marca el pedido como "en camino" o "entregado".
# ============================================================
@vendedor_activo_required
def actualizar_estado_pedido(request, pedido_id):
    if request.method == 'POST':
        pedido = get_object_or_404(Pedido, pk=pedido_id)
        nuevo_estado = request.POST.get('estado')

        # Solo permitir cambios válidos de estado
        estados_permitidos = ['en_camino', 'entregado']
        if nuevo_estado in estados_permitidos:
            pedido.estado = nuevo_estado
            pedido.save()
            messages.success(
                request,
                f'Pedido #{pedido.pk} actualizado a "{pedido.get_estado_display()}".'
            )

    return redirect('mis_pedidos_vendedor')

# ============================================================
# VISTA DE INICIO
# Página principal de ZenuMarket.
# ============================================================
def inicio(request):
    # Los 8 productos más recientes para la página de inicio
    productos_destacados = Producto.objects.filter(
        estado='activo'
    ).select_related('vendedor', 'categoria')[:8]

    # Todas las categorías para el menú de inicio
    categorias = Categoria.objects.all()

    return render(request, 'inicio.html', {
        'productos_destacados': productos_destacados,
        'categorias': categorias,
    })