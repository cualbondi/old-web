from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^moderar/$', 'apps.editor.views.mostrar_ediciones', name='mostrar_ediciones'),
    url(r'^moderar/id:(?P<id>\d+)/$', 'apps.editor.views.moderar_ediciones_id', name='moderar_ediciones_id'),
    url(r'^moderar/uuid:(?P<uuid>[-\w]+)/$', 'apps.editor.views.moderar_ediciones_uuid', name='moderar_ediciones_uuid'),
    url(r'^moderar/uuid:(?P<uuid>[-\w]+)/aprobar/$', 'apps.editor.views.moderar_ediciones_uuid_aprobar', name='moderar_ediciones_uuid_aprobar'),
    url(r'^moderar/uuid:(?P<uuid>[-\w]+)/rechazar/$', 'apps.editor.views.moderar_ediciones_uuid_rechazar', name='moderar_ediciones_uuid_rechazar'),
    
    # Indexable por google (pretty url)
    url(r'^revision/(?P<id_revision>\d+)/$', 'apps.editor.views.revision', name='revision'),
    
    url(r'^(?P<id_recorrido>\d+)/$', 'apps.editor.views.editor_recorrido', name='editor_recorrido'),
)
