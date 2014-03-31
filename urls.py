from django.conf.urls.defaults import patterns, include, url
from django.contrib.gis import admin
import settings

# Uncomment the next two lines to enable the admin:
admin.autodiscover()


urlpatterns = patterns('',
    # Archivos estaticos
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    
    url('', include('social.apps.django_app.urls', namespace='social')),
    
    # Comentarios
    url(r'^comments/post/$', 'apps.core.views.dejar_comentario', name='dejar_comentario'),
    (r'^comments/', include('django.contrib.comments.urls')),

    # APPS de CualBondi
    url(r'^api/', include('apps.api.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^usuarios/', include('apps.usuarios.urls')),
    url(r'^widget/', include('apps.widget.urls')),
    url(r'^mobile_updates/', include('apps.mobile_updates.urls')),
    url(r'^editor/', include('apps.editor.urls')),

    url(r'^contacto/', 'apps.core.views.contacto', name='contacto'),

    url(r'^', include('apps.core.urls')),
)
