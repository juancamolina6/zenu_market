from django import forms
from .models import Producto


class ProductoForm(forms.ModelForm):

    class Meta:
        model = Producto
        # Campos que el vendedor puede llenar
        # El vendedor se asigna automáticamente en la vista
        fields = ['nombre', 'categoria', 'sku', 'descripcion',
                  'precio', 'stock', 'imagen']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
        }