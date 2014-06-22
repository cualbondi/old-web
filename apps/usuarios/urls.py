from django.conf.urls import patterns, url


urlpatterns = patterns('',
#    (r'^login/$', 'apps.usuarios.views.iniciar_sesion'),
    (r'^login/$', 'apps.usuarios.views.iniciar_sesion', {'template_name': 'usuarios/login.html'}),
    (r'^logout/$', 'apps.usuarios.views.cerrar_sesion'),
    (r'^registracion/$', 'apps.usuarios.views.registrar_usuario'),
    (r'^confirmar-email/(\w+)/$', 'apps.usuarios.views.confirmar_email'),
    (r'^editar-perfil/$', 'apps.usuarios.views.editar_perfil'),
    url(r'^login_ajax/(?P<backend>[^/]+)/$', 'apps.usuarios.views.ajax_auth', name='ajax_auth'),
    (r'^(?P<username>[^/]+)/$', 'apps.usuarios.views.ver_perfil'),
    #url(r'^(?P<username>[^/]+)/$', 'apps.usuarios.views.usuario', name='usuario'),
)
