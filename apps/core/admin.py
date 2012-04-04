from django.contrib.gis import admin
from moderation.admin import ModerationAdmin
from apps.core.models import Terminal, Linea, Recorrido, Comercio, Parada, Horario
from apps.catastro.models import Ciudad, Provincia, Poi
from apps.usuarios.models import CustomPoi, RecorridoFavorito

class CustomAdmin(ModerationAdmin, admin.OSMGeoAdmin):
    exclude = ()

admin.site.register(Linea, CustomAdmin)
admin.site.register(Recorrido, CustomAdmin)
admin.site.register(RecorridoFavorito)

