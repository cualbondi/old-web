document.write("<iframe src='http://{{ current_site.domain }}{% url v1_busqueda_html %}?key={{ request.GET.key }}{{ ciudad_arg }}' style='height:100px;width:200px;border:0'></iframe>");
