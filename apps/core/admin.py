from django.contrib.gis import admin
from moderation.admin import ModerationAdmin
from apps.core.models import (Terminal, Linea, Recorrido, Provincia,
        Ciudad, Comercio, Poi, CustomPoi, RecorridoFavorito,
        Parada, Horario)

class CustomAdmin(ModerationAdmin, admin.GeoModelAdmin):
    exclude = ()

admin.site.register(Linea, CustomAdmin)
admin.site.register(Recorrido, CustomAdmin)

