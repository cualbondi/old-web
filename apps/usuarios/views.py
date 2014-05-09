# -*- coding: UTF-8 -*-
import urlparse
import settings
from random import random
from datetime import datetime, timedelta
from django.contrib.auth import logout
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login
from django.contrib.sites.models import get_current_site
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.utils.hashcompat import sha_constructor
from django.contrib.auth.decorators import login_required

from apps.usuarios.models import PerfilUsuario
from apps.usuarios.forms import RegistracionForm
from apps.usuarios.forms import PerfilUsuarioForm

from social.apps.django_app.utils import strategy
from django.contrib.auth.models import User
from django.contrib.auth import login

from apps.editor.models import RecorridoProposed

@strategy('social:complete')
def ajax_auth(request, backend):
    access_token = request.POST.get('access_token', False)
    if access_token:
        request.social_strategy.clean_partial_pipeline()
        ret = request.social_strategy.backend.do_auth(access_token)
        user = User.objects.get(username=ret)
        if user:
            if user.is_active:
                user.backend = 'social.backends.facebook.FacebookOAuth2'
                login(request, user)
                return HttpResponse(status=200)
            else:
                return HttpResponse("Disabled Account", status=403)
        else:
            return HttpResponse("Invalid Login", status=403)
    else:
        return HttpResponse("No token found", status=403)
    

@csrf_protect
@never_cache
def iniciar_sesion(request, template_name='registration/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm,
          current_app=None, extra_context=None):
    """
    Displays the login form and handles the login action.
    """
    redirect_to = request.REQUEST.get(redirect_field_name, '')

    if request.method == "POST":
        form = authentication_form(data=request.POST)
        if form.is_valid():
            netloc = urlparse.urlparse(redirect_to)[1]

            # Use default setting if redirect_to is empty
            if not redirect_to:
                redirect_to = settings.LOGIN_REDIRECT_URL

            # Security check -- don't allow redirection to a different
            # host.
            elif netloc and netloc != request.get_host():
                redirect_to = settings.LOGIN_REDIRECT_URL

            # Okay, security checks complete. Log the user in.
            auth_login(request, form.get_user())

            messages.add_message(request,
                            messages.SUCCESS,
                            'Has iniciado sesion correctamente')

            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()

            if request.is_ajax():
                return HttpResponse()
            else:
                return HttpResponseRedirect(redirect_to)

    elif request.method == 'GET':
        if request.user.is_authenticated():
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
        form = authentication_form(request)

    url_referer = request.META.get('HTTP_REFERER', settings.LOGIN_REDIRECT_URL)

    request.session.set_test_cookie()

    current_site = get_current_site(request)

    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
        'referer': url_referer
    }
    context.update(extra_context or {})
    if request.is_ajax():
        return HttpResponseForbidden()
    else:
        return render_to_response(template_name, context,
                              context_instance=RequestContext(request, current_app=current_app))


def cerrar_sesion(request):
    logout(request)
    messages.add_message(request,
                    messages.INFO,
                    'Tu sesion ha sido cerrada')
    return redirect("/")


def _generar_link_activacion(request, email):
    semilla = sha_constructor(str(random())).hexdigest()[:5]
    confirmacion_key = sha_constructor(semilla + email).hexdigest()
    dominio = request.META.get('HTTP_HOST', 'www.cualbondi.com.ar')
    path = 'usuarios/confirmar-email'
    url_activacion = u'http://{0}/{1}/{2}/'.format(dominio, path, confirmacion_key)
    return confirmacion_key, url_activacion


def _enviar_mail_activacion(email, url_activacion):
    subject = "CualBondi: Confirmación de Email"
    message = "Click <a href='"+url_activacion+"'>aqui</a> para confirmar tu email."
    print url_activacion
#            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])


def registrar_usuario(request, **kwargs):
    if request.method == "POST":
        form = RegistracionForm(request.POST)
        if form.is_valid():
            #Crear usuario y asignarle atributos
            usuario = User()
            usuario.is_active = False
            usuario.username = form.cleaned_data.get("username")
            usuario.email = form.cleaned_data["email"].strip().lower()
            password = form.cleaned_data.get("password1")
            usuario.set_password(password)
            usuario.save()

            # Generar link de activacion
            key, url_activacion = _generar_link_activacion(request, usuario.email)

            # Guardar la "confirmacion_key" en el perfil del usuario
            perfil = PerfilUsuario(usuario=usuario)
            perfil.confirmacion_key = key
            perfil.save()

            # Enviar email de activacion
            _enviar_mail_activacion(usuario.email, url_activacion)

            messages.add_message(request,
                            messages.INFO,
                            'Te hemos enviado un Email de confirmacion.')
            messages.add_message(request,
                            messages.INFO,
                            url_activacion)
            return redirect("/")
    else:
        if request.user.is_authenticated():
            messages.add_message(request,
                            messages.WARNING,
                            'Ya tenes una cuenta, no te hagas el vivo...')
            return redirect('/')
        form = RegistracionForm()

    return render_to_response("usuarios/registracion.html", RequestContext(request, {'form': form}))


def confirmar_email(request, confirmacion_key=None):
    if not request.user.is_authenticated():
        try:
            perfil = PerfilUsuario.objects.get(confirmacion_key=confirmacion_key)
            usuario = perfil.usuario
            fecha_envio = perfil.fecha_envio_confirmacion
            now = datetime.now()
            td = timedelta(weeks=1)
            if now > (fecha_envio + td):
                # Clave de verificacion vencida, enviar una nueva
                key, url_activacion = _generar_link_activacion(request, usuario.email)

                # Guardar la nueva clave en el perfil
                perfil.confirmacion_key = key
                perfil.fecha_envio_confirmacion = now
                perfil.save()

                # Enviar nuevo mail de activacion
                _enviar_mail_activacion(usuario.email, url_activacion)
                messages.add_message(request,
                                messages.WARNING,
                                'El código de verificación ha caducado, te hemos enviado uno nuevo...')
                messages.add_message(request,
                                messages.INFO,
                                url_activacion)
            elif usuario.is_active:
                messages.add_message(request,
                                messages.WARNING,
                                'Tu cuenta ya esta verificada, solo tenés que iniciar sesion.')
                return redirect('/usuarios/login/')
            else:
                # Verificacion correcta
                perfil.fecha_verificacion = now
                perfil.save()
                usuario.is_active = True
                usuario.save()

                messages.add_message(request,
                                messages.SUCCESS,
                                'Tu cuenta ha sido verificada correctamente, ahora solo tenés que iniciar sesion.')
                return redirect('/usuarios/login/')
        except ObjectDoesNotExist:
            messages.add_message(request,
                            messages.ERROR,
                            'El código de verificacion ingresado es incorrecto.')
    return redirect('/')


def ver_perfil(request, username):
    usuario = get_object_or_404(User, username=username)
    #perfil = PerfilUsuario.objects.get(usuario=usuario)
    ediciones = []
    for r in RecorridoProposed.objects.order_by('-date_update'):
        if r.get_moderacion_last_user() == usuario:
            ediciones.append(r)
    #ediciones = [ r if r.get_moderacion_last_user() == usuario for r in RecorridoProposed.objects.order_by('-date_update') ]
    return render_to_response(
        'usuarios/perfil.html',
        {
            'usuario': usuario,
            'ediciones': ediciones,
        },
        context_instance=RequestContext(request)
    )


@login_required(login_url="/usuarios/login/")
def editar_perfil(request):
    perfil = PerfilUsuario.objects.get(usuario=request.user)
    if request.method == 'POST':
        form = PerfilUsuarioForm(request.POST, instance=perfil)
        if form.is_valid():
            perfil = form.save(commit=False)
            perfil.usuario = request.user
            perfil.save()
            messages.add_message(request,
                            messages.SUCCESS,
                            'Tu perfil ha sido editado correctamente.')
            return redirect('/usuarios/perfil/')
        else:
            return render_to_response('usuarios/editar_perfil.html',
                                        {'form': form},
                                        context_instance=RequestContext(request))
    else:
        form = PerfilUsuarioForm(instance=perfil)
        return render_to_response('usuarios/editar_perfil.html',
                                    {'form': form},
                                    context_instance=RequestContext(request))
