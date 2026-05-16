from django.urls import path
from . import views

# URLs de la app users
urlpatterns = [
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('perfil/', views.perfil, name='perfil'),
    
    # Panel del vendedor
    path('vender/', views.solicitar_vendedor, name='solicitar_vendedor'),
    path('vender/pendiente/', views.vendedor_pendiente, name='vendedor_pendiente'),
    path('vendedor/dashboard/', views.dashboard_vendedor, name='dashboard_vendedor'),
    path('vendedor/productos/', views.mis_productos_panel, name='mis_productos_panel'),
    path('vendedor/productos/<int:pk>/editar/', views.editar_producto, name='editar_producto'),
    path('vendedor/pedidos/', views.mis_pedidos_vendedor, name='mis_pedidos_vendedor'),
    path('vendedor/pedidos/<int:pedido_id>/estado/', views.actualizar_estado_pedido, name='actualizar_estado_pedido'),
]