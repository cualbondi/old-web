#!/bin/sh
echo "dumping b2zipping"
ssh cualbondi@cualbondi.com.ar "su root -c \"su postgres -c \\\"pg_dump --inserts -trecorrido -tlinea -tramal -tciudad -tciudad_linea -c colectivos -Upostgres -hlocalhost | bzip2 > /tmp/dump.bz2\\\"\""

echo "sending file"
rsync -v -e ssh cualbondi@cualbondi.com.ar:/tmp/dump.bz2 ~

echo "bunzipping & inserting in database in remote host"
bunzip2 dump.bz2 -c | psql -Upostgres -h127.0.0.1 colectivos

# NOTA: poner bien el nombre de la BD y de las tablas a backupear
