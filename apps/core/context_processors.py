from apps.catastro.models import Ciudad


def lista_ciudades(request):
    ciudades = Ciudad.objects.filter(activa=True).order_by('nombre')
    return {'ciudades': ciudades}


def get_ciudad_actual(request):
    try:
        path_info = request.path_info
        slug_ciudad = path_info.split('/')[1]
        ciudad_actual = Ciudad.objects.get(slug=slug_ciudad)
    except Exception:
        ciudad_actual = None
    return {'ciudad_actual': ciudad_actual}

def show_android_alert(request):
    cookie = request.COOKIES.get('android_app_alert_closed')
    if cookie is None:
        show_alert = True
    else:
        show_alert = False
    return {'show_android_alert': show_alert}
