//Proyeccion que se necesita para transformar proyecciones mas adelante
var proj = new OpenLayers.Projection("EPSG:4326");

//Creamos el mapa
map = new OpenLayers.Map("map", {theme: null})
var gmap = new OpenLayers.Layer.Google(
    "Google Streets", {numZoomLevels: 20}
);
map.addLayers([gmap]);
map.setCenter(new OpenLayers.LonLat(ciudad_actual_coord1, ciudad_actual_coord2).transform(
    new OpenLayers.Projection("EPSG:4326"),
    map.getProjectionObject()
), ciudad_actual_zoom);

//Le agregamos una capa para el poligono de la ciudad
var style = {'strokeWidth': 4, 'strokeColor': '#0033CC', fillColor: "#0066CC", fillOpacity: 0.5}
var layer_recorrido = new OpenLayers.Layer.Vector("Recorrido", {styleMap: new OpenLayers.StyleMap(style) });
map.addLayer(layer_recorrido)

//Le agregamos una capa para los Markers de inicio y fin
var markers = new OpenLayers.Layer.Markers( "Markers" );
map.addLayer(markers);

var size = new OpenLayers.Size(20,50);
var offset = new OpenLayers.Pixel(-(size.w/2), -size.h);
var iconA = new OpenLayers.Icon(STATIC_URL+'css/openlayers/markerA.png',size,offset);
var iconB = new OpenLayers.Icon(STATIC_URL+'css/openlayers/markerB.png',size,offset);

var lonlat_inicio = new OpenLayers.LonLat(lonlat_ini_coord1, lonlat_ini_coord2);
var lonlat_fin = new OpenLayers.LonLat(lonlat_fin_coord1, lonlat_fin_coord2);

lonlat_inicio = lonlat_inicio.transform(proj, map.getProjectionObject());
lonlat_fin = lonlat_fin.transform(proj, map.getProjectionObject());

markers.addMarker(new OpenLayers.Marker(lonlat_inicio, iconA));
markers.addMarker(new OpenLayers.Marker(lonlat_fin, iconB));

$.get("/api/recorridos/"+recorrido_actual_id+"/",
    function(data) {
        path_recorrido = new OpenLayers.Format.WKT().read($.RC4.decode(data.ruta));
        path_recorrido.geometry.transform(proj, map.getProjectionObject())
        layer_recorrido.addFeatures([path_recorrido]);

        //Acomodar el zoom al poligono
        var extent = new OpenLayers.Bounds();
        extent.extend(path_recorrido.geometry.getBounds())
        map.zoomToExtent(extent);
    },
    "json"
);
