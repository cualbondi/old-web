# -*- coding: UTF-8 -*-
from django.contrib.gis.db import models
from apps.editor.fields import UUIDField
from django.contrib.auth.models import User
from django.db.models.loading import get_model
from django.core.management import call_command
from django.contrib.auth.models import AnonymousUser

MODERATION_CHOICES = (
    ('E', 'Esperando Mod'),
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
        user = kwargs.pop('user', None)
        super(RecorridoProposed, self).save(*args, **kwargs)
        mod = self.get_moderacion_last()
        if mod is None or ( user is not None and user != mod.created_by ):
            self.logmoderacion_set.create(created_by=user)
    
    def get_current_status_display(self):
        status_list = self.logmoderacion_set.all().order_by('-date_create')
        if status_list:
            return status_list[0].get_newStatus_display()
        else:
            return None
    
    def log(self):
        return self.logmoderacion_set.all().order_by('-date_create')
    
    def get_moderacion_last(self):
        loglist = self.logmoderacion_set.all().order_by('-date_create')
        if loglist:
            return loglist[0]
        else:
            return None

    def get_moderacion_last_user(self):
        loglist = self.logmoderacion_set.filter(created_by__is_staff=False).order_by('-date_create')
        if loglist:
            return loglist[0].created_by
        else:
            return AnonymousUser()

    def get_fb_uid(self):
        last = self.get_moderacion_last_user()
        if last is not None:
            return last.social_auth.get(provider='facebook').uid
        else:
            return None
        
    def __unicode__(self):
        return str(self.linea) + " - " + self.nombre

    def aprobar(self, user):
        r = self.recorrido
        if not r.uuid:
            # todavia no existe una version de este recorrido real, que estoy por retirar
            # antes de retirarlo creo su version correspondiente
            rp = RecorridoProposed(
                recorrido       = r,
                nombre          = r.nombre,
                linea           = r.linea,
                ruta            = r.ruta,
                sentido         = r.sentido,
                slug            = r.slug,
                inicio          = r.inicio,
                fin             = r.fin,
                semirrapido     = r.semirrapido,
                color_polilinea = r.color_polilinea,
                pois            = r.pois,
                descripcion     = r.descripcion
            )
            rp.save(user=user)
            self.parent=rp.uuid
            self.save()

        r.recorrido       = self.recorrido
        r.nombre          = self.nombre
        r.linea           = self.linea
        r.ruta            = self.ruta
        r.sentido         = self.sentido
        r.inicio          = self.inicio
        r.fin             = self.fin
        r.semirrapido     = self.semirrapido
        r.color_polilinea = self.color_polilinea
        r.pois            = self.pois
        r.descripcion     = self.descripcion
        r.save()

        try:
            parent = RecorridoProposed.objects.get(uuid=self.parent)
            if parent:
                parent.logmoderacion_set.create(created_by=user,newStatus='R')
        except RecorridoProposed.DoesNotExist:
            pass
        for rp in RecorridoProposed.objects.filter(current_status='S', recorrido=r.recorrido).exclude(uuid=self.uuid):
            rp.logmoderacion_set.create(created_by=user, newStatus='R')
        self.logmoderacion_set.create(created_by=user, newStatus='S')
        
        call_command('crear_thumbs', recorrido_id=self.recorrido.id)
    
    class Meta:
        permissions = (
            ("moderate_recorridos", "Can moderate (accept/decline) recorridos"),
        )

class LogModeracion(models.Model):
    recorridoProposed = models.ForeignKey(RecorridoProposed)
    created_by = models.ForeignKey(User, blank=True, null=True)
    date_create = models.DateTimeField(auto_now_add=True)
    # Nuevo Estado de la moderación
    newStatus = models.CharField( max_length=1, choices=MODERATION_CHOICES, default='E')
    
    def save(self, *args, **kwargs):
        super(LogModeracion, self).save(*args, **kwargs)
        if self.recorridoProposed.current_status != self.newStatus:
            self.recorridoProposed.current_status = self.newStatus
            self.recorridoProposed.save()