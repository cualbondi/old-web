#from django import forms
import floppyforms as forms
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


class CustomLineStringWidget(forms.gis.BaseGMapWidget, forms.gis.LineStringWidget):
    map_width = 700
    map_height = 400
    display_wkt = False


class RecorridoForm(forms.Form):
    ruta = forms.gis.LineStringField(widget=CustomLineStringWidget)
    class Meta:
        model = Recorrido



