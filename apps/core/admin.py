from django.contrib.gis import admin

from apps.core.models import (Linea, Recorrido, Tarifa, Parada,
                              Horario, Posicion, FacebookPage)
from django.utils.safestring import mark_safe

from django.contrib.auth.admin import UserAdmin
UserAdmin.list_display += ('date_joined',)
UserAdmin.list_filter += ('date_joined',)
UserAdmin.fieldsets += ('date_joined',)
UserAdmin.list_display += ('last_login',)
UserAdmin.list_filter += ('last_login',)
UserAdmin.fieldsets += ('last_login',)


# TODO: Esto fue copiado a lo macho del codigo de Django 1.5
def format_html(format_string, *args, **kwargs):
    """
    Similar to str.format, but passes all arguments through conditional_escape,
    and calls 'mark_safe' on the result. This function should be used instead
    of str.format or % interpolation to build up small HTML fragments.
    """
    args_safe = map(conditional_escape, args)
    kwargs_safe = dict((k, conditional_escape(v)) for (k, v) in
                        six.iteritems(kwargs))
    return mark_safe(format_string.format(*args_safe, **kwargs_safe))

def format_html_join(sep, format_string, args_generator):
    """
    A wrapper of format_html, for the common case of a group of arguments that
    need to be formatted using the same format string, and then joined using
    'sep'. 'sep' is also passed through conditional_escape.

    'args_generator' should be an iterator that returns the sequence of 'args'
    that will be passed to format_html.

    Example:

      format_html_join('\n', "<li>{0} {1}</li>", ((u.first_name, u.last_name)
                                                  for u in users))

    """
    return mark_safe(conditional_escape(sep).join(
            format_html(format_string, *tuple(args))
            for args in args_generator))


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
admin.site.register(Tarifa)
admin.site.register(Posicion)
admin.site.register(FacebookPage)
