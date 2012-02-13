from django.contrib.gis import admin
from apps.core.models import (Terminal, Linea, Recorrido, Provincia,
        Ciudad, Comercio, Poi, CustomPoi, RecorridoFavorito,
        Parada, Horario)


admin.site.register(Terminal, admin.GeoModelAdmin)
admin.site.register(Linea, admin.GeoModelAdmin)
admin.site.register(Recorrido, admin.OSMGeoAdmin)
admin.site.register(Provincia, admin.GeoModelAdmin)
admin.site.register(Ciudad, admin.GeoModelAdmin)
admin.site.register(Comercio, admin.GeoModelAdmin)
admin.site.register(Poi, admin.GeoModelAdmin)
admin.site.register(CustomPoi, admin.GeoModelAdmin)
admin.site.register(RecorridoFavorito, admin.GeoModelAdmin)
admin.site.register(Parada, admin.GeoModelAdmin)
admin.site.register(Horario, admin.GeoModelAdmin)
