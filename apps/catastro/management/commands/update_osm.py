#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
import urllib
import subprocess
import os
from stat import *
import sys
from optparse import make_option
from apps.catastro.models import Ciudad
from django.conf import settings
from django.db import connection, transaction
from psycopg2 import connect



class Command(BaseCommand):

    def reporthook(self, numblocks, blocksize, filesize, url=None):
        base = os.path.basename(url)
        try:
            percent = min((numblocks * blocksize * 100) / filesize, 100)
        except:
            percent = 100
        if numblocks != 0:
            sys.stdout.write("\b" * 70)
        sys.stdout.write("%-66s%3d%%" % (base, percent))

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
        )
    )

    def handle(self, *args, **options):
        inputfile = os.path.join(os.path.abspath(os.path.dirname(__file__)), "argentina.cache.osm")
        if options['inputFile'] or options['use_cache']:
            if options['inputFile']:
                inputfile = options['inputFile']
        else:
            print "Descargando argentina.osm de geofabrik:",
            url = "http://download.geofabrik.de/openstreetmap/south-america/argentina.osm.bz2"
            print url
            f, d = urllib.urlretrieve(url, inputfile+".bz2", lambda nb, bs, fs, url=url: self.reporthook(nb,bs,fs,url))
            print "Descomprimiendo"
            subprocess.Popen(["bunzip2", "-vvf", inputfile+".bz2"]).wait()
            os.chmod(inputfile, S_IROTH | S_IRUSR | S_IROTH | S_IWOTH | S_IWUSR | S_IWOTH)

        dbname = connection.settings_dict['NAME']
        dbuser = "postgres"#connection.settings_dict['USER']
        dbpass = "postgres"#connection.settings_dict['PASSWORD']
        dbhost = "localhost"#connection.settings_dict['HOST']

        cu = connection.cursor()
        cu.execute("SELECT slug, st_box(poligono::geometry) as box FROM catastro_ciudad;")

        primera = True
        for c in cu.fetchall():
            print ">>- ACTUALIZANDO " + c[0]
            print "st_box: " + c[1]
            l = c[1][1:-1].replace(")", "").replace("(", "").split(",")
            box = ",".join([l[2], l[3], l[0], l[1]])
            print "box: " + box

            if primera:
                prog = ["osm2pgsql"      , "-s" if options['slim'] else "", "-l", "-S"+os.path.join(os.path.abspath(os.path.dirname(__file__)),"update-osm.style"), "-d"+dbname, "-U"+dbuser, "-b"+box, inputfile ]
                primera = False
            else:
                prog = ["osm2pgsql", "-a", "-s" if options['slim'] else "", "-l", "-S"+os.path.join(os.path.abspath(os.path.dirname(__file__)),"update-osm.style"), "-d"+dbname, "-U"+dbuser, "-b"+box, inputfile ]
            print "ejecutando:",
            print prog
            p = subprocess.Popen(prog, env={"PGPASSWORD": dbpass} )
            p.wait()


        #POST PROCESAMIENTO
        print "POSTPROCESO"
        print " => Dando nombres alternativos a los objetos sin nombre"
        print " => NOTA: si esto no se puede completar es porque el usuario 'postgres' debe tener 'trust' en el archivo 'pg_hba.conf' para 'local'"
        superCu = connect(user="postgres", database=dbname).cursor()
        superCu.execute("update planet_osm_line    set name=ref where name is null;")
        superCu.execute("update planet_osm_point   set name=ref where name is null;")
        superCu.execute("update planet_osm_polygon set name=ref where name is null;")
        superCu.execute("update planet_osm_roads   set name=ref where name is null;")
        superCu.close()
        print " => Juntando tablas de caminos, normalizando nombres"
        cu.execute("delete from catastro_calle")
        cu.execute("insert into catastro_calle(way, nom_normal, nom) select way, upper(translate(name, 'áéíóúÁÉÍÓÚäëïöüÄËÏÖÜñÑàèìòùÀÈÌÒÙ', 'AEIOUAEIOUAEIOUAEIOUNNAEIOUAEIOU')), name from planet_osm_line where name is not null;")
        cu.execute("insert into catastro_calle(way, nom_normal, nom) select way, upper(translate(name, 'áéíóúÁÉÍÓÚäëïöüÄËÏÖÜñÑàèìòùÀÈÌÒÙ', 'AEIOUAEIOUAEIOUAEIOUNNAEIOUAEIOU')), name from planet_osm_roads where name is not null;")
        print " => Generando POIs a partir de poligonos y lugares, normalizando nombres"
        cu.execute("delete from catastro_poi")
        cu.execute("insert into catastro_poi(latlng, nom_normal, nom) select ST_Centroid(way), upper(translate(name, 'áéíóúÁÉÍÓÚäëïöüÄËÏÖÜñÑàèìòùÀÈÌÒÙ', 'AEIOUAEIOUAEIOUAEIOUNNAEIOUAEIOU')), name||coalesce(', '||(select name from catastro_zona zo where ST_Intersects(ST_Centroid(way), zo.geo)), '') from planet_osm_polygon as pop where name is not null;")
        cu.execute("insert into catastro_poi(latlng, nom_normal, nom) select latlng, upper(translate(nom, 'áéíóúÁÉÍÓÚäëïöüÄËÏÖÜñÑàèìòùÀÈÌÒÙ', 'AEIOUAEIOUAEIOUAEIOUNNAEIOUAEIOU')), nom||coalesce(', '||(select nom from catastro_zona zo where ST_Intersects(latlng, zo.geo)), '') from catastro_poi where nom is not null;")
        print " => Purgando nombres repetidos"
        cu.execute("delete from catastro_poi where id not in (select min(id) from catastro_poi group by nom_normal having count(*) > 1)")
        transaction.commit_unless_managed()

        #print " => Eliminando tablas no usadas"
        #cu.execute("drop table planet_osm_roads;")
        #cu.execute("drop table planet_osm_polygon;")
        #cx.commit()
        #cx.close()
