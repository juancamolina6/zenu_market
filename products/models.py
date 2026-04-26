from django.db import models
from users.models import Vendedor


# ============================================================
# CATEGORÍA
# Organiza los productos en grupos temáticos.
# Corresponde a la clase Categoria del diagrama UML.
# Ejemplo: Ropa, Electrónica, Alimentos
# ============================================================
class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    slug = models.SlugField(unique=True)
    # Emoji representativo de la categoría
    icono = models.CharField(max_length=10, default='🛒')

    class Meta:
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


# ============================================================
# PRODUCTO
# Artículo publicado por un Vendedor en ZenuMarket.
# Corresponde a la clase Producto del diagrama UML.
# Un Producto pertenece a una Categoria y tiene un Vendedor.
# ============================================================
class Producto(models.Model):

    # Estados posibles de un producto
    ESTADO_CHOICES = [
        ('activo', 'Activo'),        # visible para compradores
        ('inactivo', 'Inactivo'),    # oculto temporalmente
        ('agotado', 'Agotado'),      # sin stock
    ]

    # Vendedor que publica el producto (FK = llave foránea)
    # Si se elimina el vendedor, sus productos también se eliminan
    vendedor = models.ForeignKey(
        Vendedor,
        on_delete=models.CASCADE,
        related_name='productos'  # permite hacer vendedor.productos.all()
    )

    # Categoría del producto (FK)
    # SET_NULL: si se elimina la categoría, el producto queda sin categoría
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='productos'
    )

    # Datos del producto — corresponden a los atributos del UML
    sku = models.CharField(
        max_length=50,
        unique=True,  # no pueden existir dos productos con el mismo SKU
        help_text='Código único del producto. Ej: ZEN-001'
    )
    nombre = models.CharField(max_length=200, db_index=True)  # índice para búsquedas O(log n)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)  # se actualiza solo al guardar

    class Meta:
        ordering = ['-fecha_creacion']  # los más recientes primero

    def __str__(self):
        return f"{self.nombre} — ${self.precio}"

    def tiene_stock(self):
        """Retorna True si el producto tiene al menos una unidad disponible."""
        return self.stock > 0

    def actualizar_stock(self, cantidad):
        """
        Reduce el stock cuando se realiza una compra.
        Si el stock llega a 0, cambia el estado a agotado.
        Corresponde a actualizarStock() del diagrama UML.
        """
        self.stock -= cantidad
        if self.stock <= 0:
            self.stock = 0
            self.estado = 'agotado'
        self.save()