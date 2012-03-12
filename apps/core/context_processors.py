from apps.core.models import Ciudad


def lista_ciudades(request):
    ciudades = Ciudad.objects.filter(activa=True)
    return {'ciudades': ciudades}
