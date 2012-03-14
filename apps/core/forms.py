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

class BaseGMapWidget(forms.gis.BaseGeometryWidget):
    """A Google Maps base widget"""
    map_srid = 900913
    template_name = 'floppyforms/gis/google.html'

    class Media:
        js = (
            'http://openlayers.org/dev/OpenLayers.js',
            '/media/js/floppyforms/MapWidget.js',
            'http://maps.google.com/maps/api/js?sensor=false',
        )

class CustomLineStringWidget(forms.gis.BaseGMapWidget, forms.gis.LineStringWidget):
    map_width = 700
    map_height = 400
    display_wkt = False


class RecorridoForm(forms.Form):
    ruta = forms.gis.LineStringField(widget=CustomLineStringWidget)
    class Meta:
        model = Recorrido



