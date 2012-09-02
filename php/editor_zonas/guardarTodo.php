<?php
	include("conectarBD.php");
	$data = $_POST["data"];
	foreach ($data as $v) {
		$id   = $v["id"];
		$name = $v["name"];
		$geo  = $v["geo"];
		if ( $id == "undefined" ) {
			//la ciudad todavia no existe, insertar el recorrido y luego los puntos
			if ( substr($geo, 0, 5) !== "POINT" )
				$consulta = "
					INSERT INTO catastro_zona(name, geo)
						VALUES('$name', '$geo'::Geography)
				;";
		}
		else {
			//la ciudad ya existe, debo borrar todos los puntos, e insertar los nuevos
			$consulta = "
				UPDATE catastro_zona SET 
					name='$name',
					geo ='$geo'::Geography
				WHERE
					id='$id'
			;";
		}

		echo $consulta;
		$res = pg_query($consulta);
		if ($res) echo '<div id="status">OK</div>';
		else echo '<div id="status">NOK</div>';

	}
?>
