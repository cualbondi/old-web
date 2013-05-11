from django.core.management.base import BaseCommand
import sys

import json
from collections import namedtuple
from pprint import pprint

from apps.catastro.models import Provincia, Ciudad
from apps.core.models import Linea, Recorrido, Parada, Horario
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.gis.geos import Point, LineString

# antes de ejecutar esto, hacer un dump
#   pg_dump -a --inserts -t core_linea -t core_recorrido -t core_parada -t core_horario geocualbondidb > dump.sql
#
# recordar poner las sequences en el ultimo valor de las pk
#   SELECT setval('core_linea_id_seq', (SELECT max(id) FROM core_linea));
#   SELECT setval('core_recorrido_id_seq', (SELECT max(id) FROM core_recorrido));
#   SELECT setval('core_parada_id_seq', (SELECT max(id) FROM core_parada));
#   SELECT setval('core_horario_id_seq', (SELECT max(id) FROM core_horario));
# 
# comando para restorear
#   echo "DELETE FROM core_linea; DELETE FROM core_parada; DELETE FROM core_horario; DELETE FROM core_recorrido;" | psql geocualbondidb
#   psql geocualbondidb < dump.sql
#

class Command(BaseCommand):
    def handle(self, *args, **options):
        obj = json.loads(open('mendoza-all.json').read())

        lineas = list(set([ o['grupo'] for o in obj ]))
        print lineas
        ci=Ciudad.objects.get(slug='mendoza')

        ls = []
        for l in lineas:
            li = Linea(nombre=l)
            li.save()
            ls.append(li)


        for o in obj:
            for l in ls:
                if o['grupo'].startswith(l.nombre):
                    print "Agregando recorrido " + o['grupo'] + " - " + o['recorrido']
                    sys.stdout.flush()
                    
                    poly = []
                    for p in o['route']:
                        poly.append((float(p.split(",")[1]),float(p.split(",")[0])))
                    poly = LineString(poly)

                    # IDA
                    recorrido = Recorrido(
                        nombre=o['recorrido']+" - "+o['nombre'], # DatabaseError: value too long for type character varying(100)
                        sentido='IDA-VUELTA',
                        linea=l,
                        inicio=o['desde'],
                        fin=o['hasta'],
                        ruta=poly,
                        descripcion=o['nombre'],
                        paradas_completas=False
                    )
                    recorrido.save()
                    for p in o['stops']:
                        sys.stdout.flush()
                        p = Point((float(p["lng"]),float(p["lat"])))
                        try:
                            parada = Parada.objects.get(latlng=p)
                            print "-",
                        except ObjectDoesNotExist:
                            print '+',
                            parada = Parada(latlng=p)
                            parada.save()
                        horario = Horario(recorrido=recorrido, parada=parada)
                        horario.save()

                    print ""
                    sys.stdout.flush()
