from rest_framework import serializers
from rest_framework import viewsets
from rest_framework import permissions

from apps.core.models import Linea


class ReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class LineaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Linea
        fields = (
            'id',
            'nombre',
            'slug',
            'ciudad_set',
        )


class LineaViewSet(viewsets.ModelViewSet):
    permission_classes = (ReadOnly,)
    serializer_class = LineaSerializer
    queryset = Linea.objects.all()
