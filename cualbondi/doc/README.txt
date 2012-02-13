CualBondi V2.0 - DOCUMENTACION


===================================FIXTURES=====================================
DUMP    =>  python manage.py dumpdata --indent 4 core.Ciudad > apps/core/fixtures/ciudad.json
LOAD    =>  python manage.py loaddata apps/core/fixtures/ciudad.json
================================================================================


===================================VER CIUDAD===================================
-Datos de la ciudad
    -nombre
    -mapa
    -descripcion
-Pois
-Recorridos
-Comentarios
-Comercios
================================================================================

http://maps.google.com/maps/api/staticmap?size=480x480&path=color:0x0000ff|weight:5|40.737102,-73.990318|40.749825,-73.987963|40.752946,-73.987384|40.755823,-73.986397&sensor=false
