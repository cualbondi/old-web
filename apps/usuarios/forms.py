# -*- coding: UTF-8 -*-
import re
from django import forms
from django.contrib.auth.models import User

from apps.usuarios.models import PerfilUsuario


mensajes = {
    'invalid': 'El valor ingresado es incorrecto',
    'required': 'Este campo no puede ser vacio',
    'invalid_link': 'La URL ingresada no es valida'
}


class PerfilUsuarioForm(forms.ModelForm):
    nombre = forms.CharField(
        label='Nombre(s)',
        error_messages=mensajes,
        required=False
    )
    apellido = forms.CharField(
        label='Apellido(s)',
        error_messages=mensajes,
        required=False
    )
    about = forms.CharField(
        label='Mini biografia',
        error_messages=mensajes,
        widget=forms.Textarea(),
        required=False
    )
    website = forms.URLField(
        label='Página web',
        error_messages=mensajes,
        required=False
    )
    class Meta:
        model = PerfilUsuario
        exclude = ('usuario', 'confirmacion_key', 'fecha_verificacion')

    """TODO: Las regex no contemplan las letras "ñ" y "Ñ" """
    def clean_nombre(self):
        if not re.match("^[A-Za-z ]*$", self.cleaned_data["nombre"]):
            raise forms.ValidationError("Este campo solo puede contener letras y espacios en blanco")
        return self.cleaned_data["nombre"]

    def clean_apellido(self):
        if not re.match("^[A-Za-z ]*$", self.cleaned_data["apellido"]):
            raise forms.ValidationError("Este campo solo puede contener letras y espacios en blanco")
        return self.cleaned_data["apellido"]


class RegistracionForm(forms.Form):
    username = forms.CharField(
        label = "Nombre de usuario",
        max_length = 30,
        required = True,
        error_messages=mensajes,
        widget = forms.TextInput()
    )
    email = forms.EmailField(
        label = "Email",
        required = True,
        error_messages=mensajes,
        widget=forms.TextInput()
    )
    mensajes['min_length'] = 'La contraseña debe tener al menos 8 caracteres.'
    password1 = forms.CharField(
        label = "Contraseña",
        required = True,
        min_length = 8,
        error_messages=mensajes,
        widget = forms.PasswordInput(render_value=False)
    )
    password2 = forms.CharField(
        label = "Repetir contraseña",
        required = True,
        min_length = 8,
        error_messages=mensajes,
        widget = forms.PasswordInput(render_value=False)
    )
    confirmation_key = forms.CharField(
        max_length = 40,
        required = False,
        widget = forms.HiddenInput()
    )

    def clean_username(self):
        if not re.compile(r"^\w+$").search(self.cleaned_data["username"]):
            raise forms.ValidationError("El nombre de usuario solo puede contener letras, numeros y/o guion bajo.")
        try:
            User.objects.get(username__iexact=self.cleaned_data["username"])
        except User.DoesNotExist:
            return self.cleaned_data["username"]
        raise forms.ValidationError("El nombre de usuario ya esta utilizado. Por favor elegi otro.")

    def clean_email(self):
        value = self.cleaned_data["email"]
        try:
            User.objects.get(email__iexact=value)
        except User.DoesNotExist:
            return value
        raise forms.ValidationError("Ya hay una cuenta creada con este Email.")
        return value

    def clean(self):
        if "password1" in self.cleaned_data and "password2" in self.cleaned_data:
            if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
                raise forms.ValidationError("Las contraseñas deben ser iguales.")
        return self.cleaned_data

