from django.conf.urls.defaults import patterns, include, url
from django.contrib.gis import admin
import settings

# Uncomment the next two lines to enable the admin:
admin.autodiscover()


urlpatterns = patterns('',
    # Archivos estaticos
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),

    # Comentarios
    url(r'^comments/post/$', 'apps.core.views.dejar_comentario', name='dejar_comentario'),
    (r'^comments/', include('django.contrib.comments.urls')),

    # APPS de CualBondi
    url(r'^api/', include('apps.api.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^usuarios/', include('apps.usuarios.urls')),
    url(r'^widget/', include('apps.widget.urls')),
    url(r'^', include('apps.core.urls')),
)
