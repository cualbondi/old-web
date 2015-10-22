from django.contrib.gis.db import models
from django.contrib.auth.models import User


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
    recorrido = models.ForeignKey('core.Recorrido')
    activo = models.BooleanField()


class PerfilUsuario(models.Model):
    usuario = models.ForeignKey(User, blank=True, null=False)
    nombre = models.CharField(max_length=50, null=True, blank=True)
    apellido = models.CharField(max_length=50, null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    ciudad = models.ForeignKey('catastro.Ciudad', null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now=False, auto_now_add=True, null=False, blank=True)
    ultima_modificacion = models.DateTimeField(auto_now=True, null=False, blank=True)
    confirmacion_key = models.CharField(max_length=40, null=False)
    fecha_envio_confirmacion = models.DateTimeField(auto_now_add=True, null=False, blank=True)
    fecha_verificacion = models.DateTimeField(null=True, blank=True, default=None)

    def __unicode__(self):
        return "Perfil de " + self.usuario.username
