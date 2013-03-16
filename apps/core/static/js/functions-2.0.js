        function check_layout(){
            if ($(window).width() > 980){
                // bootstrap 100% height (similar googlemaps)
                $("#bloque_derecha").height($(window).height()-40+"px");
                $("#bloque_izquierda").height($(window).height()-60+"px");
                $("#bloque_derecha").width($(window).width()-$("#bloque_izquierda").width()-26+"px");
            }else{
                // para tables y celulares, mapa abajo de los resultados
                $("#bloque_derecha").width("100%");
                $("#bloque_izquierda").height("auto");
            }
        }

        $(function() {

            $("#ayudaTempl").tmpl().appendTo($("#sidebarResultados").empty());

            function preload(arrayOfImages) {
                $(arrayOfImages).each(function(){
                    $('<img/>')[0].src = this;
                    // Alternatively you could use:
                    // (new Image()).src = this;
                });
            };

            preload([
                STATIC_URL+"css/openlayers/markerA.png"      ,
                STATIC_URL+"css/openlayers/markerA-hover.png",
                STATIC_URL+"css/openlayers/markerA-drag.png" ,
                STATIC_URL+"css/openlayers/markerB.png"      ,
                STATIC_URL+"css/openlayers/markerB-hover.png",
                STATIC_URL+"css/openlayers/markerB-drag.png"
            ]);

            // definicion inicial del mapa
            OpenLayers.ImgPath = STATIC_URL+"css/openlayers/"
            var map = new OpenLayers.Map("mapa", {theme: null})
            var gmap = new OpenLayers.Layer.Google(
                "Google Streets", {numZoomLevels: 20}
            );
            var osm = new OpenLayers.Layer.OSM();
            map.addLayers([gmap, osm]);
            //var gmap = new OpenLayers.Layer.Google("Google Streets", {visibility: false});
            //map.addLayers([osm, gmap]);
            //map.addControl(new OpenLayers.Control.LayerSwitcher());
            map.setCenter(new OpenLayers.LonLat(ciudad_actual_coord1, ciudad_actual_coord2).transform(
                new OpenLayers.Projection("EPSG:4326"),
                map.getProjectionObject()
            ), ciudad_actual_zoom);

            map.zoomOut() //esto es para que el mapa se redibuje (workaround de redraw)
            //map.setCenter(map.center())

            // estilos de los markers
            var styleMap = new OpenLayers.StyleMap({fillColor: '#1166EE', fillOpacity: 0.2, strokeColor: '#1166EE', strokeOpacity: 0.3, strokeWidth: 2});
            lookup = {
                // nombre:hovering:dragging
                "A:false:false": { externalGraphic: STATIC_URL+"css/openlayers/markerA.png", graphicWidth: 20, graphicHeight: 50, graphicYOffset: -50, graphicOpacity: 1 },
                "A:true:false" : { externalGraphic: STATIC_URL+"css/openlayers/markerA-hover.png", graphicWidth: 20, graphicHeight: 50, graphicYOffset: -50, graphicOpacity: 1 },
                "A:false:true" : { externalGraphic: STATIC_URL+"css/openlayers/markerA-drag.png", graphicWidth: 20, graphicHeight: 50, graphicYOffset: -41, graphicOpacity: 1 },
                "A:true:true"  : { externalGraphic: STATIC_URL+"css/openlayers/markerA-drag.png", graphicWidth: 20, graphicHeight: 50, graphicYOffset: -41, graphicOpacity: 1 },
                "B:false:false": { externalGraphic: STATIC_URL+"css/openlayers/markerB.png", graphicWidth: 20, graphicHeight: 50, graphicYOffset: -50, graphicOpacity: 1 },
                "B:true:false" : { externalGraphic: STATIC_URL+"css/openlayers/markerB-hover.png", graphicWidth: 20, graphicHeight: 50, graphicYOffset: -50, graphicOpacity: 1 },
                "B:false:true" : { externalGraphic: STATIC_URL+"css/openlayers/markerB-drag.png", graphicWidth: 20, graphicHeight: 50, graphicYOffset: -41, graphicOpacity: 1 },
                "B:true:true"  : { externalGraphic: STATIC_URL+"css/openlayers/markerB-drag.png", graphicWidth: 20, graphicHeight: 50, graphicYOffset: -41, graphicOpacity: 1 }
            }
            styleMap.addUniqueValueRules("default", "tipo", lookup);

            // creacion de las diferentes capas
            var markers = new OpenLayers.Layer.Vector( "Markers", {
                styleMap: styleMap
                //,renderers: ["SVG2", "VML", "Canvas"] // allow render while panning when possible
            });
            var recorridos = new OpenLayers.Layer.Vector( "Recorridos", {styleMap: new OpenLayers.StyleMap({strokeWidth: 5})});
            map.addLayer(recorridos)
            map.addLayer(markers)

            // proyeccion que se necesita para transformar proyecciones mas adelante
            var proj = new OpenLayers.Projection("EPSG:4326");

            // clase Marker (para manejar el markerA y marerB mas facil)
            function Marker(layer, id, visible) {
                if (typeof(visible)=='undefined') this.visible = true
                else this.visible = visible
                this.listo  = false
                this.point  = null
                this.layer  = layer
                this.id     = id
                this.centro = null
                this.confirmado = false
                this.rad=300/Math.cos(-34.9)/Math.cos(50*(Math.PI/180));
            }
            Marker.prototype.setPoint = function(point) {
                // setea el punto con latlng y lo pone en el mapa
                // point = new OpenLayers.Geometry.Point(lon, lat);
                if (this.point == null || !this.point.attributes.dragging) {
                    try {
                        this.layer.removeFeatures([this.point])
                    }
                    catch(err) {}

                    this.centro = point
                    this.point = new OpenLayers.Feature.Vector(
                        new OpenLayers.Geometry.Collection(
                            [
                            OpenLayers.Geometry.Polygon.createRegularPolygon(point, this.rad, 20, 0),
                            point
                            ]
                        ),
                        {
                            tipo:this.id+":false:false",
                            dragging: false
                        }
                    )

                    if (this.visible) {
                        this.layer.addFeatures([this.point])
                        this.listo = true
                        //this.layer.map.moveTo(this.point)
                        this.layer.drawFeature(this.point)
                    }
                }
            }
            Marker.prototype.setRadius = function(rad) {
                var lat = -34.9;
                if ( this.centro !== null )
                    lat =(new OpenLayers.Geometry.Point(this.centro.x, this.centro.y))
                        .transform(map.getProjectionObject(), proj)
                        .y;
                this.rad=rad/Math.cos(lat)/Math.cos(50*(Math.PI/180));
                if ( this.listo )
                    this.setPoint(this.centro);
            }
            // dos objetos de la clase marker // cuidado, este código se repite mas abajo
            var markerA = new Marker(markers, "A")
            var markerB = new Marker(markers, "B")
            var markerAaux = new Marker(markers, "A", false)
            var markerBaux = new Marker(markers, "B", false)

            // manejo de clicks en el mapa
            //      creacion de los markers A y B
            //      busqueda por click en el mapa
            var clickHandler = new OpenLayers.Handler.Click(
                { 'map': map },
                {
                    'click': function(evt) {
                        var lonlat = map.getLonLatFromViewPortPx(evt.xy);
                        point = new OpenLayers.Geometry.Point(lonlat.lon, lonlat.lat);
                        if ( !markerA.listo ) {
                            markerA.setPoint(point)
                            markerAaux.setPoint(point)
                            markerA.confirmado = true
                            piwikLog("/click/mapa/marker/A")
                        }
                        else
                            if ( !markerB.listo ) {
                                markerB.setPoint(point)
                                markerBaux.setPoint(point)
                                markerB.confirmado = true
                                piwikLog("/click/mapa/marker/B")
                                clickHandler.deactivate();
                                pagina_input = 1
                                buscarporclick(markerA.centro, markerB.centro)
                            }
                    }
                }
            );

            // manejo del drag de los markers
            //      cambio de imagenes al draggear y onhover
            //      busqueda por ondrag
            dragControl = new OpenLayers.Control.DragFeature(
                markers,
                {
                    onComplete: function(feature, pixel) {
                        feature.attributes.dragging = true
                        t = feature.attributes.tipo.split(":")
                        feature.attributes.tipo=t[0]+":true:false"
                        if ( feature == markerA.point ) {
                            markerA.confirmado = true
                            markerAaux.setPoint(markerA.centro)
                            markerBaux.setPoint(markerB.centro)
                            piwikLog("/click/mapa/drag/A")
                        }
                        if ( feature == markerB.point ) {
                            markerB.confirmado = true
                            markerAaux.setPoint(markerA.centro)
                            markerBaux.setPoint(markerB.centro)
                            piwikLog("/click/mapa/drag/B")
                        }
                        if (markerA.centro !== null && markerB.centro !== null) {
                            $('a[data-toggle="tab"]').first().tab('show')
                            pagina_input = 1
                            buscarporclick(markerA.centro, markerB.centro)
                        }
                        markers.redraw()
                    },
                    onEnter: function(feature, pixel) {
                        feature.attributes.dragging = true
                        t = feature.attributes.tipo.split(":")
                        feature.attributes.tipo=t[0]+":true:false"
                        markers.redraw()
                    },
                    onLeave: function(feature, pixel) {
                        feature.attributes.dragging = false
                        t = feature.attributes.tipo.split(":")
                        feature.attributes.tipo=t[0]+":false:false"
                        markers.redraw()
                    },
                    onStart: function(feature, pixel) {
                        feature.attributes.dragging = true
                        t = feature.attributes.tipo.split(":")
                        feature.attributes.tipo=t[0]+":true:true"
                        markers.redraw()
                    }
                }
            )
            map.addControl(dragControl)

            // activar el click y drag handlers
            clickHandler.activate()
            dragControl.activate()

            // variables "globales"
            var resultados = new Object()
            resultados[true] = new Object()
            resultados[false] = new Object()
            var polylinea  = new Array()
            var polyhover  = new Array()
            var pagina_input     = 1
            var pagina_nombre    = 1
            var ajaxInputLinea = false
            var buscar     = true //false si busca de A a B, true si busca por nombre de recorrido (es para llamar la funcion correcta al paginar)

            // handler para mostrar resultados, usa el template de listado de results
            function mostrar_resultado(id, porNombre, forzarPanZoom) {
                try {
                    if ( typeof(id)==='undefined' )
                        if (porNombre)
                            id = $("#sidebarResultadosPorNombre li:first").attr("id").slice(3)
                        else
                            id = $("#sidebarResultados li:first").attr("id").slice(3)
                }
                catch (err) {
                    //console.log(err)
                    return 1
                }

                if (porNombre) {
                    $("#sidebarResultadosPorNombre li").removeClass("active")
                    $("#sidebarResultadosPorNombre #res"+id).addClass("active")
                }
                else {
                    $("#sidebarResultados li").removeClass("active")
                    $("#sidebarResultados #res"+id).addClass("active")
                }
                recorridos.removeAllFeatures()

                var polylinea = new Array()
                $.each(resultados[porNombre][id], function(key, value) {
                    var poly = new OpenLayers.Format.WKT().read($.RC4.decode(value.ruta_corta));
                    poly.geometry.transform(proj, map.getProjectionObject())
                    var style = OpenLayers.Util.extend({}, OpenLayers.Feature.Vector.style['default']);
                    style.strokeOpacity = 0.8;
                    style.strokeWidth   = 5;
                    style.strokeColor   = value.color_polilinea ? value.color_polilinea : "#000000";
                    poly.style          = style;
                    polylinea.push(poly);
                });
                recorridos.addFeatures(polylinea);
                if (porNombre) {
                    markerA.setPoint(polylinea[0].geometry.getVertices()[0]);
                    markerB.setPoint(polylinea[polylinea.length-1].geometry.getVertices()[polylinea[polylinea.length-1].geometry.getVertices().length-1]);
                }
                else {
                    markerA.setPoint(markerAaux.centro);
                    markerB.setPoint(markerBaux.centro);
                }
                if (porNombre || forzarPanZoom) {
                    map.panTo(recorridos.getDataExtent().getCenterLonLat());
                    map.zoomTo(map.getZoomForExtent(recorridos.getDataExtent())-1);
                }
            }

            function buscar_por_inputs() {
                recorridos.removeAllFeatures()
                $("#ajaxLoader").tmpl().appendTo($("#sidebarResultados").empty())
                var data1 = null
                var data2 = null
                // muestra los resultados de la busqueda como sugerencia
                function mostrarResultadoCatastro(data, id) {
                    data.id = id
                    data = $.map(data, function(item, i){item.id = id; item.domId = Math.floor(Math.random()*10000);return item});
                    if ( id == 1 ) data1=data
                    else data2=data
                    if ( data1 !== null && data2 !== null ) {
                        piwikTracker.trackSiteSearch( $("#inputDesde").val(), "Desde", data1.length )
                        piwikTracker.trackSiteSearch( $("#inputHasta").val(), "Hasta", data2.length )
                        $("#listSuggest").tmpl([{ data1: data1, data2: data2 }]).appendTo($("#sidebarResultados").empty())
                        bindearEventos(false);
                    }
                }
                $.ajax({
                    url: "/api/catastro/?query="+$("#inputDesde").val()+"&ciudad="+GLOBAL_ci,
                    success: function (data) {
                        mostrarResultadoCatastro(data, 1)
                    }
                })
                $.ajax({
                    url: "/api/catastro/?query="+$("#inputHasta").val()+"&ciudad="+GLOBAL_ci,
                    success: function (data) {
                        mostrarResultadoCatastro(data, 2)
                    }
                })
            }

            // mueve el markerA o B a el punto seleccionado
            function marcarPunto(pointWKT, id, domId) {
                // pointWKT es 'POINT(12.234 56.789)'
                // id es 1 para origen(markerA) y 2 para destino(markerB)
                var point = new OpenLayers.Format.WKT().read(pointWKT).geometry
                point.transform(proj, map.getProjectionObject())
                point = new OpenLayers.Geometry.Point(point.x, point.y);
                if ( id == 1 ) {
                    markerA.setPoint(point)
                    markerAaux.setPoint(point)
                }
                else if ( id == 2 ) {
                    markerB.setPoint(point)
                    markerBaux.setPoint(point)
                }
                map.panTo(new OpenLayers.LonLat(point.x, point.y))
                $("#sug" + domId).siblings().removeClass("active")
                $("#sug" + domId).addClass("active")
            }

            // busca una vez que se eligieron las sugerencias
            function seleccionarSugerencias() {
                markerA.confirmado = true
                markerB.confirmado = true
                if ( markerA.listo && markerB.listo ) {
                    pagina_input = 1
                    buscarporclick(markerA.centro, markerB.centro, 'false', true)
                }
            }

            // busca por transbordo
            function buscarTransbordo() {
                markerA.confirmado = true
                markerB.confirmado = true
                if ( markerA.listo && markerB.listo ) {
                    pagina_input = 1
                    buscarporclick(markerA.centro, markerB.centro, 'true')
                }
            }

            // pasa a la siguiente pagina
            // n = -1: pagina anterior
            //      x: pagina x
            //      0: pagina siguiente
            function pasarPagina(n, combinar, porNombre) {
                n = parseInt(n);
                if (porNombre) {
                    if ( n < 0 )
                        pagina_nombre = ( pagina_nombre > 1 ) ? pagina_nombre - 1 : 1;
                    else if ( n == 0 )
                        pagina_nombre+=1;
                    else if ( n > 0)
                        pagina_nombre = n;
                }
                else {
                    if ( n < 0 )
                        pagina_input = ( pagina_input > 1 ) ? pagina_input - 1 : 1;
                    else if ( n == 0 )
                        pagina_input+=1;
                    else if ( n > 0)
                        pagina_input = n;
                }

                if ( !porNombre )
                    buscarporclick(markerA.centro, markerB.centro, combinar);
                else
                    inputLinea();
            }

            // envia peticion al server para buscar por latlng
            function buscarporclick(lla, llb, combinar, forzarPanZoom) {
                if ( typeof(combinar) === 'undefined' ) combinar = 'false';
                buscar     = true
                recorridos.removeAllFeatures()
                $("#ajaxLoader").tmpl().appendTo($("#sidebarResultados").empty())
                lla = lla.transform(map.getProjectionObject(), proj)
                llb = llb.transform(map.getProjectionObject(), proj)
                $.get(
                    "/api/recorridos/",
                    {
                        origen: lla.x+","+lla.y,
                        destino: llb.x+","+llb.y,
                        radio_origen: $('#button-radio').val(),
                        radio_destino: $('#button-radio').val(),
                        c: GLOBAL_ci,
                        p: pagina_input,
                        combinar: combinar
                    },
                    function (data){
                        mostrarResultados(data, combinar, false, forzarPanZoom);
                    }
                );
                lla = lla.transform(proj, map.getProjectionObject())
                llb = llb.transform(proj, map.getProjectionObject())
            }

            // muestra los resultados devueltos por el server usando un template
            function mostrarResultados(data, combinar, porNombre, forzarPanZoom){
                if ( typeof(porNombre)==='undefined' ) porNombre = false
                if ( typeof(combinar) ==='undefined' ) combinar  = 'false'

                res = data['resultados']
                if ( res.length === 0 )
                    if ( (porNombre && pagina_nombre == 1) || (!porNombre && pagina_input == 1) ) {
                        if (porNombre)
                            $("#vacioTempl").tmpl().appendTo($("#sidebarResultadosPorNombre").empty());
                        else
                            if (combinar == 'true')
                                $("#vacio2Templ").tmpl().appendTo($("#sidebarResultados").empty());
                            else
                                $("#vacio1Templ").tmpl().appendTo($("#sidebarResultados").empty());
                        bindearEventos(porNombre);
                    }
                    else {
                        if (porNombre)
                            pagina_nombre -= 1
                        else
                            pagina_input -= 1
                    }
                else {
                    resultados[porNombre] = new Object()
                    $.each(res, function(key, value) {
                        resultados[porNombre][value.id] = value.itinerario
                    });

                    data['combinar'] = combinar;
                    data['porNombre'] = porNombre;
                    if (porNombre)
                        divResultados = $("#sidebarResultadosPorNombre")
                    else
                        divResultados = $("#sidebarResultados")

                    // calcular lista de paginas a mostrar
                    data['cant_paginas'] = Math.ceil(data['cant']/data['long_pagina']);
                    data['page_list'] = new Array();
                    for (var i=0; i<data['cant_paginas']; i++){
                        data['page_list'].push(i+1);
                    }
                    var index = $.inArray(data['p'], data['page_list']);
                    var desde = index - 3 > 0 ? index - 3 : 0;
                    var hasta = index + 3 < data['cant_paginas'] ? index + 3 : data['cant_paginas'];
                    data['page_list'] = data['page_list'].slice(desde, hasta);

                    $("#listTempl").tmpl( [{ data: data }] ).appendTo(divResultados.empty());
                    bindearEventos(porNombre);
                    divResultados.find("[id^=res]").each( function(i) {
                        $(this).children().bind("click", function(e) {
                            id = $(this).attr("id")
                            //console.log(this)
                            //console.log(porNombre)
                            mostrar_resultado(id, porNombre, true)
                            e.preventDefault()
                            if (porNombre)
                                piwikLog("/click/resultado/porNombre/"+$.map(resultados[porNombre][id], function(e){ e.name } ).join("+"))
                            else
                                piwikLog("/click/resultado/busqueda/"+$.map(resultados[porNombre][id], function(e){ e.name } ).join("+"))
                        })
                        $(this).children().bind("mouseenter", function(e) {
                            id = $(this).attr("id")
                            recorridos.removeFeatures(polyhover)
                            polyhover = new Array();
                            $.each(resultados[porNombre][id], function(key, value) {
                                var poly = new OpenLayers.Format.WKT().read($.RC4.decode(value.ruta_corta))
                                poly.geometry.transform(proj, map.getProjectionObject())
                                var style = OpenLayers.Util.extend({}, OpenLayers.Feature.Vector.style['default']);
                                style.strokeOpacity = 0.5
                                style.strokeWidth   = 5
                                style.strokeColor   = value.color_polilinea ? value.color_polilinea : "#000000"
                                poly.style          = style
                                polyhover.push(poly);
                            });
                            recorridos.addFeatures(polyhover)
                        })
                        $(this).children().bind("mouseleave", function(e) {
                            recorridos.removeFeatures(polyhover)
                        })
                    })
                    mostrar_resultado(undefined, porNombre, forzarPanZoom)
                }
            }

            function limpiar() {
                // cuidado, este código se repite mas arriba
                markerA = new Marker(markers, "A");
                markerB = new Marker(markers, "B");
                markerA.confirmado = true;
                markerB.confirmado = true;
                recorridos.removeAllFeatures();
                markers.removeAllFeatures();
                $('#inputDesde').val('');
                $('#inputHasta').val('');
                $("#ayudaTempl").tmpl().appendTo($("#sidebarResultados").empty());
                clickHandler.activate();
            }

            // bind eventos click partes estaticas de la pagina (bind unico)

            $("#button-limpiar").bind("click", function(e) {
                e.preventDefault();
                piwikLog("/click/limpiar/");
                limpiar();
            })

            $("[data-slider]").bind("slider:release", function (event, data) {
                if (markerA.listo && markerB.listo) {
                    piwikLog("/click/buscarRadio/"+data.value);
                    buscarporclick(markerA.centro, markerB.centro, false, true);
                }
            });
            
            $("[data-slider]").bind("slider:changed", function (event, data) {
                $('#button-radio-value').html('Caminar max. ' + data.value + ' metros')
                markerA.setRadius(data.value);
                markerB.setRadius(data.value);
            });

            // buscador de lineas por sugerencia al tipear
            $('#inputLinea').attr("autocomplete","off")

            $('#inputLinea').keypress(function (e) {
                if (e.which == 13){
                    e.preventDefault();
                    piwikLog("/click/buscarNombre/enter/"+$("#inputLinea").val())
                    buscar_por_nombre()
                }
            })

            $("#button-buscarnombre").bind("click", function(e) {
                e.preventDefault();
                piwikLog("/click/buscarNombre/button/"+$("#inputLinea").val())
                buscar_por_nombre();
            })

            function buscar_por_nombre() {
                recorridos.removeAllFeatures()
                $("#ajaxLoader").tmpl().appendTo($("#sidebarResultadosPorNombre").empty())
                if ( ajaxInputLinea ) ajaxInputLinea.abort()
                pagina_nombre = 1
                inputLinea()
            }

            function inputLinea() {
                buscar = false
                ajaxInputLinea = $.ajax({
                    url: "/api/recorridos/?c="+GLOBAL_ci+"&q="+$('#inputLinea').val()+"&p="+pagina_nombre,
                    success: function(data) {mostrarResultados(data, false, true)}
                })
            }

            $("#button-ayuda").bind("click", function(e) {
                e.preventDefault()
                $("#ayudaTempl").tmpl().appendTo($("#modal-ayuda-content").empty());
                $("#modal-ayuda").modal();
                piwikLog("/click/botonera/ayuda")
            })

            function invalidarMarkers() {
                markerA.confirmado = false
                markerB.confirmado = false
            }

            $("#inputDesde").bind("change", invalidarMarkers)
            $("#inputHasta").bind("change", invalidarMarkers)

            function input_press_enter(e){
                if (e.which == 13){
                    e.preventDefault();
                    piwikLog("/click/buscar/enter/"+$("#inputDesde").val()+"/"+$("#inputHasta").val())
                    buscar_por_inputs();
                }
            }

            $("#inputDesde").keypress(input_press_enter);
            $("#inputHasta").keypress(input_press_enter);

            $("#button-buscarinputs").bind("click", function(e) {
                e.preventDefault();
                piwikLog("/click/buscar/button/"+$("#inputDesde").val()+"/"+$("#inputHasta").val())
                buscar_por_inputs();
            })

            $("#button-origendestino").bind("click", function(e) {
                e.preventDefault()
                piwikLog("/click/botonera/darVuelta")
                desde = $("#inputDesde").val()
                hasta = $("#inputHasta").val()
                if ( $.trim(desde) != '' && $.trim(hasta) != '' ) {
                    $("#inputDesde").val(hasta)
                    $("#inputHasta").val(desde)
                }
                if ( markerA.confirmado && markerB.confirmado ) {
                    ma = new OpenLayers.Geometry.Point(markerA.centro.x, markerA.centro.y)
                    mb = new OpenLayers.Geometry.Point(markerB.centro.x, markerB.centro.y)
                    markerA.setPoint(mb)
                    markerAaux.setPoint(mb)
                    markerB.setPoint(ma)
                    markerBaux.setPoint(ma)
                    // buscar sobre los markers
                    buscarporclick(markerA.centro, markerB.centro)
                }
                else {
                    // buscar sobre los textbox
                    buscar_por_inputs()
                }
            })

            // bind eventos click partes dinamicas de la pagina (bind multiple)
            function bindearEventos(porNombre) {
                var selectorDiv = '#sidebarResultadosPorNombre'
                if (!porNombre) {
                    $("#button_buscar_transbordo:not(binded)").bind("click", function(e) {
                        e.preventDefault();
                        piwikLog("/click/buscar/transbordo")
                        buscarTransbordo();
                        $(this).addClass("binded");
                    })

                    $("#button-seleccionarSugerencias:not(binded)").bind("click", function(e) {
                        e.preventDefault();
                        //trackear nombre de seleccionadas
                        piwikLog("/click/buscar/suggest/")
                        seleccionarSugerencias();
                        $(this).addClass("binded");
                    })

                    $(".marcarSuggest:not(binded)").bind("click", function(e) {
                        e.preventDefault();
                        marcarPunto(
                            $(this).attr("data_geom"),
                            $(this).attr("data_id"),
                            $(this).attr("data_domId")
                        );
                        $(this).parent().siblings().removeClass("active");
                        $(this).parent().addClass("active");
                        $(this).addClass("binded");
                    })

                    selectorDiv = '#sidebarResultados';
                }

                $(selectorDiv + " div.pagination a[href]:not(binded)").bind("click", function(e) {
                    e.preventDefault();
                    n = $(this).attr("data_pagina");
                    if      ( n <  0 ) pps = "ant";
                    else if ( n == 0 ) pps = "sig";
                    else if ( n >  0 ) pps = n;
                    piwikLog("/click/pagina/"+pps)
                    pasarPagina($(this).attr("data_pagina"), $(this).attr("combinar"), porNombre);
                    //console.log("porNombre="+porNombre)
                    //console.log("n="+n)
                    $(this).addClass("binded");
                })
            }

            if ($("#inputDesde").val() != "" && $("#inputHasta").val() != ""){
                buscar_por_inputs();
            }

            $('a[data-toggle="tab"]').on('shown', function (e) {
                if ( $(e.target).attr('href')=='#1' )
                    mostrar_resultado(undefined, false)
                else
                    mostrar_resultado(undefined, true);
            })

        })
