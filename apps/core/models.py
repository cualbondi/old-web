from django.contrib.gis.db import models
from django.db import DatabaseError
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.contrib.gis.geos import Point
from apps.core.managers import RecorridoManager

class Linea(models.Model):
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, blank=True, null=False)
    descripcion = models.TextField()
    foto = models.CharField(max_length=20, blank=True, null=True)

    def __unicode__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        self.slug = slugify("linea " + self.nombre)
        super(Linea, self).save(*args, **kwargs)


class Terminal(models.Model):
    linea = models.ForeignKey(Linea)
    descripcion = models.TextField()
    direccion = models.CharField(max_length=150)
    telefono = models.CharField(max_length=150)
    latlng = models.PointField()
    objects = models.GeoManager()


class Recorrido(models.Model):
    nombre = models.CharField(max_length=100)
    linea = models.ForeignKey(Linea)
    ruta = models.LineStringField()

    slug = models.SlugField(max_length=200, blank=True, null=False)
    inicio = models.CharField(max_length=100, blank=True, null=False)
    fin = models.CharField(max_length=100, blank=True, null=False)
    semirrapido = models.BooleanField(default=False)

    objects = RecorridoManager()

    def __unicode__(self):
        return str(self.linea) + " " + self.nombre

    def save(self, *args, **kwargs):
        # Generar el SLUG a partir del origen y destino del recorrido
        self.slug = slugify("recorrido " + self.nombre + " desde " +\
                                   self.inicio + " hasta " + self.fin)

        # Ejecutar el SAVE original
        super(Recorrido, self).save(*args, **kwargs)

        # Ver que ciudades intersecta
        ciudades = Ciudad.objects.all()
        for ciudad in ciudades:
            if ciudad.zona.intersects(self.ruta):
                ciudad.recorridos.add(self)
                ciudad.lineas.add(self.linea)


class Provincia(models.Model):
    nombre = models.CharField(max_length=100)
    zona = models.PolygonField()
    objects = models.GeoManager()

    def __unicode__(self):
        return self.nombre


class Ciudad(models.Model):
    nombre = models.CharField(max_length=100)
    recorridos = models.ManyToManyField(Recorrido, blank=True, null=True)
    lineas = models.ManyToManyField(Linea, blank=True, null=True)
    slug = models.SlugField(max_length=120, blank=True, null=False)
    zona = models.PolygonField()
    zoom = models.IntegerField()
    centro = models.PointField()
    provincia = models.ForeignKey(Provincia)
    activa = models.BooleanField(default=False)
    objects = models.GeoManager()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nombre)
        super(Ciudad, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.nombre + " (" + self.provincia.nombre + ")"


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
