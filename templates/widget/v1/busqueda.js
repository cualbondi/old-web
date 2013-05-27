document.write("<iframe name='cb_{{ ciudad_arg }}' src='http://{{ current_site.domain }}{% url 'v1_busqueda_html' %}?key={{ request.GET.key }}{{ ciudad_arg }}' height='400' width='300' />");
