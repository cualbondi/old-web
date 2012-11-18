from apps.catastro.models import Ciudad


def lista_ciudades(request):
    ciudades = Ciudad.objects.filter(activa=True)
    return {'ciudades': ciudades}


def get_ciudad_actual(request):
    try:
        path_info = request.path_info
        slug_ciudad = path_info.split('/')[1]
        ciudad_actual = Ciudad.objects.get(slug=slug_ciudad)
    except Exception:
        ciudad_actual = None
    return {'ciudad_actual': ciudad_actual}
