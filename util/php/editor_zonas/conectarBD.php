<?php

	$conn = pg_pconnect("host=localhost dbname=geocualbondidb user=geocualbondiuser password=geocualbondipass");
	if (!$conn) {
		echo "An error occured in connection.\n";
		exit;
	}


/* listado de tablas
geography_columns, geometry_columns, linea, log, log_resultado, lugar, planet_osm_line, planet_osm_point, planet_osm_polygon, planet_osm_roads, ramal, recorrido, spatial_ref_sys, recorrido_id_seq,  ramal_id_seq, lugar_id_seq, log_id_seq, linea_id_seq
*/

?>
