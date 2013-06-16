from django.contrib.gis import admin

from apps.core.models import Linea, Recorrido, Tarifa, Parada, Horario
#from apps.usuarios.models import RecorridoFavorito
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe

class CustomAdmin(admin.OSMGeoAdmin):
    default_lon = -6428013
    default_lat = -4177742
    search_fields = ['nombre', 'linea__nombre', 'recorrido__nombre']
    exclude = ()

class HorarioAdminInline(admin.TabularInline):
    model = Horario
    
class RecorridoCustomAdmin(admin.OSMGeoAdmin):
    default_lon = -6428013
    default_lat = -4177742
    search_fields = ['nombre', 'linea__nombre']
    inlines = (HorarioAdminInline,)
    exclude = ('horarios',)
    
class ParadaCustomAdmin(admin.OSMGeoAdmin):
    default_lon = -6428013
    default_lat = -4177742
    search_fields = ['nombre', 'codigo']
    #inlines = (HorarioAdminInline,)
    readonly_fields = ('horarios',)
    
    def horarios(self, instance):
        return format_html_join(
            mark_safe('<br/>'),
            '{0}',
            ((line,) for line in instance.horario_set.all()),
        ) or "<span class='errors'>Can't find horarios.</span>"

    horarios.short_description = "Horarios"
    horarios.allow_tags = True

admin.site.register(Linea, CustomAdmin)
admin.site.register(Recorrido, RecorridoCustomAdmin)
admin.site.register(Parada, ParadaCustomAdmin)
#admin.site.register(RecorridoFavorito)
admin.site.register(Tarifa)
