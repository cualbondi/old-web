from django.contrib.gis import admin

from apps.core.models import Linea, Recorrido, Tarifa
from apps.usuarios.models import RecorridoFavorito


class CustomAdmin(admin.OSMGeoAdmin):
    search_fields = ['nombre', 'linea__nombre']
    exclude = ()

admin.site.register(Linea, CustomAdmin)
admin.site.register(Recorrido, CustomAdmin)
admin.site.register(RecorridoFavorito)
admin.site.register(Tarifa)
