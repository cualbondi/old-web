# -*- coding: UTF-8 -*-
from django.contrib.gis.db import models
from django.template.defaultfilters import slugify

from apps.catastro.managers import PuntoBusquedaManager

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
    nombre = models.CharField(max_length=100, blank=False, null=False)
    variantes_nombre = models.CharField(max_length=150, blank=True, null=True)
    slug = models.SlugField(max_length=120, blank=True, null=False)
    longitud_poligono = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    area_poligono = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    centro = models.PointField(blank=True, null=False)
    poligono = models.PolygonField()
    objects = models.GeoManager()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nombre)
        self.centro = self.poligono.centroid
        super(Provincia, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.nombre


class Ciudad(models.Model):
    nombre = models.CharField(max_length=100, blank=False, null=False)
    variantes_nombre = models.CharField(max_length=150, blank=True, null=True)
    recorridos = models.ManyToManyField('core.Recorrido', blank=True, null=True)
    lineas = models.ManyToManyField('core.Linea', blank=True, null=True)
    slug = models.SlugField(max_length=120, blank=True, null=False)
    longitud_poligono = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    area_poligono = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    poligono = models.PolygonField()
    zoom = models.IntegerField(blank=True, null=False, default=14)
    centro = models.PointField(blank=True, null=False)
    provincia = models.ForeignKey(Provincia)
    activa = models.BooleanField(default=False)
    objects = models.GeoManager()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nombre)
        self.centro = self.poligono.centroid
        super(Ciudad, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.nombre + " (" + self.provincia.nombre + ")"


class Calle(models.Model):
    way = models.GeometryField(srid=4326, geography=True)
    nom_normal = models.TextField()
    nom = models.TextField()
    objects = models.GeoManager()


class Poi(models.Model):
    """ Un "Punto de interes" es algun lugar representativo
        de una "Ciudad". Por ej: la catedral de La Plata.
    """
#    nom_normal = models.TextField()
#    nom = models.TextField()
    latlng = models.PointField()
    objects = models.GeoManager()


class PuntoBusqueda(models.Model):
    objects = PuntoBusquedaManager()

    class Meta:
        abstract = True
