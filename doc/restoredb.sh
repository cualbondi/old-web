#!/bin/bash

DATABASE=$1
echo "Iniciando script para la base de datos '$DATABASE'..."

echo "Eliminando DB..."
dropdb $DATABASE

echo "Creando nueva DB..."
createdb $DATABASE --owner=postgres

echo "Instalando PostGIS..."
createlang plpgsql $DATABASE
psql -d $DATABASE -f /usr/share/postgresql/8.4/contrib/postgis-1.5/postgis.sql
psql -d $DATABASE -f /usr/share/postgresql/8.4/contrib/postgis-1.5/spatial_ref_sys.sql
psql -d $DATABASE -f /usr/share/postgresql/8.4/contrib/postgis_comments.sql

echo "Finalizado!"
