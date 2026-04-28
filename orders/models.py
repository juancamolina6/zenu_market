from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from products.models import Producto


# ============================================================
# CARRITO
# Cada usuario tiene un carrito activo a la vez.
# Se crea automáticamente cuando el usuario agrega
# su primer producto. Corresponde a Carrito del UML.
# ============================================================
class Carrito(models.Model):

    # Un usuario tiene un solo carrito activo
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Carrito de {self.usuario.username}"

    def calcular_total(self):
        """
        Suma el subtotal de todas las líneas del carrito.
        Complejidad O(n) donde n = número de productos en el carrito.
        Corresponde a calcularTotal() del diagrama UML.
        """
        return sum(linea.subtotal() for linea in self.lineas.all())

    def total_items(self):
        """Retorna la cantidad total de items en el carrito."""
        return sum(linea.cantidad for linea in self.lineas.all())

    def vaciar(self):
        """
        Elimina todas las líneas del carrito.
        Corresponde a vaciar() del diagrama UML.
        """
        self.lineas.all().delete()


# ============================================================
# LÍNEA DE CARRITO
# Representa un producto dentro del carrito con su cantidad.
# Una línea por cada producto distinto agregado.
# ============================================================
class LineaCarrito(models.Model):

    # Cada línea pertenece a un carrito específico
    carrito = models.ForeignKey(
        Carrito,
        on_delete=models.CASCADE,
        related_name='lineas'  # permite carrito.lineas.all()
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE
    )
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre}"

    def subtotal(self):
        """
        Precio de esta línea = precio unitario × cantidad.
        Complejidad O(1): operación simple sin recorrer nada.
        """
        return self.producto.precio * self.cantidad


# ============================================================
# PEDIDO
# Se crea cuando el usuario confirma la compra del carrito.
# Guarda el estado del pedido durante todo su ciclo de vida.
# Corresponde a Pedido del diagrama UML.
# ============================================================
class Pedido(models.Model):

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),         # recién creado
        ('confirmado', 'Confirmado'),       # pago recibido
        ('en_camino', 'En camino'),         # despachado
        ('entregado', 'Entregado'),         # entrega exitosa
        ('cancelado', 'Cancelado'),         # cancelado
    ]

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='pedidos'
    )
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente'
    )
    # Dirección de entrega guardada al momento del pedido
    direccion_entrega = models.CharField(max_length=255)
    # Total guardado al momento de la compra
    # (el precio del producto puede cambiar después)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        ordering = ['-fecha']  # los más recientes primero

    def __str__(self):
        return f"Pedido #{self.pk} — {self.usuario.username} — {self.estado}"

    def pagar(self):
        """
        Confirma el pedido y descuenta el stock de cada producto.
        Corresponde a pagar() del diagrama UML.
        """
        for linea in self.lineas.all():
            linea.producto.actualizar_stock(linea.cantidad)
        self.estado = 'confirmado'
        self.save()


# ============================================================
# LÍNEA DE PEDIDO
# Snapshot del producto al momento de la compra.
# Guarda nombre y precio aunque el producto cambie después.
# Corresponde a LineaPedido del diagrama UML.
# ============================================================
class LineaPedido(models.Model):

    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='lineas'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.SET_NULL,  # si se elimina el producto, la línea queda
        null=True
    )
    # Guardamos nombre y precio en el momento de la compra
    nombre_producto = models.CharField(max_length=200)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.PositiveIntegerField()

    def subtotal(self):
        """Subtotal de esta línea. Complejidad O(1)."""
        return self.precio_unitario * self.cantidad