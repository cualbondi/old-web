from django.contrib.gis import admin

from apps.catastro.models import Provincia, Ciudad, Poi, Zona, ImagenCiudad


class CustomAdmin(admin.OSMGeoAdmin):
    search_fields = ['nombre', 'variantes_nombre']
    exclude = ()

class ZonaAdmin(admin.OSMGeoAdmin):
    search_fields = ['name']

admin.site.register(Provincia, CustomAdmin)
admin.site.register(Ciudad, CustomAdmin)
admin.site.register(Poi, CustomAdmin)
admin.site.register(ImagenCiudad, CustomAdmin)
admin.site.register(Zona, ZonaAdmin)
