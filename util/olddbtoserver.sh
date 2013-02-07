#!/bin/sh
echo "dumping b2zipping"
pg_dump --inserts -trecorrido -tlinea -tramal -tciudad -tciudad_linea -c colectivos -Upostgres -hlocalhost | bzip2 > /tmp/dump.bz2

echo "sending file"
rsync -v -e ssh /tmp/dump.bz2 cualbondi@cualbondi.com.ar:~

echo "bunzipping & inserting in database in remote host"
ssh cualbondi@cualbondi.com.ar "bunzip2 dump.bz2 -c | psql -Upostgres -h127.0.0.1 colectivos"
