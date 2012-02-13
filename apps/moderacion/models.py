from django.contrib.gis.db import models
from django.contrib.auth.models import User


class Linea(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    foto = models.CharField(max_length=20)
    visible = models.BooleanField(default=False)

    def __unicode__(self):
        return self.nombre

class Terminal(models.Model):
    linea = models.ForeignKey(Linea)
    descripcion = models.TextField()
    direccion = models.CharField(max_length=150)
    telefono = models.CharField(max_length=150)
    latlng = models.PointField()
    objects = models.GeoManager()


class Recorrido(models.Model):
    nombre = models.CharField(max_length=100)
    ruta = models.LineStringField()
    inicio = models.CharField(max_length=100)
    fin = models.CharField(max_length=100)
    linea = models.ForeignKey(Linea)
    semirrapido = models.BooleanField()
    objects = models.GeoManager()
    visible = models.BooleanField(default=False)

    def __unicode__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        super(Recorrido, self).save(*args, **kwargs)


class Provincia(models.Model):
    nombre = models.CharField(max_length=100)
    zona = models.PolygonField()
    objects = models.GeoManager()


class Ciudad(models.Model):
    nombre = models.CharField(max_length=100)
    zona = models.PolygonField()
    zoom = models.IntegerField()
    centro = models.PointField()
    recorridos = models.ManyToManyField(Recorrido, blank=True, null=True)
    provincia = models.ForeignKey(Provincia)
    objects = models.GeoManager()


class Comercio(models.Model):
    nombre = models.CharField(max_length=100)
    latlng = models.PointField()
    ciudad = models.ForeignKey(Ciudad)
    objects = models.GeoManager()


class Poi(models.Model):
    """ Un "Punto de interes" es algun lugar representativo
        de una "Ciudad". Por ej: la catedral de La Plata.
    """
    nombre = models.CharField(max_length=100)
    latlng = models.PointField()
    ciudad = models.ForeignKey(Ciudad)
    objects = models.GeoManager()


class CustomPoi(models.Model):
    """ Los usuarios pueden definir sus propios
        puntos de interes. Por ej: "Mi casa", y
        luego usarlos como puntos origen o destino 
        en las busquedas. 
    """
    usuario = models.ForeignKey(User)
    nombre = models.CharField(max_length=100)
    latlng = models.PointField()
    objects = models.GeoManager()


class RecorridoFavorito(models.Model):
    """ Los "Usuarios" pueden marcar un "Recorrido"
        como favorito. Si lo DESmarcan como favorito,
        la tupla no se borra, sino que se pone como
        activo = False
    """
    usuario = models.ForeignKey(User)
    recorrido = models.ForeignKey(Recorrido)
    activo = models.BooleanField()


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
