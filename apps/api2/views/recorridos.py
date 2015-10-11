from rest_framework import serializers
from rest_framework import viewsets

from apps.core.models import Recorrido


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
    serializer_class = RecorridoSerializer
    queryset = Recorrido.objects.all()
