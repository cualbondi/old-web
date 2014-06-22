from django.conf.urls import patterns


urlpatterns = patterns('',
     (r'^package_recorridos$', 'apps.mobile_updates.views.recorridos_package'),
     (r'^package_ciudades$', 'apps.mobile_updates.views.ciudades_package'),
     (r'^versiones$', 'apps.mobile_updates.views.versiones'),
)
