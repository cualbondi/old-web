# -*- coding: UTF-8 -*-
from django.conf import settings

from apps.catastro.models import Ciudad


def lista_ciudades(request):
    ciudades = Ciudad.objects.filter(activa=True).order_by('nombre')
    return {'ciudades': ciudades}


def get_ciudad_actual(request):
    try:
        path_info = request.path_info
        slug_ciudad = path_info.split('/')[1]
        if slug_ciudad == 'mapa':
            slug_ciudad = path_info.split('/')[2]
        ciudad_actual = Ciudad.objects.get(slug=slug_ciudad)
        anuncios = ciudad_actual.anuncios.all().filter(activo=True)
    except Exception:
        ciudad_actual = None
        anuncios = []
    return {
        'ciudad_actual': ciudad_actual,
        'anuncios': anuncios,
    }


def show_android_alert(request):
    cookie = request.COOKIES.get('android_app_alert_closed')
    if cookie is None:
        show_alert = True
    else:
        show_alert = False
    return {'show_android_alert': show_alert}


def home_url(request):
    return {'HOME_URL': settings.HOME_URL}


def facebook_app_id(request):
    return {'FACEBOOK_APP_ID': settings.FACEBOOK_APP_ID}
