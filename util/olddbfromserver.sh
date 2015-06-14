#!/bin/sh

ID=$RANDOM

echo "dumping b2zipping"
ssh -t cualbondi.com.ar "su root -c \"su postgres -c \\\"pg_dump --inserts -c geocualbondidb -Upostgres | bzip2 > /tmp/dump-$ID.bz2\\\"\""

echo "sending file"
rsync -v -e ssh cualbondi.com.ar:/tmp/dump-$ID.bz2 /tmp/dump-$ID.bz2

echo "bunzipping & inserting in database in local host"
bunzip2 /tmp/dump-$ID.bz2 -c | vagrant ssh -c "sudo -u postgres psql -Upostgres cualbondi"