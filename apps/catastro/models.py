# -*- coding: UTF-8 -*-
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from django.contrib.gis.db import models
from django.template.defaultfilters import slugify

from apps.catastro.managers import (
    CiudadManager, ZonaManager, PuntoBusquedaManager)

from django.core.urlresolvers import reverse

""" Dejemos estos modelos comentados hasta que resolvamos
la migracion de Provincia y Ciudad """

#class ArgAdm1(models.Model):
#    gid = models.IntegerField(primary_key=True)
#    id_0 = models.IntegerField()
#    iso = models.CharField(max_length=3)
#    name_0 = models.CharField(max_length=75)
#    id_1 = models.IntegerField()
#    name_1 = models.CharField(max_length=75)
#    varname_1 = models.CharField(max_length=150)
#    nl_name_1 = models.CharField(max_length=50)
#    hasc_1 = models.CharField(max_length=15)
#    cc_1 = models.CharField(max_length=15)
#    type_1 = models.CharField(max_length=50)
#    engtype_1 = models.CharField(max_length=50)
#    validfr_1 = models.CharField(max_length=25)
#    validto_1 = models.CharField(max_length=25)
#    remarks_1 = models.CharField(max_length=125)
#    shape_leng = models.DecimalField(max_digits=7, decimal_places=2)
#    shape_area = models.DecimalField(max_digits=7, decimal_places=2)
#    the_geom = models.MultiPolygonField(srid=-1)
#    objects = models.GeoManager()
#    class Meta:
#        db_table = u'arg_adm1'

#class ArgAdm2(models.Model):
#    gid = models.IntegerField(primary_key=True)
#    id_0 = models.IntegerField()
#    iso = models.CharField(max_length=3)
#    name_0 = models.CharField(max_length=75)
#    id_1 = models.IntegerField()
#    name_1 = models.CharField(max_length=75)
#    id_2 = models.IntegerField()
#    name_2 = models.CharField(max_length=75)
#    varname_2 = models.CharField(max_length=150)
#    nl_name_2 = models.CharField(max_length=75)
#    hasc_2 = models.CharField(max_length=15)
#    cc_2 = models.CharField(max_length=15)
#    type_2 = models.CharField(max_length=50)
#    engtype_2 = models.CharField(max_length=50)
#    validfr_2 = models.CharField(max_length=25)
#    validto_2 = models.CharField(max_length=25)
#    remarks_2 = models.CharField(max_length=100)
#    shape_leng = models.DecimalField(max_digits=7, decimal_places=2)
#    shape_area = models.DecimalField(max_digits=7, decimal_places=2)
#    the_geom = models.MultiPolygonField(srid=-1)
#    objects = models.GeoManager()
#    class Meta:
#        db_table = u'arg_adm2'


class Provincia(models.Model):
    # Obligatorios
    nombre = models.CharField(max_length=100, blank=False, null=False)
    slug = models.SlugField(max_length=120, blank=True, null=False)

    # Opcionales
    variantes_nombre = models.CharField(max_length=150, blank=True, null=True)
    longitud_poligono = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    area_poligono = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    centro = models.PointField(blank=True, null=True)
    poligono = models.PolygonField(blank=True, null=True)

    objects = models.GeoManager()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nombre)
        if self.poligono:
            self.centro = self.poligono.centroid
        super(Provincia, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.nombre


class Ciudad(models.Model):
    # Obligatorios
    nombre = models.CharField(max_length=100, blank=False, null=False)
    slug = models.SlugField(max_length=120, blank=True, null=False)
    provincia = models.ForeignKey(Provincia)
    activa = models.BooleanField(blank=True, null=False, default=False)
    img_panorama = models.ImageField(upload_to='ciudad', blank=True, null=True)
    img_cuadrada = models.ImageField(upload_to='ciudad', blank=True, null=True)

    # Opcionales
    variantes_nombre = models.CharField(max_length=150, blank=True, null=True)
    recorridos = models.ManyToManyField('core.Recorrido', blank=True, null=True)
    lineas = models.ManyToManyField('core.Linea', blank=True, null=True)
    longitud_poligono = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    area_poligono = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    poligono = models.PolygonField(blank=True, null=True)
    envolvente = models.PolygonField(blank=True, null=True)
    zoom = models.IntegerField(blank=True, null=True, default=14)
    centro = models.PointField(blank=True, null=True)
    descripcion = models.TextField(null=True, blank=True)
    sugerencia = models.CharField(max_length=100, blank=True, null=True)

    objects = CiudadManager()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nombre)
        #if self.poligono:
        #    self.centro = self.poligono.centroid
        super(Ciudad, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.nombre + " (" + self.provincia.nombre + ")"
    
    def get_absolute_url(self):
        return reverse('ver_ciudad', kwargs={'nombre_ciudad': self.slug})


class ImagenCiudad(models.Model):
    ciudad = models.ForeignKey(Ciudad, blank=False, null=False)
    original = models.ImageField(
        upload_to='img/ciudades',
        blank=False,
        null=False
    )
    custom_890x300 = ImageSpecField([ResizeToFill(890, 300)], image_field='original',
            format='JPEG', options={'quality': 100})
    titulo = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return self.original.name + " (" + self.ciudad.nombre + ")"


class Zona(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    geo = models.GeometryField(srid=4326, geography=True)

    objects = ZonaManager()
    
    def __unicode__(self):
        return self.name

class Calle(models.Model):
    way = models.GeometryField(srid=4326, geography=True)
    nom_normal = models.TextField()
    nom = models.TextField()
    objects = models.GeoManager()


class Poi(models.Model):
    """ Un "Punto de interes" es algun lugar representativo
        de una "Ciudad". Por ej: la catedral de La Plata.
    """
    nom_normal = models.TextField()
    nom = models.TextField()
    latlng = models.PointField()
    objects = models.GeoManager()


class PuntoBusqueda(models.Model):
    nombre = models.TextField()
    precision = models.FloatField()
    geom = models.TextField()
    tipo = models.TextField()

    objects = PuntoBusquedaManager()

    def asDict(self):
        return {
                "nombre": self.nombre,
                "precision": self.precision,
                "geom": self.geom,
                "tipo": self.tipo
            }

    class Meta:
        abstract = True
