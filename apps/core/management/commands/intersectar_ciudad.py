from django.core.management.base import BaseCommand, CommandError
from apps.core.models import Recorrido
from apps.catastro.models import Ciudad
from pprint import pprint

class Command(BaseCommand):

    def handle(self, *args, **options):
        stats = {}
        recorridos = Recorrido.objects.all()
        ciudades = Ciudad.objects.all()
        for ciudad in ciudades:
            stats[ciudad.id] = 0
            for recorrido in recorridos:
                """ Checkear si la ciudad intersecta
                    al recorrido. Si lo intersecta
                    agregarlo a la relacion ManyToMany
                """
                if ciudad.poligono.intersects(recorrido.ruta):
                    stats[ciudad.id] += 1
                    ciudad.recorridos.add(recorrido)
                    ciudad.lineas.add(recorrido.linea)
            if len(ciudad.recorridos.all())>0:
                ciudad.activa=True
                ciudad.save()
                print ciudad, stats[ciudad.id]

