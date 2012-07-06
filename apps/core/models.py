# -*- coding: UTF-8 -*-
from django.contrib.gis.db import models
from django.db import DatabaseError
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.contrib.gis.geos import Point
from django.core.exceptions import ObjectDoesNotExist

from apps.core.managers import RecorridoManager
from apps.catastro.models import Ciudad
from apps.usuarios.models import RecorridoFavorito


class Linea(models.Model):
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, blank=True, null=False)
    descripcion = models.TextField(blank=True, null=True)
    foto = models.CharField(max_length=20, blank=True, null=True)

    def __unicode__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nombre)
        super(Linea, self).save(*args, **kwargs)


class Recorrido(models.Model):
    nombre = models.CharField(max_length=100)
    linea = models.ForeignKey(Linea)
    ruta = models.LineStringField()
    sentido = models.CharField(max_length=100, blank=True, null=False)
    slug = models.SlugField(max_length=200, blank=True, null=False)
    inicio = models.CharField(max_length=100, blank=True, null=False)
    fin = models.CharField(max_length=100, blank=True, null=False)
    semirrapido = models.BooleanField(default=False)

    objects = RecorridoManager()

    def __unicode__(self):
        return str(self.linea) + " " + self.nombre

    def es_favorito(self, usuario):
        """ Verificar si este recorrido esta marcado como favorito para <usuario> """
        try:
            favorito = RecorridoFavorito.objects.get(recorrido=self, usuario=usuario)
            return favorito.activo
        except ObjectDoesNotExist:
            return False

    def save(self, *args, **kwargs):
        # Generar el SLUG a partir del origen y destino del recorrido
        self.slug = slugify(self.nombre + " desde " + self.inicio + " hasta " + self.fin)

        # Ejecutar el SAVE original
        super(Recorrido, self).save(*args, **kwargs)

        # Ver que ciudades intersecta
        ciudades = Ciudad.objects.all()
        for ciudad in ciudades:
            if ciudad.poligono.intersects(self.ruta):
                ciudad.recorridos.add(self)
                ciudad.lineas.add(self.linea)


class Comercio(models.Model):
    nombre = models.CharField(max_length=100)
    latlng = models.PointField()
    ciudad = models.ForeignKey(Ciudad)
    objects = models.GeoManager()


class Parada(models.Model):
    nombre = models.CharField(max_length=100)
    latlng = models.PointField()
    objects = models.GeoManager()


class Horario(models.Model):
    """ Un "Recorrido" pasa por una "Parada" a
        cierto "Horario". "Horario" es el modelo 
        interpuesto entre "Recorrido" y "Parada"
    """
    recorrido = models.ForeignKey(Recorrido)
    parada = models.ForeignKey(Parada)
    hora = models.CharField(max_length=5)


class Terminal(models.Model):
    linea = models.ForeignKey(Linea)
    descripcion = models.TextField()
    direccion = models.CharField(max_length=150)
    telefono = models.CharField(max_length=150)
    latlng = models.PointField()
    objects = models.GeoManager()


