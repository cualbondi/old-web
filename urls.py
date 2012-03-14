from django.conf.urls.defaults import patterns, include, url
from django.contrib.gis import admin
import settings

# Uncomment the next two lines to enable the admin:
admin.autodiscover()

from moderation.helpers import auto_discover
auto_discover()

urlpatterns = patterns('',
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),

    url(r'^api/', include('apps.api.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^usuarios/', include('apps.usuarios.urls')),

    url(r'^$', 'apps.core.views.index', name='index'),
    url(r'^seleccionar-ciudad/$', 'apps.core.views.seleccionar_ciudad', name='seleccionar_ciudad'),

    url(r'^(?P<nombre_ciudad>[\w-]+)/lineas/agregar/$', 'apps.core.views.agregar_linea', name='agregar_linea'),
    url(r'^(?P<nombre_ciudad>[\w-]+)/recorridos/agregar/$', 'apps.core.views.agregar_recorrido', name='agregar_recorrido'),

    # Ciudades
    url(r'^(?P<nombre_ciudad>[\w-]+)/$', 'apps.core.views.ver_ciudad', name='ver_ciudad'),
    url(r'^mapa/(?P<nombre_ciudad>[\w-]+)/$', 'apps.core.views.ver_mapa_ciudad', name='ver_mapa_ciudad'),

    # Lineas
    url(r'^(?P<nombre_ciudad>[\w-]+)/(?P<nombre_linea>[\w-]+)/$', 'apps.core.views.ver_linea', name='ver_linea'),

    # Recorridos
    url(r'^(?P<nombre_ciudad>[\w-]+)/(?P<nombre_linea>[\w-]+)/(?P<nombre_recorrido>[\w-]+)/$', 'apps.core.views.ver_recorrido', name='ver_recorrido'),
)
