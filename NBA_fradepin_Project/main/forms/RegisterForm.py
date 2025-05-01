# main/forms.py (Archivo SIN CAMBIOS, ya que es para Registro de Usuarios)

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UserRegistrationForm(UserCreationForm):
    # Añade el campo email al formulario de registro estándar
    email = forms.EmailField(label="Email", required=True) # Hacemos el email obligatorio

    class Meta(UserCreationForm.Meta): # Hereda de UserCreationForm.Meta para mantener campos base
        model = User
        # Campos a mostrar en el formulario: username y el email añadido
        fields = ('username', 'email')

# Este formulario está listo para ser usado en una vista de registro de Django.
# No requiere cambios para la funcionalidad de búsqueda de jugadores NBA.