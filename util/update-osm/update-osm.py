#!/usr/bin/python
# -*- coding: utf-8 -*-

import pwd, os
import psycopg2
import urllib
import subprocess
from stat import *
import sys

if os.getuid()==pwd.getpwnam('postgres')[2]:

    print "Comenzando actualizacion. En caso de errores recuerde instalar"
    print "sudo apt-get install osm2pgsql python-psycopg2"

    HOST="127.0.0.1"
    BASE="geocualbondidb"
    USER="geocualbondiuser"
    PASS="geocualbondipass"
    SUPERUSER="postgres"

    def _reporthook(numblocks, blocksize, filesize, url=None):
        base = os.path.basename(url)
        try:
            percent = min((numblocks*blocksize*100)/filesize, 100)
        except:
            percent = 100
        if numblocks != 0:
            sys.stdout.write("\b"*70)
        sys.stdout.write("%-66s%3d%%" % (base, percent))

    nom = "argentina.osm"
    if len(sys.argv) > 1:
        print "no se descargara argentina.osm, se buscara en el directorio actual"
    else:
        print "Descargando argentina.osm de geofabrik:",
        url = "http://download.geofabrik.de/osm/south-america/argentina.osm.bz2"
        nom = "argentina.osm"
        print url
        f, d = urllib.urlretrieve(url, nom+".bz2", lambda nb, bs, fs, url=url: _reporthook(nb,bs,fs,url))
        print "Descomprimiendo"
        subprocess.Popen(["bunzip2", "-vvf", nom+".bz2"]).wait()
        os.chmod(nom, S_IROTH)

    cx = psycopg2.connect(dbname=BASE, user=SUPERUSER)
    cu = cx.cursor()
    cu.execute("SELECT nombre, st_box(poligono::geometry) FROM catastro_ciudad;")

    primera = True
    for i in cu:
        print ">>- ACTUALIZANDO " + str(i[0])
        l = i[1][1:-1].replace(")", "").replace("(", "").split(",")
        box = ",".join([l[2], l[3], l[0], l[1]])
        
        if primera:
            prog = ["osm2pgsql", "-Supdate-osm.style", "-d"+BASE, "-l", "-b" + box, nom]
            primera = False
        else:
            prog = ["osm2pgsql", "-Supdate-osm.style", "-d"+BASE, "-l", "-a", "-b" + box, nom]
        print "ejecutando:",
        print prog
        p = subprocess.Popen(prog)
        p.wait()

    #"""#print "eliminando residuos..."
    #os.remove(nom)

    #POST PROCESAMIENTO
    print "POSTPROCESO"
    print " => Dando nombres alternativos a los objetos sin nombre"
    cu.execute("update planet_osm_line    set name=ref where name is null;")
    cu.execute("update planet_osm_point   set name=ref where name is null;")
    cu.execute("update planet_osm_polygon set name=ref where name is null;")
    cu.execute("update planet_osm_roads   set name=ref where name is null;")
    print " => Juntando tablas de caminos, normalizando nombres"
    cu.execute("delete from catastro_calle")
    cu.execute("insert into catastro_calle(way, nom_normal, nom) select way, upper(translate(name, 'áéíóúÁÉÍÓÚäëïöüÄËÏÖÜñÑàèìòùÀÈÌÒÙ', 'AEIOUAEIOUAEIOUAEIOUNNAEIOUAEIOU')), name from planet_osm_line where name is not null;")
    cu.execute("insert into catastro_calle(way, nom_normal, nom) select way, upper(translate(name, 'áéíóúÁÉÍÓÚäëïöüÄËÏÖÜñÑàèìòùÀÈÌÒÙ', 'AEIOUAEIOUAEIOUAEIOUNNAEIOUAEIOU')), name from planet_osm_roads where name is not null;")
    print " => Generando POIs a partir de poligonos y lugares, normalizando nombres"
    cu.execute("delete from catastro_poi")
    cu.execute("""
        insert into
            catastro_poi(
                latlng,
                nom_normal,
                nom
            )
            select
                ST_Centroid(way),
                upper(
                    translate(
                        name, 
                        'áéíóúÁÉÍÓÚäëïöüÄËÏÖÜñÑàèìòùÀÈÌÒÙ', 
                        'AEIOUAEIOUAEIOUAEIOUNNAEIOUAEIOU'
                    )
                ),
                name ||
                    coalesce(
                        ', ' ||
                        (select
                            name
                         from
                            catastro_ciudad zo
                         where
                            ST_Intersects(
                                ST_Centroid(way),
                                zo.poligono
                            )
                         limit 1
                        ),
                        ''
                    )
            from
                planet_osm_polygon as pop
            where
                name is not null
    ;""")
    cu.execute("insert into catastro_poi(latlng, nom_normal, nom) select centro, upper(translate(nombre, 'áéíóúÁÉÍÓÚäëïöüÄËÏÖÜñÑàèìòùÀÈÌÒÙ', 'AEIOUAEIOUAEIOUAEIOUNNAEIOUAEIOU')), nombre||coalesce(', '||(select nombre from catastro_ciudad zo where ST_Intersects(centro, zo.poligono) LIMIT 1), '') from catastro_ciudad where nombre is not null;")
    print " => Purgando nombres repetidos"
    cu.execute("delete from catastro_poi where id not in (select min(id) from catastro_poi group by nom_normal)")
    #print " => Cambiando permisos"
    #cu.execute("grant select,update,insert,delete on  to $DB_USER")


    #print " => Eliminando tablas no usadas"
    #cu.execute("drop table planet_osm_roads;")
    #cu.execute("drop table planet_osm_polygon;")
    cx.commit()
    cx.close()

else:
    print "debe correr el programa como usuario postgres"
