from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    (r'^login/$', 'apps.usuarios.views.iniciar_sesion'),
    (r'^logout/$', 'apps.usuarios.views.cerrar_sesion'),
)
