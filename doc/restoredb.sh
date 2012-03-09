#!/bin/bash

DATABASE=$1
USUARIO=$2
echo "Iniciando script para la base de datos '$DATABASE'..."

echo "Eliminando DB..."
dropdb $DATABASE

echo "Creando nueva DB..."
createdb $DATABASE --owner=$USUARIO

echo "Instalando PostGIS..."
createlang plpgsql $DATABASE
psql -d $DATABASE -f /usr/share/postgresql/9.1/contrib/postgis-1.5/postgis.sql
psql -d $DATABASE -f /usr/share/postgresql/9.1/contrib/postgis-1.5/spatial_ref_sys.sql
psql -d $DATABASE -f /usr/share/postgresql/9.1/contrib/postgis_comments.sql

psql -d $DATABASE -c "GRANT ALL PRIVILEGES ON spatial_ref_sys TO $USUARIO"
psql -d $DATABASE -c "GRANT ALL PRIVILEGES ON geometry_columns TO $USUARIO"

echo "Finalizado!"
