from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    url(r'^$', 'apps.widget.views.not_found'),
    url(r'^v1/busqueda.js$', 'apps.widget.views.v1_busqueda', { 'extension': 'js' }, name='v1_busqueda_js'),
    url(r'^v1/busqueda.html$', 'apps.widget.views.v1_busqueda', { 'extension': 'html' }, name='v1_busqueda_html'),
    url(r'^v1/lineas.js$', 'apps.widget.views.v1_lineas', { 'extension': 'js' }, name='v1_lineas_js'),
    url(r'^v1/lineas.html$', 'apps.widget.views.v1_lineas', { 'extension': 'html' }, name='v1_lineas_html'),
    url(r'^test.html$', 'apps.widget.views.test'),
)
