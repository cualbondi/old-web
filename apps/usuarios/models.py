from django.db import models
from django.contrib.auth.models import User
from apps.core.models import Ciudad


class PerfilUsuario(models.Model):
    usuario = models.ForeignKey(User, blank=True, null=False)
    nombre = models.CharField(max_length=50, null=True, blank=True)
    apellido = models.CharField(max_length=50, null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    ciudad = models.ForeignKey(Ciudad, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now=False, auto_now_add=True, null=False, blank=True)
    ultima_modificacion = models.DateTimeField(auto_now=True, auto_now_add=True, null=False, blank=True)
    confirmacion_key = models.CharField(max_length=40, null=False)
    fecha_envio_confirmacion = models.DateTimeField(auto_now=False, auto_now_add=True, null=False, blank=True)
    fecha_verificacion = models.DateTimeField(null=True, blank=True, default=None)

