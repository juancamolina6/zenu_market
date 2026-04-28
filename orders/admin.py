from django.contrib import admin
from .models import Carrito, LineaCarrito, Pedido, LineaPedido


class LineaCarritoInline(admin.TabularInline):
    # Muestra las líneas del carrito dentro del carrito en el admin
    model = LineaCarrito
    extra = 0


class LineaPedidoInline(admin.TabularInline):
    # Muestra las líneas del pedido dentro del pedido en el admin
    model = LineaPedido
    extra = 0
    readonly_fields = ['nombre_producto', 'precio_unitario', 'cantidad']


@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'fecha_creacion']
    inlines = [LineaCarritoInline]


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'estado', 'total', 'fecha']
    list_filter = ['estado']
    # Permite cambiar el estado del pedido directo desde la lista
    list_editable = ['estado']
    inlines = [LineaPedidoInline]