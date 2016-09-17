#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
import urllib
import subprocess
import os
from stat import *
import sys
from optparse import make_option
from apps.catastro.models import Ciudad, Poi, Poicb
from django.conf import settings
from django.db import connection, transaction
from psycopg2 import connect
from datetime import datetime



class Command(BaseCommand):

    def reporthook(self, numblocks, blocksize, filesize, url=None):
        base = os.path.basename(url)
        try:
            percent = min((numblocks * blocksize * 100) / filesize, 100)
        except:
            percent = 100
        if numblocks != 0:
            sys.stdout.write('\b' * 70)
        sys.stdout.write('%-66s%3d%%' % (base, percent))

    option_list = BaseCommand.option_list + (
        make_option(
            '-f',
            type    = 'string',
            action  = 'store',
            dest    = 'inputFile',
            default = '',
            help    = 'Use an input file instead of trying to download osm data'
        ),
        make_option(
            '--use-cache',
            action  = 'store_true',
            dest    = 'use_cache',
            default = False,
            help    = 'Use the cache of downloaded osm'
        ),
        make_option(
            '-s',
            action  = 'store_true',
            dest    = 'slim',
            default = False,
            help    = 'Set osm2pgsql slim mode (create raw tables: nodes, rels, ways)'
        ),
        make_option(
            '--no-o2p',
            action  = 'store_true',
            dest    = 'no-o2p',
            default = False,
            help    = 'Ignore osm2pgsql execution (debug purposes only)'
        ),
        make_option(
            '--no-tmp',
            action  = 'store_true',
            dest    = 'no-tmp',
            default = False,
            help    = 'Don\'t use /tmp folder, instead use apps/catastro/management/commands folder to save the downloaded argentina.osm.pbf file'
        ),
        make_option(
            '--ciudad',
            type    = 'string',
            action  = 'store',
            dest    = 'ciudad',
            help    = 'Only import this ciudad slug'
        )
    )

    def handle(self, *args, **options):
        inputfile = '/tmp/argentina.cache.osm-{}.pbf'.format(datetime.now().strftime('%Y%m%d%H%M%S'))
        if options['no-tmp']:
            inputfile = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'argentina.cache.osm.pbf')
        if options['inputFile'] or options['use_cache']:
            if options['inputFile']:
                inputfile = options['inputFile']
        else:
            print ' => Descargando mapa de Argentina de geofabrik'
            url = 'http://download.geofabrik.de/south-america/argentina-latest.osm.pbf'
            print '    - {}'.format(url)
            f, d = urllib.urlretrieve(url, inputfile, lambda nb, bs, fs, url=url: self.reporthook(nb,bs,fs,url))
            #print 'Descomprimiendo'
            #subprocess.Popen(['bunzip2', '-vvf', inputfile+'.bz2']).wait()
            #os.chmod(inputfile, S_IROTH | S_IRUSR | S_IROTH | S_IWOTH | S_IWUSR | S_IWOTH)

        dbname = connection.settings_dict['NAME']
        dbuser = 'postgres'#connection.settings_dict['USER']
        dbpass = 'postgres'#connection.settings_dict['PASSWORD']
        dbhost = 'localhost'#connection.settings_dict['HOST']

        cu = connection.cursor()
        cu.execute('SELECT slug, box(poligono::geometry) as box FROM catastro_ciudad;')

        # TODO: osmconvert /tmp/argentina.cache.osm-20160711192104.pbf -b=-57.8526306071815,-38.1354198737499,-57.5065612712919,-37.8562051788731 -o=1.pbf

        print ' => Cargando data de osm en la base de cualbondi'

        ciudades = cu.fetchall()
        for c in ciudades:

            # if options.ciudad is defined, and this is not it, skip it
            if options['ciudad'] and options['ciudad'] != c[0]:
                continue

            l = c[1][1:-1].replace(')', '').replace('(', '').split(',')
            box = ','.join([l[2], l[3], l[0], l[1]])
            print '    - Extrayendo {} ({})'.format(c[0], box)
            prog = [
                'osmconvert',
                inputfile,
                '-b={}'.format(box),
                '-o=/tmp/part-{}.osm'.format(c[0])
            ]

            subprocess.Popen(prog).wait()


        print '    - Uniendo partes'
        partfiles = ['/tmp/part-{}.osm'.format(c[0]) for c in ciudades]
        prog = [
            'osmconvert',
            '-o=/tmp/part-all.pbf'
        ] + partfiles
        subprocess.Popen(prog).wait()


        print '    - Cargando en la base de datos'
        prog = [
            'osm2pgsql',
            '-l',
            '-S{}'.format(os.path.join(os.path.abspath(os.path.dirname(__file__)),'update-osm.style')),
            '-d{}'.format(dbname),
            '-U{}'.format(dbuser),
            '-b{}'.format(box),
            '-c',
            '/tmp/part-all.pbf'
        ]
        if options['slim']:
            prog.append('-s')
        print '    - ejecutando:',
        print ' '.join(prog)
        if not options['no-o2p']:
            p = subprocess.Popen(prog, env={'PGPASSWORD': dbpass} )
            p.wait()



        #POST PROCESAMIENTO
        print 'POSTPROCESO'
        print ' => Dando nombres alternativos a los objetos sin nombre'
        print '    - NOTA: si esto no se puede completar es porque el usuario "postgres" debe tener "trust" en el archivo "pg_hba.conf" para "local"'
        superCu = connect(user='postgres', database=dbname).cursor()
        print '    - planet_osm_line'
        superCu.execute('update planet_osm_line    set name=ref where name is null;')
        print '    - planet_osm_point'
        superCu.execute('update planet_osm_point   set name=ref where name is null;')
        print '    - planet_osm_polygon'
        superCu.execute('update planet_osm_polygon set name=ref where name is null;')
        print '    - planet_osm_roads'
        superCu.execute('update planet_osm_roads   set name=ref where name is null;')
        superCu.close()


        print ' => Juntando tablas de caminos, normalizando nombres'
        print '    - Eliminando viejos'
        cu.execute('delete from catastro_calle')
        print '    - planet_osm_line'
        cu.execute("insert into catastro_calle(way, nom_normal, nom) select way, upper(translate(name, 'áéíóúÁÉÍÓÚäëïöüÄËÏÖÜñÑàèìòùÀÈÌÒÙ', 'AEIOUAEIOUAEIOUAEIOUNNAEIOUAEIOU')), name from planet_osm_line where name is not null;")
        print '    - planet_osm_roads'
        cu.execute("insert into catastro_calle(way, nom_normal, nom) select way, upper(translate(name, 'áéíóúÁÉÍÓÚäëïöüÄËÏÖÜñÑàèìòùÀÈÌÒÙ', 'AEIOUAEIOUAEIOUAEIOUNNAEIOUAEIOU')), name from planet_osm_roads where name is not null;")
        print '    - Eliminando nombres comunes (av., avenida, calle, diagonal, boulevard)'
        cu.execute("update catastro_calle set nom_normal = replace(nom_normal, 'AV. ', '');")
        cu.execute("update catastro_calle set nom_normal = replace(nom_normal, 'AVENIDA ', '');")
        cu.execute("update catastro_calle set nom_normal = replace(nom_normal, 'CALLE ', '');")
        cu.execute("update catastro_calle set nom_normal = replace(nom_normal, 'DIAGONAL ', '');")
        cu.execute("update catastro_calle set nom_normal = replace(nom_normal, 'BOULEVARD ', '');")


        print ' => Generando POIs a partir de poligonos normalizando nombres, agregando slugs (puede tardar bastante)'
        cu.execute('delete from catastro_poi')
        cu.execute("select ST_Centroid(way), upper(translate(name, 'áéíóúÁÉÍÓÚäëïöüÄËÏÖÜñÑàèìòùÀÈÌÒÙ', 'AEIOUAEIOUAEIOUAEIOUNNAEIOUAEIOU')), name||coalesce(', '||(select name from catastro_zona zo where ST_Intersects(ST_Centroid(way), zo.geo)), '') from planet_osm_polygon as pop where name is not null;")
        polygons = cu.fetchall()
        total = len(polygons)
        i = 0
        for poly in polygons:
            i = i + 1
            Poi.objects.create(nom_normal = poly[1], nom = poly[2], latlng = poly[0])
            if i * 100.0 / total % 1 == 0:
                print '    - {:2.0f}%'.format(i * 100.0 / total)
        # unir catastro_poicb (13 y 60, 13 y 66, 13 y 44) con catastro_poi (osm_pois)
        print '    - Mergeando POIs propios de cualbondi'
        for poicb in Poicb.objects.all():
            Poi.objects.create(nom_normal = poicb.nom_normal.upper(), nom = poicb.nom, latlng = poicb.latlng)
        print '    - Purgando nombres repetidos'
        cu.execute('delete from catastro_poi where id not in (select min(id) from catastro_poi group by nom_normal)')


        print ' => Regenerando indices'
        superCu = connect(user='postgres', database=dbname).cursor()
        print '    - Eliminando viejos'
        superCu.execute('DROP INDEX IF EXISTS catastrocalle_nomnormal_gin;')
        superCu.execute('DROP INDEX IF EXISTS catastropoi_nomnormal_gin;')
        print '    - Generando catastro_calle'
        superCu.execute('CREATE INDEX catastrocalle_nomnormal_gin ON catastro_calle USING gin (nom_normal gin_trgm_ops);')
        print '    - Generando catastro_poi'
        superCu.execute('CREATE INDEX catastropoi_nomnormal_gin ON catastro_poi USING gin (nom_normal gin_trgm_ops);')
        superCu.close()


        #print ' => Eliminando tablas no usadas'
        #cu.execute('drop table planet_osm_roads;')
        #cu.execute('drop table planet_osm_polygon;')
        #cx.commit()
        #cx.close()

        print ' LISTO! '
