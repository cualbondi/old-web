from django.contrib.gis.db import models
from django.contrib.auth.models import User
from core.models import Recorrido, Linea, Horario, Parada


class Revision(models.Model):
    class Meta:
        abstract = True

    fecha_edicion = models.DateTimeField(auto_now=True, auto_now_add=True)
    fecha_creacion = models.DateTimeField(auto_now=False, auto_now_add=True)
    moderado = models.IntegerField(default=0)
    editor = models.ForeignKey(User, blank=True, null=True)

    def save(self, *args, **kwargs):
        super(Revision, self).save(*args, **kwargs)


class LineaRevision(Revision):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    foto = models.CharField(max_length=20)

    def __unicode__(self):
        return self.nombre


class RecorridoRevision(Revision):
    nombre = models.CharField(max_length=100)
    ruta = models.LineStringField()
    inicio = models.CharField(max_length=100)
    fin = models.CharField(max_length=100)
    linea = models.ForeignKey(LineaRevision)
    semirrapido = models.BooleanField()
    objects = models.GeoManager()

    def __unicode__(self):
        return self.nombre + " (" + self.linea.nombre + ")"


class ParadaRevision(Revision):
    nombre = models.CharField(max_length=100)
    latlng = models.PointField()
    objects = models.GeoManager()

    def __unicode__(self):
        return self.nombre

class HorarioRevision(Revision):
    recorrido = models.ForeignKey(RecorridoRevision)
    parada = models.ForeignKey(ParadaRevision)
    hora = models.CharField(max_length=5)

    def __unicode__(self):
        return self.hora
