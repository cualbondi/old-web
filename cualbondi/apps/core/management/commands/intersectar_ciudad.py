from django.core.management.base import BaseCommand, CommandError
from apps.core.models import Recorrido, Ciudad
from pprint import pprint

class Command(BaseCommand):

    def handle(self, *args, **options):
        stats = {}
        recorridos = Recorrido.objects.all()
        ciudades = Ciudad.objects.all()
        for ciudad in ciudades:
            stats[ciudad] = {'cant_intersecciones': 0,
                             'recorridos': [],
                             'lineas': []}
            for recorrido in recorridos:
                """ Checkear si la ciudad intersecta
                    al recorrido. Si lo intersecta
                    agregarlo a la relacion ManyToMany
                """
                if ciudad.zona.intersects(recorrido.ruta):
                    stats[ciudad]['cant_intersecciones'] += 1
                    stats[ciudad]['recorridos'].append(recorrido)
                    stats[ciudad]['lineas'].append(recorrido.linea)
                    ciudad.recorridos.add(recorrido)
                    ciudad.lineas.add(recorrido.linea)
        pprint(stats)

