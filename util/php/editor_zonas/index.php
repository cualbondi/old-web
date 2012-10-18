<html>
	<head>
		<title>Editar ciudades</title>
		<script src="http://openlayers.org/api/OpenLayers.js"></script>
        <script src="http://maps.google.com/maps/api/js?v=3.3&amp;sensor=false"></script>
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js"></script>
		<script defer="defer" type="text/javascript">
		
	        var map, wkt, ctlPoly, ctlCen, ctlDrag, vlayer, map, polygonControl, modifyControl, snap;
			function load() {

				map = new OpenLayers.Map({
					div: "map",
					projection: new OpenLayers.Projection("ESRI:4326")
				});
				
				var defaultStyle = new OpenLayers.Style(
	        	{
			        strokeColor: "#DD5555",
			        strokeOpacity: 1,
			        strokeWidth: 3,
			        fillColor: "#DD5555",
			        fillOpacity: 0.5,
			        pointRadius: 6,
			        //pointerEvents: "visiblePainted",
			        //label : "${name}",
			        //fontColor: "${favColor}",
			        fontSize: "10px",
			        fontFamily: "Tahoma",
			        //fontWeight: "bold",
			        //labelAlign: "${align}",
			        //labelXOffset: "${xOffset}",
			        //labelYOffset: "${yOffset}"
	        	})

				var rules = [
					new OpenLayers.Rule(
					{
						filter: new OpenLayers.Filter.Comparison(
						{
							type: OpenLayers.Filter.Comparison.NOT_EQUAL_TO,
							property: "name",
							value: undefined
						}),
						symbolizer:
						{
							label: "${name}"
						},
						elseFilter: false
					}),
					new OpenLayers.Rule({
						symbolizer: {},
						elseFilter: true
					}) 
				];

				defaultStyle.addRules( rules ); 

				var osm = new OpenLayers.Layer.OSM();            
				var gmap = new OpenLayers.Layer.Google("Google v3");
				vlayer = new OpenLayers.Layer.Vector(
					"Editable", 
					{
				        styleMap: new OpenLayers.StyleMap(
				        {
				        	'default': defaultStyle
				        })
					}
				)

				map.addLayers( [gmap, osm, vlayer] );

				//map.addControl( new OpenLayers.Control.PanZoom() );
				map.addControl( new OpenLayers.Control.LayerSwitcher() );
				map.addControl( new OpenLayers.Control.MousePosition() );
				//map.addControl( new OpenLayers.Control.Navigation({documentDrag:true}) );

				wkt = new OpenLayers.Format.WKT({
					'internalProjection': new OpenLayers.Projection("EPSG:900913"),
					'externalProjection': new OpenLayers.Projection("EPSG:4326")
				});

				map.setCenter(
					new OpenLayers.LonLat(-64, -36).transform(
						new OpenLayers.Projection("EPSG:4326"),
						map.getProjectionObject()
					), 
					5
				);

				var navControl = new OpenLayers.Control.Navigation({title: 'Pan/Zoom'});
				var editPanel = new OpenLayers.Control.Panel({displayClass: 'olControlEditingToolbar'});
				polygonControl = new OpenLayers.Control.DrawFeature(
					vlayer,
					OpenLayers.Handler.Polygon,
					{
						displayClass: 'olControlDrawFeaturePolygon'
					}
				)
				modifyControl = new OpenLayers.Control.ModifyFeature(
					vlayer,
					{
						title: 'Edit feature'
					}
				)
			    //modifyControl.mode =
			    //	OpenLayers.Control.ModifyFeature.DRAG |
			    //	OpenLayers.Control.ModifyFeature.RESIZE |
				//	OpenLayers.Control.ModifyFeature.ROTATE;
				editPanel.addControls([
					polygonControl,
					modifyControl,
					navControl
				]);
				editPanel.defaultControl = navControl;
				map.addControl(editPanel);

				snap = new OpenLayers.Control.Snapping({
					layer: vlayer,
					targets: [{
						layer: vlayer,
						node: true,
						nodeTolerance: 20,
						vertex: true,
						vertexTolerance: 20,
						edge: true,
						edgeTolerance: 20
					}],
					greedy: false
				});
				map.addControl(snap);
				snap.activate();

				$.ajax(
					{
						url:'get_zonas.php',
						success: function (data) {
							//alert(data)
							data = jQuery.parseJSON(data)
							//alert(data)
							for ( var i in data) {
								var feature = wkt.read(data[i].geo)
								feature.attributes = { name : data[i].name, id: data[i].id }
								vlayer.addFeatures([feature])
								//$.
							}
							vlayer.events.on({
								beforefeaturemodified: function(obj) {
									$('#nombre').val(obj.feature.attributes.name)
									$("#id_bd").val(obj.feature.attributes.id);
									$("#id_ol").val(obj.feature.id);
									vlayer.drawFeature(obj.feature)
								},
								afterfeaturemodified: function(obj) {
									while ( $('#nombre').val() == "" )
										$('#nombre').val(window.prompt("Dale un nombre a esa nueva zona",""))
									obj.feature.attributes.name = $('#nombre').val()
									$('#nombre').val("")
									$("#id_bd").val("");
									$("#id_ol").val("");
									vlayer.drawFeature(obj.feature)
								},
								featureadded: function(obj) {
									while ( $('#nombre').val() == "" )
										$('#nombre').val(window.prompt("Dale un nombre a esa nueva zona",""))
									obj.feature.attributes.name = $('#nombre').val()
									$('#nombre').val("")
									$("#id_bd").val("");
									$("#id_ol").val("");
									vlayer.drawFeature(obj.feature)
								}
							});
						}
					}
				)
				
			}
			
			function guardarTodo() {
				$('#status').html = 'Guardando: Enviando datos...';
				var obj = new Array()
				for (var i in vlayer.features)
					obj.push({
						id:   vlayer.features[i].attributes.id,
						geo:  vlayer.features[i].geometry.transform(
								new OpenLayers.Projection("EPSG:900913"),
								new OpenLayers.Projection("EPSG:4326")
							).toString(),
						name: vlayer.features[i].attributes.name
					})
				//alert(obj)
				//alert(obj.toString())
				$('#status').load(
					"guardarTodo.php #status",
					{data: obj}
//					function(data) {
//						$('#status').html(data);
//					}
				);
			}

		</script>

		<link rel="stylesheet" href="http://openlayers.org/api/theme/default/style.css" type="text/css" />
	</head>
	<body onload="load()">
		<div style="width:78%; height:100%; float:left" id="map"></div>
		<div style="width:18%; height:100%; float:left" id="info">
			<label for="id_bd">id_BD</label>
			<input id="id_bd" readonly></input>
			<br>
			<label for="id_ol">id_OL</label>
			<input id="id_ol" readonly></input>
			<br>
			<label for="nombre">Nombre</label>
			<input id="nombre"></input>
			<br>
			<input type="button" onclick="javascript:guardarTodo()" value="Guardar Todo!"></input>
			<div id="status"></div>
		</div>
	</body>
</html>
