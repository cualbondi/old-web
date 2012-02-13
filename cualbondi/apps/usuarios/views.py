# -*- coding: UTF-8 -*-

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.contrib import messages


def iniciar_sesion(request):
    url_referer = request.META.get('HTTP_REFERER', None)
    username = request.POST.get('username', None)
    password = request.POST.get('password', None)
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            msg = '{0}, has iniciado sesion correctamente en CualBondi!'
            messages.add_message(request,
                            messages.SUCCESS,
                            msg.format(user.username.capitalize()))
        else:
            msg = 'La cuenta ingresada se encuentra actualmente deshabilitada!'
            messages.add_message(request,
                            messages.ERROR,
                            msg)
    else:
        msg = 'El usuario o contraseña ingresado es incorrecto!'
        messages.add_message(request,
                        messages.ERROR,
                        msg)
    if url_referer:
        return redirect(url_referer)
    else:
        return redirect("/")


def cerrar_sesion(request):
    logout(request)
    messages.add_message(request,
                    messages.SUCCESS,
                    'Tu sesion ha sido cerrada correctamente!')
    return redirect("/")
