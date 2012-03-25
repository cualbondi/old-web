from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
#    (r'^login/$', 'apps.usuarios.views.iniciar_sesion'),
    (r'^login/$', 'apps.usuarios.views.iniciar_sesion', {'template_name': 'usuarios/login.html'}),
    (r'^logout/$', 'apps.usuarios.views.cerrar_sesion'),
)
