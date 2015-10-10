from rest_framework import serializers
from rest_framework import viewsets
from rest_framework import permissions

from apps.catastro.models import Ciudad


class ReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


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
    permission_classes = (ReadOnly,)
    serializer_class = CiudadSerializer
    queryset = Ciudad.objects.all()
