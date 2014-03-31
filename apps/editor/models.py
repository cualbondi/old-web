# -*- coding: UTF-8 -*-
from django.contrib.gis.db import models
from apps.editor.fields import UUIDField
from django.contrib.auth.models import User
from django.db.models.loading import get_model


MODERATION_CHOICES = (
    ('E', 'Esperando Moderación'),
    ('S', 'Aceptado'),
    ('N', 'Rechazado'),
    ('R', 'Retirado'),
)

class RecorridoProposed(models.Model):
    recorrido = models.ForeignKey(get_model('core', 'Recorrido'))
    parent = UUIDField()
    uuid = UUIDField()
    nombre = models.CharField(max_length=100)
    linea = models.ForeignKey(get_model('core', 'Linea'))
    ruta = models.LineStringField()
    sentido = models.CharField(max_length=100, blank=True, null=True)
    slug = models.SlugField(max_length=200, blank=True, null=True)
    inicio = models.CharField(max_length=100, blank=True, null=True)
    fin = models.CharField(max_length=100, blank=True, null=True)
    semirrapido = models.BooleanField(default=False)
    color_polilinea = models.CharField(max_length=20, blank=True, null=True)
    horarios = models.TextField(blank=True, null=True)
    pois = models.TextField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    current_status = models.CharField(max_length=1, choices=MODERATION_CHOICES, default='E')
    
    date_create = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    # Si tiene las paradas completas es porque tiene todas las paradas de
    # este recorrido en la tabla paradas+horarios (horarios puede ser null),
    # y se puede utilizar en la busqueda usando solo las paradas.
    paradas_completas = models.BooleanField(default=False)
    
    objects = models.GeoManager()
    
    def save(self, *args, **kwargs):
        super(RecorridoProposed, self).save(*args, **kwargs)
        if not self.logmoderacion_set:
            self.logmoderacion_set.create()
    
    def get_current_status_display(self):
        status_list = self.logmoderacion_set.all().order_by('-date_create')
        if status_list:
            return status_list[0].get_newStatus_display()
        else:
            return None        

    def __unicode__(self):
        #return str(self.ciudad_set.all()[0]) + " - " + str(self.linea) + " - " + self.nombre
        return str(self.linea) + " - " + self.nombre

    class Meta:
        permissions = (
            ("moderate_recorridos", "Can moderate (accept/decline) recorridos"),
        )

class LogModeracion(models.Model):
    recorridoProposed = models.ForeignKey(RecorridoProposed)
    created_by = models.ForeignKey(User)
    date_create = models.DateTimeField(auto_now_add=True)
    # Nuevo Estado de la moderación
    newStatus = models.CharField( max_length=1, choices=MODERATION_CHOICES, default='E')
    
    def save(self, *args, **kwargs):
        super(LogModeracion, self).save(*args, **kwargs)
        if self.recorridoProposed.current_status != self.newStatus:
            self.recorridoProposed.current_status = self.newStatus
            self.recorridoProposed.save()