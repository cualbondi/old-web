from django import forms
from moderation.forms import BaseModeratedObjectForm
from apps.core.models import Linea, Recorrido

mensajes = {
    'invalid': 'El valor ingresado es incorrecto',
    'required': 'Este campo no puede ser vacio'
}

class LineaForm(BaseModeratedObjectForm):
    nombre = forms.CharField(error_messages=mensajes)
    descripcion = forms.CharField(error_messages=mensajes,
                            widget = forms.Textarea(
                                        attrs={'cols': 80, 'rows': 10}))
#    foto = forms.FileField(error_messages=mensajes, required=False)

    class Meta:
        model = Linea
        exclude = ('slug')
