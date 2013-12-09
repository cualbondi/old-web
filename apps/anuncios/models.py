# -*- coding: UTF-8 -*-
from django.contrib.gis.db import models


class Anuncio(models.Model):

    class Meta:
        ordering = ['orden']

    nombre = models.CharField(max_length=100)
    img = models.ImageField(max_length=500, upload_to='anuncios')
    link = models.URLField(max_length=500)
    created_date = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=True, auto_now=True)
    activo = models.BooleanField(default=False)
    orden = models.IntegerField()
    ciudades = models.ManyToManyField('catastro.Ciudad',
                                      related_name='anuncios')

    def __unicode__(self):
        return u'{0} - {1} ({2})'.format(
            self.orden,
            self.nombre,
            "Activo" if self.activo else "Inactivo"
        )
