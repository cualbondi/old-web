$(document).on("mobileinit", function(){
    $.allowCrossDomainPages = true;
});
$(document).ready(function(){
    var CIUDAD = null;

    $('#lista-ciudades a').on('click', function(e){
        e.preventDefault();
        CIUDAD = $(this).attr('data-name');
        $.mobile.changePage("#opciones");
    });

    $("#boton_buscar").click(function(event){
        event.preventDefault();

        var origen = $("#origen").val();
        var destino = $("#destino").val();
        var slider = $("#slider").val();

        if (origen !== '' && destino !== ''){
            var base_url = "http://cualbondi.com.ar/api/";
            $.ajax({
                 url: base_url + "catastro/?query=" + origen + "&ciudad=" + CIUDAD,
                 dataType: 'jsonp',
                 success:function(data){
                    var suggestOrigen = $("#suggest_origen");
                    suggestOrigen.empty();
                    $("#listSuggest").tmpl({'data': data, 'punto': 'origen'}).appendTo(suggestOrigen);
                    suggestOrigen.trigger("create");
                 },
                 error:function(){
                     alert("Error");
                 }
            });
            $.ajax({
                 url: base_url + "catastro/?query=" + destino + "&ciudad=" + CIUDAD,
                 dataType: 'jsonp',
                 success:function(data){
                    var suggestDestino = $("#suggest_destino");
                    suggestDestino.empty();
                    $("#listSuggest").tmpl({'data': data, 'punto': 'destino'}).appendTo(suggestDestino);
                    suggestDestino.trigger("create");
                 },
                 error:function(){
                     alert("Error");
                 }
            });
            $.mobile.changePage("#sugerencias");
        }else{
            $("#errorSuggest").tmpl({'msg': 'Origen y Destino no deben ser vacios.'}).appendTo($("#opciones_errors").empty());
        }
    });

    $("#boton_aceptar_sugg").click(function(event){
        event.preventDefault();
        var origen = $("#controlgroup_origen input:checked");
        var destino = $("#controlgroup_destino input:checked");
        if (origen.length > 0 && destino.length > 0){
            origen = origen.val().replace("POINT(", "").replace(")","").replace(" ", ",");
            destino = destino.val().replace("POINT(", "").replace(")","").replace(" ", ",");
            var radio = $("#slider").val();

            var base_url = "http://cualbondi.com.ar/api/";
            $.ajax({
                 url: base_url + "recorridos/?origen=" + origen + "&destino=" + destino + "&radio_origen=" + radio + "&radio_destino=" + radio + "&c=" + CIUDAD + "&combinar=false",
                 dataType: 'jsonp',
                 success:function(data){
                    $("#listResultados").tmpl(data).appendTo($("#resultados_content").empty());
                    $("#resultados_content").trigger("create");
                 },
                 error:function(){
                     alert("Error");
                 }
            });

            $.mobile.changePage("#resultados");
        }else{
            $("#errorSuggest").tmpl({'msg': 'Debe seleccionar origen y destion'}).appendTo($("#suggest_errors").empty());
        }
    });
});
