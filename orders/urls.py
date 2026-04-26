from django.urls import path
from . import views

urlpatterns = [
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/eliminar/<int:linea_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('pedido/confirmar/', views.confirmar_pedido, name='confirmar_pedido'),
    path('pedidos/', views.mis_pedidos, name='mis_pedidos'),
]