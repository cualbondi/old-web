from django.core.management.base import BaseCommand
import sys

import json
from collections import namedtuple
from pprint import pprint

from apps.catastro.models import Provincia, Ciudad
from apps.core.models import Linea, Recorrido, Parada, Horario
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.gis.geos import WKTReader

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
        obj = json.loads(open('rosario-all.json').read())

        lineas = ['101','102','103','106','107','110','112','113','115','116','120','121','122','123','125','126','127','128','129','130','131','132','133','134','135','136','137','138','139','140','141','142','143','144','145','146','153','35/9','Enlace','K','Linea de la Costa','Ronda del Centro','Expreso','Las Rosas','M','Metropolitana','Monticas','Serodino','TIRSA']

        ci=Ciudad.objects.get(slug='rosario')

        ls = []
        for l in lineas:
            li = Linea(nombre=l)
            li.save()
            ls.append(li)


        for o in obj:
            for l in ls:
                if o['linea'].startswith(l.nombre):
                    print "Agregando recorrido " + o['linea']
                    print "IDA: ",
                    sys.stdout.flush()
                    
                    # IDA
                    recorrido = Recorrido(
                        nombre=o['linea'].replace(l.nombre, ''),
                        sentido='IDA',
                        linea=l,
                        inicio=o['descripcionIDA'].split(',')[0].replace('Desde', '').strip().capitalize(),
                        fin=o['descripcionIDA'].split(',')[-1].replace('Hasta', '').strip().capitalize(),
                        ruta=WKTReader().read(o['ida']),
                        descripcion=o['descripcionIDA'],
                        paradas_completas=True
                    )
                    recorrido.save()
                    for p in o['paradas']:
                        if WKTReader().read(p['point']).distance(recorrido.ruta) < 0.0005555: # ~50 metros
                            print p['codigo'],
                            sys.stdout.flush()
                            try:
                                parada = Parada.objects.get(codigo=p['codigo'])
                            except ObjectDoesNotExist:
                                parada = Parada(codigo=p['codigo'], latlng=WKTReader().read(p['point']))
                                parada.save()
                            horario = Horario(recorrido=recorrido, parada=parada)
                            horario.save()

                    print ""
                    print "VUELTA: ",
                    sys.stdout.flush()
                    # VUELTA
                    recorrido = Recorrido(
                        nombre=o['linea'].replace(l.nombre, ''),
                        sentido='VUELTA',
                        linea=l,
                        inicio=o['descripcionVUELTA'].split(',')[-1].replace('Hasta', '').strip().capitalize(),
                        fin=o['descripcionVUELTA'].split(',')[0].replace('Desde', '').strip().capitalize(),
                        ruta=WKTReader().read(o['vuelta']),
                        descripcion=o['descripcionVUELTA'],
                        paradas_completas=True
                    )
                    recorrido.save()
                    for p in o['paradas']:
                        print p['codigo'],
                        sys.stdout.flush()
                        if WKTReader().read(p['point']).distance(recorrido.ruta) < 0.0005555: # ~50 metros
                            try:
                                parada = Parada.objects.get(codigo=p['codigo'])
                            except ObjectDoesNotExist:
                                parada = Parada(codigo=p['codigo'], latlng=WKTReader().read(p['point']))
                                parada.save()
                            horario = Horario(recorrido=recorrido, parada=parada)
                            horario.save()
                    print ""
                    print "--------------------------------"
