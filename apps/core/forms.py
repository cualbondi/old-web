# -*- coding: UTF-8 -*-
import floppyforms as floppyforms

from django import forms
from django.conf import settings

from apps.core.models import Linea
from apps.catastro.models import Ciudad

mensajes = {
    'invalid': 'El valor ingresado es incorrecto',
    'required': 'Este campo no puede ser vacio'
}


class LineaForm(forms.Form):
    nombre = forms.CharField(error_messages=mensajes)
    descripcion = forms.CharField(error_messages=mensajes,
                                  widget=forms.Textarea(
                                  attrs={'cols': 80, 'rows': 10}))
#    foto = forms.FileField(error_messages=mensajes, required=False)

    class Meta:
        model = Linea
        exclude = ('slug')


class BaseGMapWidget(floppyforms.gis.BaseGeometryWidget):
    """A Google Maps base widget"""
    map_srid = 900913
    template_name = 'floppyforms/gis/google.html'

    class Media:
        js = (
            'http://openlayers.org/dev/OpenLayers.js',
            settings.STATIC_URL+'js/floppyforms/MapWidget.js',
            'http://maps.google.com/maps/api/js?sensor=false',
        )


class CustomLineStringWidget(BaseGMapWidget, floppyforms.gis.LineStringWidget):
    map_width = 700
    map_height = 400
    display_wkt = False


class RecorridoForm(floppyforms.Form):
    nombre = forms.CharField()
    linea = forms.ModelChoiceField(queryset=Linea.objects.all())
    ruta = floppyforms.gis.LineStringField(widget=CustomLineStringWidget)


class ContactForm(forms.Form):
    email = forms.EmailField(
        help_text="Déjenos su email para que podamos contactarlo")
    ciudad = forms.ModelChoiceField(
        queryset=Ciudad.objects.filter(activa=True),
        help_text="Díganos en que ciudad vive"
    )
    asunto = forms.CharField(
        max_length=100,
        help_text="¿Sobre qué es su consulta?"
    )
    mensaje = forms.CharField(widget=forms.Textarea)
