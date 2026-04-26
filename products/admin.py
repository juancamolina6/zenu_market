from django.contrib import admin
from .models import Categoria, Producto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'slug']
    # prepopulated_fields: genera el slug automáticamente
    # desde el nombre mientras escribes en el admin
    prepopulated_fields = {'slug': ('nombre',)}
    search_fields = ['nombre']


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'vendedor', 'categoria', 'precio', 'stock', 'estado']
    list_filter = ['estado', 'categoria']
    search_fields = ['nombre', 'sku']
    # permite editar el estado directamente desde la lista
    list_editable = ['estado', 'stock']