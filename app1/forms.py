from django import forms
from .models import Cliente, Zapato

class ClientesForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'direccion', 'telefono', 'correo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo'}),
        }

class ZapatoForm(forms.ModelForm):
    class Meta:
        model = Zapato
        fields = ['referencia', 'modelo', 'talla', 'sexo', 'color', 'requerimientos', 'observaciones']
        widgets = {
            'referencia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Referencia'}),
            'modelo': forms.Select(attrs={'class': 'form-control'}),
            'talla': forms.Select(attrs={'class': 'form-control'}),
            'sexo': forms.Select(attrs={'class': 'form-control'}),
            'color': forms.Select(attrs={'class': 'form-control'}),
            'requerimientos': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Requerimientos'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Observaciones'}),
        }

class QRFileUploadForm(forms.Form):
    archivo = forms.FileField(
        label="Sube una imagen o PDF con QR",
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )