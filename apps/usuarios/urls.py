from django.conf.urls.defaults import patterns


urlpatterns = patterns('',
#    (r'^login/$', 'apps.usuarios.views.iniciar_sesion'),
    (r'^login/$', 'apps.usuarios.views.iniciar_sesion', {'template_name': 'usuarios/login.html'}),
    (r'^logout/$', 'apps.usuarios.views.cerrar_sesion'),
    (r'^registracion/$', 'apps.usuarios.views.registrar_usuario'),
    (r'^perfil/$', 'apps.usuarios.views.ver_perfil'),
    (r'^confirmar-email/(\w+)/$', 'apps.usuarios.views.confirmar_email'),
    (r'^editar-perfil/$', 'apps.usuarios.views.editar_perfil'),
)
