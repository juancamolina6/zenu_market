from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Perfil, Vendedor


# ============================================================
# FORMULARIO DE REGISTRO
# Extiende el formulario base de Django para crear usuarios.
# Agrega campos extra: nombre, apellido, teléfono y la opción
# de registrarse como vendedor.
# ============================================================
class RegistroForm(UserCreationForm):

    # Campos adicionales que no trae Django por defecto
    first_name = forms.CharField(
        max_length=50,
        required=True,
        label='Nombre'
    )
    last_name = forms.CharField(
        max_length=50,
        required=True,
        label='Apellido'
    )
    email = forms.EmailField(
        required=True,
        label='Correo electrónico'
    )
    telefono = forms.CharField(
        max_length=20,
        required=False,
        label='Teléfono'
    )
    direccion = forms.CharField(
        max_length=200,
        required=True,
        label='Direccion'
    )
    # Casilla para que el usuario elija si quiere ser vendedor
    ser_vendedor = forms.BooleanField(
        required=False,
        label='Quiero vender en ZenuMarket'
    )
    nombre_tienda = forms.CharField(
        max_length=200,
        required=False,
        label='Nombre de tu tienda (si vas a vender)'
    )

    class Meta:
        # Le decimos a Django que este formulario está ligado al modelo User
        model = User
        fields = ['username', 'first_name', 'last_name', 'email','direccion',
                  'password1', 'password2']

    def clean(self):
        """
        Validación personalizada: si el usuario marcó 'ser vendedor',
        el nombre de tienda es obligatorio.
        """
        cleaned_data = super().clean()
        ser_vendedor = cleaned_data.get('ser_vendedor')
        nombre_tienda = cleaned_data.get('nombre_tienda')

        if ser_vendedor and not nombre_tienda:
            raise forms.ValidationError(
                'Si quieres vender, debes ingresar el nombre de tu tienda.'
            )
        return cleaned_data


# ============================================================
# FORMULARIO DE EDICIÓN DE PERFIL
# Permite al usuario actualizar sus datos personales.
# ============================================================
class EditarPerfilForm(forms.ModelForm):

    # Campos del modelo User que también queremos editar
    first_name = forms.CharField(max_length=50, label='Nombre')
    direccion = forms.CharField(max_length=50, label='Apellido')
    email = forms.EmailField(label='Correo electrónico')

    class Meta:
        # Este formulario está ligado al modelo Perfil
        model = Perfil
        fields = ['telefono', 'direccion', 'fecha_nacimiento']
        widgets = {
            # Widget especial para que el campo fecha muestre un selector
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
        }