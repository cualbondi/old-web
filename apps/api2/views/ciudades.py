from rest_framework import serializers
from rest_framework import viewsets

from apps.catastro.models import Ciudad


class CiudadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ciudad
        fields = (
            'id',
            'nombre',
            'slug',
            'centro',
            'activa',
            'img_panorama',
            'img_cuadrada',
        )


class CiudadViewSet(viewsets.ModelViewSet):
    serializer_class = CiudadSerializer
    queryset = Ciudad.objects.all()
