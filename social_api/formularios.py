from django import forms

# Formulario de registro
class Formulario_registro(forms.Form):
    nombre_usuario = forms.CharField(max_length=100)
    correo_electronico = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)