init = function() {
    
    var groupAll = new L.featureGroup()
    
    function atras() {
        if (typeof navigator.app !== 'undefined')
            navigator.app.backHistory()
        else
            history.back()
    }
    
    document.addEventListener("backbutton", function(e){
        if($.mobile.activePage.is('#inicio')){
            e.preventDefault();
            if (typeof navigator.app !== 'undefined')
                navigator.app.exitApp();
            else
                alert('salir de la app')
        }
        else {
            atras()
        }
    }, false);
    
    $(".back").click(function(e) {
        atras()
        if ($.mobile.activePage.is("#form-busqueda"))
            {}
    })
    
    $.support.cors = true;
    $.mobile.defaultPageTransition = 'slide';
    var API_ENDPOINT = "http://cualbondi.com.ar/api/";
    var CIUDAD       = null;

    //if (typeof navigator.connection !== 'undefined' && navigator.connection.type == Connection.NONE)
    //    alert('No se detecta conexión de internet. Por favor, conéctate para poder usar la aplicación');
    //else {
        var API_ENDPOINT = "http://cualbondi.com.ar/api/";
            $("#tmpl-listCiudades").tmpl({'data': [
                {"slug":"bahia-blanca",  "nombre":"Bahía Blanca"},
                {"slug":"buenos-aires",  "nombre":"Buenos Aires"},
                {"slug":"cordoba",       "nombre":"Córdoba"},
                {"slug":"la-plata",      "nombre":"La Plata"},
                {"slug":"mar-del-plata", "nombre":"Mar del Plata"},
                {"slug":"mendoza",       "nombre":"Mendoza"},
                {"slug":"rosario",       "nombre":"Rosario"},
                {"slug":"salta",         "nombre":"Salta"},
                {"slug":"santa-fe",      "nombre":"Santa Fé"}
            ]}).appendTo($("#listCiudades").empty());
            $("#listCiudades").trigger('create')
            $('#listCiudades a').on('click', function(e){
                e.preventDefault();
                CIUDAD = $(this).attr('data-slug');
                $.mobile.changePage("#form-busqueda");
            });
          /*      
        $.ajax({
            url: API_ENDPOINT + "ciudades/",
            dataType: 'jsonp'
        }).done(function(data, textStatus, jqXHR) {
            $("#tmpl-listCiudades").tmpl({'data': data}).appendTo($("#listCiudades").empty());
        }).fail(function(jqXHR, textStatus, errorThrown) {
            //alert("Error");
            $("#tmpl-listCiudades").tmpl({'data': [{"slug":"la-plata","nombre":"La Plata"},{"slug":"buenos-aires","nombre":"Buenos Aires"}]}).appendTo($("#listCiudades").empty());
        }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown) {
            $("#listCiudades").trigger('create')
            $('#listCiudades a').on('click', function(e){
                e.preventDefault();
                CIUDAD = $(this).attr('data-name');
                $.mobile.changePage("#opciones");
            });
        });
        */


        $("#boton_buscar").click(function(event) {
            event.preventDefault();
            
            $("#tmpl-loader").tmpl().appendTo($("#suggest_Origen_list").empty());
            $("#tmpl-loader").tmpl().appendTo($("#suggest_Destino_list").empty());
            var origen = $("#origen").val();
            var destino = $("#destino").val();
            var slider = $("#slider").val();

            if (origen !== '' && destino !== '') {

                $.mobile.changePage("#sugerencias");
                
                $.ajax({
                    url: API_ENDPOINT  + "catastro/?query=" + origen + "&ciudad=" + CIUDAD,
                    dataType: 'jsonp'
                }).done(function(data, textStatus, jqXHR){
                    $("#listSuggest").tmpl({'data': data, 'punto': 'Origen'}).appendTo($("#suggest_Origen_list").empty());
                    $("#suggest_Origen").listview()
                    $("#suggest_Origen").trigger("create")
                }).fail(function(jqXHR, textStatus, errorThrown){
                    alert("Error");
                });
                
                $.ajax({
                    url: API_ENDPOINT  + "catastro/?query=" + destino + "&ciudad=" + CIUDAD,
                    dataType: 'jsonp'
                }).done(function(data, textStatus, jqXHR){
                    $("#listSuggest").tmpl({'data': data, 'punto': 'Destino'}).appendTo($("#suggest_Destino_list").empty());
                    $("#suggest_Destino").listview()
                    $("#suggest_Destino").trigger("create")
                }).fail(function(jqXHR, textStatus, errorThrown){
                    alert("Error");
                });
            }
            else {
                $("#tmpl-errorSuggest").tmpl({'msg': 'Origen y Destino no deben estar vacios.'}).appendTo($("#opciones_errors").empty());
            }
        });

        $("#boton_aceptar_sugg").click(function(event) {
            event.preventDefault();
            var origen = $("#controlgroup_Origen input:checked");
            var destino = $("#controlgroup_Destino input:checked");
            if (origen.length > 0 && destino.length > 0){
                origen = origen.val().replace("POINT(", "").replace(")","").replace(" ", ",");
                destino = destino.val().replace("POINT(", "").replace(")","").replace(" ", ",");
                var radio = $("#slider").val();

                $.ajax({
                     url: API_ENDPOINT + "recorridos/?origen=" + origen + "&destino=" + destino + "&radio_origen=" + radio + "&radio_destino=" + radio + "&c=" + CIUDAD + "&combinar=false",
                     dataType: 'jsonp',
                     success:function(data){
                        if (data.resultados.length > 0){
                            $("#listResultados").tmpl(data).appendTo($("#resultados_content").empty());
                            $("#resultados_content").trigger("create");
                        }else{
                            $("#resultados_content").html("<p>No se han encontrado resultados...</p>");
                        }
                     },
                     error:function(){
                         alert("Error");
                     }
                });
                $("#resultados_content").empty();
                $.mobile.changePage("#resultados");
            }else{
                $("#tmpl-errorSuggest").tmpl({'msg': 'Debe seleccionar origen y destino'}).appendTo($("#suggest_errors").empty());
            }
        });


        $(document).bind( "pagebeforechange", function( e, data ) {
            if ( typeof data.toPage === "string" ) {
                var url = $.mobile.path.parseUrl( data.toPage ),
                    re = /^#resultado-mapa/;

                if ( url.hash.search(re) !== -1 ) {
                    var idRes = url.hash.replace( /.*id=/, "" )
                    var $page = $( "#resultado-mapa" )
                    var $map  = $page.children( "#map-res" )
                    
                    $page.page();
                    if (typeof map === 'undefined') {
                        map = new L.Map('map-res');
                        var osmUrl='http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
                        var osmAttrib='Map data © OpenStreetMap contributors';
                        var osm = new L.TileLayer(osmUrl, {maxZoom: 17, attribution: osmAttrib});		

                        // start the map in South-East England
                        map.setView(new L.LatLng(51.3, 0.7),9);
                        map.addLayer(osm);
                    }

                    groupAll.clearLayers()

                    var llA = $("#controlgroup_Origen input:checked").val().replace("POINT(", "").replace(")","").split(" ").reverse();
                    var llB = $("#controlgroup_Destino input:checked").val().replace("POINT(", "").replace(")","").split(" ").reverse();
                    
                    var mA = L.marker(llA, {icon: new L.Icon.Default({iconUrl:"img/markerA.png",shadowUrl:"img/marker-shadow.png"})});
                    mA.bindPopup($("#controlgroup_Origen input:checked").next().find(".ui-btn-text").html())
                    
                    var mB = L.marker(llB, {icon: new L.Icon.Default({iconUrl:"img/markerB.png",shadowUrl:"img/marker-shadow.png"})});
                    mB.bindPopup($("#controlgroup_Destino input:checked").next().find(".ui-btn-text").html())
                    
                    var r = new Array();
                    $.RC4.decode($("#res-" + idRes).data("geo")).replace("LINESTRING(", "").replace(")","").split(",").forEach(function (e) {
                        p = e.split(" ");
                        r.push([parseFloat(p[1]), parseFloat(p[0])]);
                    })
                    console.log(r)
                    var ruta = L.polyline(r, {color:"black"});

                    groupAll = new L.featureGroup([mA, mB, ruta]);
                    groupAll.addTo(map)
                        
                    $.mobile.changePage( $page, {"dataUrl":url.href} );
                    $page.on("pageshow", function(event, ui) {
                        map.invalidateSize()
                        map.fitBounds(groupAll.getBounds());
                    })

                    e.preventDefault();
                }
            }
        })

    //}
};


$(init);
document.addEventListener('deviceready', init, false);
