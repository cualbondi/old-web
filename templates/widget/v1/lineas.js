document.write("<iframe src='http://{{ current_site.domain }}{% url "v1_lineas_html" %}?key={{ request.GET.key }}&lat={{ request.GET.lat }}&lon={{ request.GET.lon }}&rad={{ request.GET.rad }}&ramales={{ request.GET.ramales }}' style='height:100px;width:200px;border:0'></iframe>");