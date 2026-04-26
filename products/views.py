from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Producto, Categoria
from .forms import ProductoForm
from users.models import Vendedor


# ============================================================
# LISTA DE PRODUCTOS
# Página principal del catálogo. Soporta búsqueda y filtro
# por categoría. Complejidad: O(n) donde n = productos.
# ============================================================
def lista_productos(request):
    # Empezar con todos los productos activos
    productos = Producto.objects.filter(estado='activo').select_related('categoria', 'vendedor')

    # Filtro por categoría si viene en la URL ej: ?categoria=ropa
    categoria_slug = request.GET.get('categoria')
    categoria_activa = None
    if categoria_slug:
        categoria_activa = get_object_or_404(Categoria, slug=categoria_slug)
        productos = productos.filter(categoria=categoria_activa)

    # Búsqueda por nombre o descripción si viene en la URL ej: ?q=zapatos
    # Q permite combinar condiciones con OR (|)
    busqueda = request.GET.get('q')
    if busqueda:
        productos = productos.filter(
            Q(nombre__icontains=busqueda) |       # busca en el nombre
            Q(descripcion__icontains=busqueda)    # o en la descripción
        )

    categorias = Categoria.objects.all()

    return render(request, 'products/lista.html', {
        'productos': productos,
        'categorias': categorias,
        'categoria_activa': categoria_activa,
        'busqueda': busqueda,
    })


# ============================================================
# DETALLE DE PRODUCTO
# Muestra toda la información de un producto específico.
# get_object_or_404: si el producto no existe retorna error 404
# Complejidad: O(1) búsqueda por ID con índice.
# ============================================================
def detalle_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk, estado='activo')
    return render(request, 'products/detalle.html', {'producto': producto})


# ============================================================
# CREAR PRODUCTO
# Solo disponible para usuarios que sean Vendedores.
# ============================================================
@login_required
def crear_producto(request):
    # Verificar que el usuario tiene perfil de Vendedor
    try:
        vendedor = Vendedor.objects.get(usuario=request.user)
    except Vendedor.DoesNotExist:
        messages.error(request, 'Necesitas ser vendedor para publicar productos.')
        return redirect('lista_productos')

    if request.method == 'POST':
        # request.FILES contiene los archivos subidos (imagen)
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save(commit=False)  # no guardar aún
            producto.vendedor = vendedor         # asignar el vendedor
            producto.save()
            messages.success(request, f'Producto "{producto.nombre}" publicado correctamente.')
            return redirect('detalle_producto', pk=producto.pk)
    else:
        form = ProductoForm()

    return render(request, 'products/crear.html', {'form': form})


# ============================================================
# MIS PRODUCTOS
# Lista los productos del vendedor logueado.
# ============================================================
@login_required
def mis_productos(request):
    try:
        vendedor = Vendedor.objects.get(usuario=request.user)
        productos = Producto.objects.filter(vendedor=vendedor)
    except Vendedor.DoesNotExist:
        productos = []

    return render(request, 'products/mis_productos.html', {'productos': productos})