from django.conf.urls import url, include
from rest_framework import routers
from views import ciudades, lineas, recorridos, geocoder

router = routers.DefaultRouter()

router.register(r'ciudad', ciudades.CiudadViewSet)
router.register(r'linea', lineas.LineaViewSet)
router.register(r'recorrido', recorridos.RecorridoViewSet)
router.register(r'geocoder', geocoder.GeocoderViewSet, "geocoder")

urlpatterns = [
    url(r'^auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^', include(router.urls, namespace="api2")),
]
