from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('',
    url(r'^zona/(?P<slug>[^/]+)/$', 'apps.catastro.views.zona', name='zona'),
    url(r'^(?P<slug>[^/]+)/$', 'apps.catastro.views.poi', name='poi'),
)