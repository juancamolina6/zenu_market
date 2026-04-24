from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistroForm, EditarPerfilForm
from .models import Perfil, Vendedor, Cliente


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
# VISTA DE INICIO
# Página principal de ZenuMarket.
# ============================================================
def inicio(request):
    return render(request, 'inicio.html')