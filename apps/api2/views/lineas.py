from rest_framework import serializers
from rest_framework import viewsets

from apps.core.models import Linea


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
    serializer_class = LineaSerializer
    queryset = Linea.objects.all()
