<?php

	include("conectarBD.php");
	
	$consulta = "
		SELECT
			st_astext(geo) as geo,
			name,
			id
		FROM
			catastro_zona
	;";

	//echo $consulta;
	echo json_encode(pg_fetch_all(pg_query($consulta)));
	
	
?>
