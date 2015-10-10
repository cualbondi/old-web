from django.conf.urls import url, include
from rest_framework import routers
from views import ciudades, lineas, recorridos

router = routers.SimpleRouter()

router.register(r'ciudad'   , ciudades.CiudadViewSet)
router.register(r'linea'    , lineas.LineaViewSet)
router.register(r'recorrido', recorridos.RecorridoViewSet)
#router.register(r'catastro'  , views.catastro.CatastroViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^auth/', include('rest_framework.urls', namespace='rest_framework'))
]