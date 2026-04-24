from django.contrib import admin
from .models import Perfil, Vendedor, Cliente

# Registrar los modelos para verlos y gestionarlos
# desde el panel de administración de Django

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    # Columnas visibles en la lista del admin
    list_display = ['usuario', 'telefono', 'direccion']
    # Campo de búsqueda
    search_fields = ['usuario__username', 'telefono']


@admin.register(Vendedor)
class VendedorAdmin(admin.ModelAdmin):
    list_display = ['nombre_tienda', 'usuario', 'estado', 'fecha_registro']
    list_filter = ['estado']  # Filtro lateral por estado
    search_fields = ['nombre_tienda', 'usuario__username']


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'direccion_envio']
    search_fields = ['usuario__username']