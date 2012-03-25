# -*- coding: UTF-8 -*-

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
import settings
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login, logout as auth_logout
from django.contrib.sites.models import get_current_site
from django.template import RequestContext
import urlparse
from django.http import HttpResponseRedirect


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
    return render_to_response(template_name, context,
                              context_instance=RequestContext(request, current_app=current_app))



def cerrar_sesion(request):
    logout(request)
    messages.add_message(request,
                    messages.INFO,
                    'Tu sesion ha sido cerrada')
    return redirect("/")
