from apps.core.models import Linea, Recorrido
from apps.catastro.models import Ciudad, Poi
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.http import HttpResponse
from django.template import RequestContext, Context
from django.template.defaultfilters import slugify
from apps.core.forms import LineaForm, RecorridoForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.contrib import comments
from django.contrib.comments import signals
from django.contrib.comments.views.utils import next_redirect, confirmation_view
from django.contrib.comments.views.comments import CommentPostBadRequest
from django.utils import simplejson
from olwidget.widgets import EditableMap

def index(request):
    """ TODO: Aca hay que checkear si tiene seteada una
        cookie con la ciudad predeterminada.
        Si no la tiene redirect a "seleccionar_ciudad"
    """
    id_ciudad = request.COOKIES.get('default_city', None)
    if id_ciudad:
        ciudad = get_object_or_404(Ciudad, id=id_ciudad)
        url = '/{0}/'.format(ciudad.slug)
    else:
        url = '/seleccionar-ciudad/'
    return redirect(url)

def seleccionar_ciudad(request):
    if request.method == 'GET':
        return render_to_response('core/seleccionar_ciudad.html',
                                  {'ciudad_actual': None},
                                  context_instance=RequestContext(request))
    elif request.method == 'POST':
        id_ciudad = request.POST.get('ciudad', None)
        next = request.POST.get('next', 'mapa')
        predeterminada = request.POST.get('predeterminada', False)

        ciudad = get_object_or_404(Ciudad, id=id_ciudad)
        if next == 'mapa':
            response = redirect('/mapa/{0}/'.format(ciudad.slug))
        else:
            response = redirect('/{0}/'.format(ciudad.slug))
        if predeterminada:
            response.set_cookie('default_city', ciudad.id)
        return response


def ver_ciudad(request, nombre_ciudad):
    slug_ciudad = slugify(nombre_ciudad)
    ciudad_actual = get_object_or_404(Ciudad, slug=slug_ciudad, activa=True)

    lineas = ciudad_actual.lineas.all()

    return render_to_response('core/ver_ciudad.html',
                              {'lineas': lineas},
                              context_instance=RequestContext(request))


def ver_mapa_ciudad(request, nombre_ciudad):
    slug_ciudad = slugify(nombre_ciudad)
    ciudad_actual = get_object_or_404(Ciudad, slug=slug_ciudad, activa=True)
    mapa = EditableMap(
        options={ 
            "map_div_style": {"width": '100%', "height": '100%'},
            "layers":["osm.mapnik"],# "google.streets", "google.hybrid"],#, "ve.road", "ve.hybrid", "yahoo.map"]
            "default_lat":ciudad_actual.centro.coords[1],
            "default_lon":ciudad_actual.centro.coords[0],
            "default_zoom":ciudad_actual.zoom,            
            "editable":False
        }
    )
#    pois = Poi.objects.filter(ciudad=ciudad_actual)
#    comercios = Comercio.objects.filter(ciudad=ciudad_actual)

    return render_to_response('core/ver_mapa_ciudad.html',
                              {'es_vista_mapa': True,
                               'ciudad_actual': ciudad_actual,
                               'mapa':mapa},
                              context_instance=RequestContext(request))


def ver_linea(request, nombre_ciudad, nombre_linea):
    slug_ciudad = slugify(nombre_ciudad)
    slug_linea = slugify(nombre_linea)

    ciudad_actual = get_object_or_404(Ciudad, slug=slug_ciudad, activa=True)
    """ TODO: Buscar solo lineas activas """
    linea_actual = get_object_or_404(Linea,
                                     slug=slug_linea,
                                     ciudad=ciudad_actual)
    recorridos = Recorrido.objects.filter(linea=linea_actual)
    return render_to_response('core/ver_linea.html',
                              {'ciudad_actual': ciudad_actual,
                               'linea_actual': linea_actual,
                               'recorridos': recorridos},
                              context_instance=RequestContext(request))


def ver_recorrido(request, nombre_ciudad, nombre_linea, nombre_recorrido):
    slug_ciudad = slugify(nombre_ciudad)
    slug_linea = slugify(nombre_linea)
    slug_recorrido = slugify(nombre_recorrido)

    ciudad_actual = get_object_or_404(Ciudad, slug=slug_ciudad, activa=True)
    """ TODO: Buscar solo lineas activas """
    linea_actual = get_object_or_404(Linea,
                                     slug=slug_linea,
                                     ciudad=ciudad_actual)
    """ TODO: Buscar solo recorridos activos """
    recorrido_actual = get_object_or_404(Recorrido,
                                         slug=slug_recorrido,
                                         linea=linea_actual)

    favorito = False
    if request.user.is_authenticated():
        favorito = recorrido_actual.es_favorito(request.user)

    return render_to_response('core/ver_recorrido.html',
                              {'ciudad_actual': ciudad_actual,
                               'linea_actual': linea_actual,
                               'recorrido_actual': recorrido_actual,
                               'favorito': favorito},
                              context_instance=RequestContext(request))


@login_required(login_url="/usuarios/login/")
def agregar_linea(request):
    if request.method == 'POST':
        form = LineaForm(request.POST)
        if form.is_valid():
            linea = form.save(commit=True)
            msg = 'La linea {0} se ha agregado correctamente'
            messages.add_message(request,
                            messages.SUCCESS,
                            msg.format(linea))
        else:
            msg = 'La operacion no pudo realizarse con exito'
            messages.add_message(request,
                            messages.ERROR,
                            msg)
        return render_to_response('core/agregar_linea.html',
                                 {'form': form},
                              context_instance=RequestContext(request))
    elif request.method == 'GET':
        linea_form = LineaForm()
        return render_to_response('core/agregar_linea.html',
                                  {'form': linea_form},
                                  context_instance=RequestContext(request))


@login_required(login_url="/usuarios/login/")
def agregar_recorrido(request):
    if request.method == 'POST':
        pass
    elif request.method == 'GET':
        recorrido_form = RecorridoForm()
        return render_to_response('core/agregar_recorrido.html',
                                  {'form': recorrido_form},
                                    context_instance=RequestContext(request))


@csrf_protect
@require_POST
def dejar_comentario(request, next=None, using=None):
    # Fill out some initial data fields from an authenticated user, if present
    data = request.POST.copy()
    if request.user.is_authenticated():
        if not data.get('name', ''):
            data["name"] = request.user.get_full_name() or request.user.username
        if not data.get('email', ''):
            data["email"] = request.user.email

    # Check to see if the POST data overrides the view's next argument.
    next = data.get("next", next)

    # Look up the object we're trying to comment about
    ctype = data.get("content_type")
    object_pk = data.get("object_pk")
    if ctype is None or object_pk is None:
        return CommentPostBadRequest("Missing content_type or object_pk field.")
    try:
        model = models.get_model(*ctype.split(".", 1))
        target = model._default_manager.using(using).get(pk=object_pk)
    except TypeError:
        return CommentPostBadRequest(
            "Invalid content_type value: %r" % escape(ctype))
    except AttributeError:
        return CommentPostBadRequest(
            "The given content-type %r does not resolve to a valid model." % \
                escape(ctype))
    except ObjectDoesNotExist:
        return CommentPostBadRequest(
            "No object matching content-type %r and object PK %r exists." % \
                (escape(ctype), escape(object_pk)))
    except (ValueError, ValidationError), e:
        return CommentPostBadRequest(
            "Attempting go get content-type %r and object PK %r exists raised %s" % \
                (escape(ctype), escape(object_pk), e.__class__.__name__))

    # Construct the comment form
    form = comments.get_form()(target, data=data)

    # Check security information
    if form.security_errors():
        return CommentPostBadRequest(
            "The comment form failed security verification: %s" % \
                escape(str(form.security_errors())))

    # If there are errors show the comment or return errors in JSON
    if form.errors:
        if request.is_ajax():
            response = simplejson.dumps({'exito': False})
            return HttpResponse(response, mimetype='application/javascript')
        else:
            template_list = [
                # These first two exist for purely historical reasons.
                # Django v1.0 and v1.1 allowed the underscore format for
                # preview templates, so we have to preserve that format.
                "comments/%s_%s_preview.html" % (model._meta.app_label, model._meta.module_name),
                "comments/%s_preview.html" % model._meta.app_label,
                # Now the usual directory based template heirarchy.
                "comments/%s/%s/preview.html" % (model._meta.app_label, model._meta.module_name),
                "comments/%s/preview.html" % model._meta.app_label,
                "comments/preview.html",
            ]
            return render_to_response(
                template_list, {
                    "comment" : form.data.get("comment", ""),
                    "form" : form,
                    "next": next,
                },
                RequestContext(request, {})
            )

    # Otherwise create the comment
    comment = form.get_comment_object()
    comment.ip_address = request.META.get("REMOTE_ADDR", None)
    if request.user.is_authenticated():
        comment.user = request.user

    # Signal that the comment is about to be saved
    responses = signals.comment_will_be_posted.send(
        sender  = comment.__class__,
        comment = comment,
        request = request
    )

    for (receiver, response) in responses:
        if response == False:
            return CommentPostBadRequest(
                "comment_will_be_posted receiver %r killed the comment" % receiver.__name__)

    # Save the comment and signal that it was saved
    comment.save()
    signals.comment_was_posted.send(
        sender  = comment.__class__,
        comment = comment,
        request = request
    )

    if request.is_ajax():
        cleaned_data = form.cleaned_data
        json = {'exito': True, 
                'comentario': cleaned_data['comment'],
                'usuario': cleaned_data['name'],
                'fecha': cleaned_data['timestamp']}
        response = simplejson.dumps(json)
        return HttpResponse(response, mimetype='application/javascript')
    else:
        return next_redirect(data, next, comment_done, c=comment._get_pk_val())

comment_done = confirmation_view(
    template = "comments/posted.html",
    doc = """Display a "comment was posted" success page."""
)
