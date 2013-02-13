function dibujar_comentario(comentario, usuario, fecha){
    html = '<div class="row">'
        html += '<div class="span2" align="right">'
            html += '<h4>'+usuario+'</h4>'
            var datetime = new Date()
            html += ' ('+datetime.format('dd/mm/yyyy')+')';
        html += '</div>'
        html += '<div class="span6 well">'+comentario+'</div>'
    html += '</div>'
    $("#lista-comentarios").append(html)
}
