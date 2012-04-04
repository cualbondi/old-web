from django.contrib.gis.db import models


class Provincia(models.Model):
    nombre = models.CharField(max_length=100)
    zona = models.PolygonField()
    objects = models.GeoManager()

    def __unicode__(self):
        return self.nombre


class Ciudad(models.Model):
    nombre = models.CharField(max_length=100)
    recorridos = models.ManyToManyField('core.Recorrido', blank=True, null=True)
    lineas = models.ManyToManyField('core.Linea', blank=True, null=True)
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


class Calle(models.Model):
    pass


class Poi(models.Model):
    """ Un "Punto de interes" es algun lugar representativo
        de una "Ciudad". Por ej: la catedral de La Plata.
    """
    nombre = models.CharField(max_length=100)
    latlng = models.PointField()
    ciudad = models.ForeignKey(Ciudad)
    objects = models.GeoManager()



