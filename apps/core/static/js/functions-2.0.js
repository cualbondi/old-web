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
                STATIC_URL+"css/markers/markerA.png"      ,
                STATIC_URL+"css/markers/markerA-hover.png",
                STATIC_URL+"css/markers/markerA-drag.png" ,
                STATIC_URL+"css/markers/markerB.png"      ,
                STATIC_URL+"css/markers/markerB-hover.png",
                STATIC_URL+"css/markers/markerB-drag.png"
            ]);

            map = new L.Map('mapa');

            var osmUrl='//{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
            var osmAttrib='Map data © Cualbondi & OpenStreetMap contributors';
            var osm = new L.TileLayer(osmUrl, {minZoom: 8, maxZoom: 16, attribution: osmAttrib});		
            map.setView(L.latLng(ciudad_actual_coord2, ciudad_actual_coord1), ciudad_actual_zoom);
            map.addLayer(osm);
            
            // creacion de las diferentes capas
            var paradas = L.featureGroup();
            var markers = L.featureGroup();
            var recorridos = L.featureGroup();
            var hoverLayer = L.featureGroup();
            map.addLayer(paradas);
            map.addLayer(recorridos);
            map.addLayer(markers);
            map.addLayer(hoverLayer);

            // clase Marker (para manejar el markerA y marerB mas facil)
            function Marker(layer, id, options) {
                this.visible = true
                this.draggable = true
                this.popup = false
                if ( typeof options !== "undefined" ) {
                    if ( typeof options.visible   !== 'undefined' ) this.visible   = options.visible
                    if ( typeof options.draggable !== 'undefined' ) this.draggable = options.draggable
                    if ( typeof options.popup     !== 'undefined' ) this.popup     = options.popup
                }
                this.listo  = false
                this.point  = null
                this.id     = id
                this.centro = null
                this.confirmado = false
                this.rad=200;
                this.layer  = layer
                this.group  = null
            }
            Marker.prototype.setPoint = function(point) {
                // setea el punto con latlng y lo pone en el mapa
                if (this.group)
                    this.layer.removeLayer(this.group)

                this.centro = point;

                this.group = L.editableCircleMarker(this.centro, this.rad, {draggable: this.draggable, className: this.id, popup: this.popup})
                
                self = this
                this.group.on('moveend', function(latlng) {
                    if ( self.id == markerA.id ) {
                        markerA.confirmado = true
                        markerAaux.setPoint(markerA.getLatlng())
                        markerBaux.setPoint(markerB.getLatlng())
                        piwikLog("/click/mapa/drag/A")
                    }
                    if ( self.id == markerB.id ) {
                        markerB.confirmado = true
                        markerAaux.setPoint(markerA.getLatlng())
                        markerBaux.setPoint(markerB.getLatlng())
                        piwikLog("/click/mapa/drag/B")
                    }
                    if (markerA !== null && markerB !== null) {
                        $('a[data-toggle="tab"]').first().tab('show')
                        pagina_input = 1
                        buscarporclick(markerA.getLatlng(), markerB.getLatlng())
                    }
                })
                
                if (this.visible) {
                    this.layer.addLayer(this.group)
                    this.listo = true
                }
                
            }
            Marker.prototype.setRadius = function(rad) {
                this.rad = rad
                if (this.group) {
                    this.group.setRadius(rad)
                }
            }
            Marker.prototype.getLatlng = function(rad) {
                return this.group.getLatLng()
            }

            // dos objetos de la clase marker // cuidado, este código se repite mas abajo
            var markerA = new Marker(markers, "markerA")
            var markerB = new Marker(markers, "markerB")
            var markerAaux = new Marker(markers, "markerA", { visible: false })
            var markerBaux = new Marker(markers, "markerB", { visible: false })

            // manejo de clicks en el mapa
            //      creacion de los markers A y B
            //      busqueda por click en el mapa
            map.on('click', function(e){
                if ( !markerA.listo ) {
                    markerA.setPoint(e.latlng)
                    markerAaux.setPoint(e.latlng)
                    markerA.confirmado = true
                    piwikLog("/click/mapa/marker/A")
                }
                else
                    if ( !markerB.listo ) {
                        markerB.setPoint(e.latlng)
                        markerBaux.setPoint(e.latlng)
                        markerB.confirmado = true
                        piwikLog("/click/mapa/marker/B")
                        pagina_input = 1
                        buscarporclick(markerA.getLatlng(), markerB.getLatlng())
                    }
            })

            
            // manejo del drag de los markers
            //      cambio de imagenes al draggear y onhover
            //      busqueda por ondrag
            /*

            // hover en las paradas
            var hoverControl = new OpenLayers.Control.SelectFeature([paradas, markers], {
                hover: true,
                click: false,
                highlightOnly: true,
                renderIntent: "hover"
            });
            map.addControl(hoverControl);
            hoverControl.activate()
            
            // click en las paradas
            var selectorControl = new OpenLayers.Control.SelectFeature([paradas, markers], {
                click: true,
                hover: false,
                toggle: true
            });
            map.addControl(selectorControl);
            selectorControl.activate()
            */

            // variables "globales"
            var resultados = new Object()
            resultados[true] = new Object()
            resultados[false] = new Object()
            var polylinea  = new Array()
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
                recorridos.clearLayers();
                paradas.clearLayers();
                map.closePopup();

                var polylinea = new Array()
                var trasbordos = new Array()
                var stops = new Array()
                var cant = resultados[porNombre][id].length
                $.each(resultados[porNombre][id], function(key, value) {
                    ruta = $.RC4.decode(value.ruta_corta)
                    var wkt = new Wkt.Wkt();
                    wkt.read(ruta);
                    var poly = wkt.toObject(map.defaults);
                    if (value.p1 !== null)
                        stops.push(value.p1)
                    else
                        if (key != 0) // not first (punto A)
                            trasbordos.push(L.latLng(poly._latlngs[0]));
                    if (value.p2 !== null)
                        stops.push(value.p2)
                    else
                        if (key != cant-1) // not last (punto B)
                            trasbordos.push(L.latLng(poly._latlngs[poly._latlngs.length-1]));
                    poly.setStyle({
                        color: value.color_polilinea ? value.color_polilinea : "#000000",
                        opacity: 0.8
                    })
                    polylinea.push(poly);
                });

                $.each(polylinea, function(key, value) {
                    recorridos.addLayer(value);
                    var flechas = L.polylineDecorator(value, {
                            patterns: [
                                {offset: '50', repeat: 150, symbol: L.Symbol.arrowHead({pixelSize: 15, polygon: false, pathOptions: {color: value.options.color, opacity: 0.6, stroke: true}})}
                            ]
                        });
                    recorridos.addLayer(flechas);
                })
                
                $.each(trasbordos, function(key, value) {
                    markerT = new Marker(recorridos, "markerT", { draggable: false });
                    markerT.setRadius(0);
                    markerT.setPoint(value);
                })
                
                $.each(stops, function(key, value) {
                    if (typeof value !== 'undefined') {
                        p = new Marker(paradas, "markerP", { draggable: false, popup: "<p><strong>Parada "+value.codigo+"</strong><br>"+value.nombre+"</p>" });
                        p.setRadius(0);
                        var wkt = new Wkt.Wkt();
                        wkt.read(value.latlng);
                        p.setPoint(L.latLng(wkt.toObject(map.defaults)._latlng))
                    }
                })
                                
                if (porNombre) {
                    markerA.setPoint(L.latLng(polylinea[0]._latlngs[0]));
                    markerB.setPoint(L.latLng(polylinea[polylinea.length-1]._latlngs[polylinea[polylinea.length-1]._latlngs.length-1]));
                }
                else {
                    markerA.setPoint(markerAaux.getLatlng());
                    markerB.setPoint(markerBaux.getLatlng());
                }
                if (porNombre || forzarPanZoom) {
                    map.fitBounds(recorridos.getBounds().extend(markers.getBounds()))
                }
            }

            function buscar_por_inputs() {
                markerA = new Marker(markers, "markerA");
                markerB = new Marker(markers, "markerB");
                markerA.confirmado = true;
                markerB.confirmado = true;
                recorridos.clearLayers();
                paradas.clearLayers();
                map.closePopup()
                markers.clearLayers();
                $("[data-slider]").simpleSlider("setValue", 300);
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
                        try { piwikTracker.trackSiteSearch( $("#inputDesde").val(), "Desde", data1.length ) } catch(err) {}
                        try { piwikTracker.trackSiteSearch( $("#inputHasta").val(), "Hasta", data2.length ) } catch(err) {}
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
                var wkt = new Wkt.Wkt();
                wkt.read(pointWKT);
                var point = L.latLng(wkt.toObject(map.defaults)._latlng);
                if ( id == 1 ) {
                    markerA.setPoint(point)
                    markerAaux.setPoint(point)
                }
                else if ( id == 2 ) {
                    markerB.setPoint(point)
                    markerBaux.setPoint(point)
                }
                map.panTo(point)
                $("#sug" + domId).siblings().removeClass("active")
                $("#sug" + domId).addClass("active")
            }

            // busca una vez que se eligieron las sugerencias
            function seleccionarSugerencias() {
                markerA.confirmado = true
                markerB.confirmado = true
                if ( markerA.listo && markerB.listo ) {
                    pagina_input = 1
                    buscarporclick(markerA.getLatlng(), markerB.getLatlng(), 'false', true)
                }
            }

            // busca por transbordo
            function buscarTransbordo() {
                markerA.confirmado = true
                markerB.confirmado = true
                if ( markerA.listo && markerB.listo ) {
                    pagina_input = 1
                    buscarporclick(markerA.getLatlng(), markerB.getLatlng(), 'true')
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
                    buscarporclick(markerA.getLatlng(), markerB.getLatlng(), combinar);
                else
                    inputLinea();
            }

            // envia peticion al server para buscar por latlng
            function buscarporclick(lla, llb, combinar, forzarPanZoom) {
                if ( typeof(combinar) === 'undefined' ) combinar = 'false';
                buscar     = true
                recorridos.clearLayers();
                paradas.clearLayers();
                map.closePopup();
                $("#ajaxLoader").tmpl().appendTo($("#sidebarResultados").empty())
                $.get(
                    "/api/recorridos/",
                    {
                        origen: lla.lng+","+lla.lat,
                        destino: llb.lng+","+llb.lat,
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

                            // codigo repetido mas arriba (solo cambia la opacity)
                            //recorridos.clearLayers(polyhover)
                            trasbordos = new Array();
                            $.each(resultados[porNombre][id], function(key, value) {
                                var wkt = new Wkt.Wkt();
                                wkt.read($.RC4.decode(value.ruta_corta));
                                var poly = wkt.toObject(map.defaults);
                                trasbordos.push(poly._latlngs[0]);
                                trasbordos.push(poly._latlngs[poly._latlngs.length-1]);
                                poly.setStyle({color: value.color_polilinea ? value.color_polilinea : "#000000"})
                                hoverLayer.addLayer(poly);
                            });

                            trasbordos.pop() //eliminar ultimo elemento (punto B)
                            trasbordos.splice(0,1) //eliminar primer elemento (punto A)
                            $.each(trasbordos, function(key, value) {
                                markerT = new Marker(hoverLayer, "markerT", { draggable: false });
                                markerT.setRadius(0);
                                markerT.setPoint(value);
                            })
                        })
                        $(this).children().bind("mouseleave", function(e) {
                            hoverLayer.clearLayers()
                        })
                    })
                    mostrar_resultado(undefined, porNombre, forzarPanZoom)
                }
            }

            function limpiar() {
                // cuidado, este código se repite mas arriba
                markerA = new Marker(markers, "markerA");
                markerB = new Marker(markers, "markerB");
                markerA.confirmado = true;
                markerB.confirmado = true;
                recorridos.clearLayers();
                paradas.clearLayers();
                map.closePopup()
                markers.clearLayers();
                $("[data-slider]").simpleSlider("setValue", 300);
                $('#inputDesde').val('');
                $('#inputHasta').val('');
                $("#ayudaTempl").tmpl().appendTo($("#sidebarResultados").empty());
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
                    buscarporclick(markerA.getLatlng(), markerB.getLatlng(), false, true);
                }
            });
            
            $("[data-slider]").bind("slider:changed", function (event, data) {
                $('#button-radio-value').html('Caminar max. ' + data.value + ' metros')
                markerA.setRadius(data.value);
                markerB.setRadius(data.value);
            });
            $("[data-slider]").simpleSlider("setValue", 300);

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
                recorridos.clearLayers();
                paradas.clearLayers();
                map.closePopup();
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
                    ma = markerA.getLatlng()
                    mb = markerB.getLatlng()
                    markerA.setPoint(mb)
                    markerAaux.setPoint(mb)
                    markerB.setPoint(ma)
                    markerBaux.setPoint(ma)
                    // buscar sobre los markers
                    buscarporclick(markerA.getLatlng(), markerB.getLatlng())
                }
                else {
                    // buscar sobre los textbox
                    buscar_por_inputs()
                }
            })

            // bind eventos click partes dinamicas de la pagina (bind multiple)
            function bindearEventos(porNombre) {
                
                $('span[href]').not('.binded').bind('click', function(e) {
                    e.preventDefault();
                    piwikLog("/click/verMasInfo/"+$(this).parent().parent().attr('id'))
                    window.open($(this).attr('href'));
                }).addClass("binded");
                
                var selectorDiv = '#sidebarResultadosPorNombre'
                if (!porNombre) {
                    $("#button_buscar_transbordo").not('.binded').bind("click", function(e) {
                        e.preventDefault();
                        piwikLog("/click/buscar/transbordo")
                        buscarTransbordo();
                    }).addClass("binded")

                    $("#button-seleccionarSugerencias").not('.binded').bind("click", function(e) {
                        e.preventDefault();
                        //trackear nombre de seleccionadas
                        piwikLog("/click/buscar/suggest/")
                        seleccionarSugerencias();
                    }).addClass("binded")

                    $(".marcarSuggest").not('.binded').bind("click", function(e) {
                        e.preventDefault();
                        marcarPunto(
                            $(this).attr("data_geom"),
                            $(this).attr("data_id"),
                            $(this).attr("data_domId")
                        );
                        $(this).parent().siblings().removeClass("active");
                        $(this).parent().addClass("active");
                    }).addClass("binded");

                    selectorDiv = '#sidebarResultados';
                }

                $(selectorDiv + " div.pagination a[href]").not('.binded').bind("click", function(e) {
                    e.preventDefault();
                    n = $(this).attr("data_pagina");
                    if      ( n <  0 ) pps = "ant";
                    else if ( n == 0 ) pps = "sig";
                    else if ( n >  0 ) pps = n;
                    piwikLog("/click/pagina/"+pps)
                    pasarPagina($(this).attr("data_pagina"), $(this).attr("combinar"), porNombre);
                    //console.log("porNombre="+porNombre)
                    //console.log("n="+n)
                }).addClass("binded");
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
