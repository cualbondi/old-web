from django.contrib.gis import admin
from apps.catastro.models import Provincia, Ciudad, Poi

class CustomAdmin(admin.OSMGeoAdmin):
    exclude = ()

admin.site.register(Provincia, CustomAdmin)
admin.site.register(Ciudad, CustomAdmin)
admin.site.register(Poi, CustomAdmin)
