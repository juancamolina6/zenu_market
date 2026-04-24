from django.db import models
from django.contrib.auth.models import User

# ============================================================
# PERFIL
# Extiende el User de Django con datos adicionales.
# Cada usuario tiene exactamente un Perfil (relación 1 a 1).
# Esto reemplaza la clase "Perfil" del diagrama UML.
# ============================================================
class Perfil(models.Model):
    # OneToOneField significa que cada User tiene UN solo Perfil
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    direccion = models.CharField(max_length=255, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)

    def __str__(self):
        # Esto define cómo se muestra el objeto en el admin de Django
        return f"Perfil de {self.usuario.username}"

    def actualizar_datos(self, direccion=None, telefono=None):
        """Actualiza los datos del perfil. Corresponde a actualizarDatos() del UML."""
        if direccion:
            self.direccion = direccion
        if telefono:
            self.telefono = telefono
        self.save()


# ============================================================
# VENDEDOR
# Un usuario puede registrarse como vendedor para publicar
# productos en ZenuMarket. Corresponde a la clase Vendedor del UML.
# ============================================================
class Vendedor(models.Model):

    # Opciones de estado del vendedor
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('suspendido', 'Suspendido'),
    ]

    # Un vendedor está ligado a un único usuario
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre_tienda = models.CharField(max_length=200)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre_tienda

    def esta_activo(self):
        """Retorna True si el vendedor puede publicar productos."""
        return self.estado == 'activo'


# ============================================================
# CLIENTE
# Perfil de comprador. El mismo usuario puede tener también
# un Vendedor (rol dual, según decisión del equipo).
# Corresponde a la clase Cliente del UML.
# ============================================================
class Cliente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    direccion_envio = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Cliente: {self.usuario.get_full_name() or self.usuario.username}"