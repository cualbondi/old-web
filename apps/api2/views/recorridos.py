from rest_framework import serializers
from rest_framework import viewsets
from rest_framework import permissions

from apps.core.models import Recorrido


class ReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class RecorridoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recorrido
        fields = (
            'id',
            'nombre',
            'slug',
            'ciudad_set',
        )


class RecorridoViewSet(viewsets.ModelViewSet):
    permission_classes = (ReadOnly,)
    serializer_class = RecorridoSerializer
    queryset = Recorrido.objects.all()
