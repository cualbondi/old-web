from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.http import HttpResponse
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.views.decorators.http import require_POST
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.contrib import comments
from django.contrib.comments import signals
from django.contrib.comments.views.utils import next_redirect, confirmation_view
from django.contrib.comments.views.comments import CommentPostBadRequest
from django.utils import simplejson
from olwidget.widgets import InfoMap
from django.http import HttpResponse, HttpResponseRedirect
import sys
from django.contrib.gis.geos import GEOSGeometry

from apps.core.models import Linea, Recorrido, Tarifa, RecorridoProposed
from apps.catastro.models import Ciudad, ImagenCiudad
from apps.core.forms import LineaForm, RecorridoForm


def natural_sort_qs(qs, key):
    """ Hace un sort sobre un queryset sobre el campo key
        utilizando una tecnica para obtener un natural_sort
        ej de algo ordenado naturalmente:             ['xx1', 'xx20', 'xx100']
        lo mismo ordenado con sort comun (asciisort): ['xx1', 'xx100', 'xx20']
    """
    import re, operator
    def natural_key(string_):
        return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]
    op = operator.attrgetter(key)
    return sorted(qs, key=lambda a:natural_key(op(a)) )

def index(request):
    """ TODO: Aca hay que checkear si tiene seteada una
        cookie con la ciudad predeterminada.
        Si no la tiene redirect a "seleccionar_ciudad"
    """
    id_ciudad = request.COOKIES.get('default_city', None)
    if id_ciudad:
        ciudad = get_object_or_404(Ciudad, id=id_ciudad)
        return redirect('/{0}/'.format(ciudad.slug))

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
    else:
        return HttpResponse(status=501)
        

def ver_ciudad(request, nombre_ciudad):
    if request.method == 'GET':
        slug_ciudad = slugify(nombre_ciudad)
        ciudad_actual = get_object_or_404(Ciudad, slug=slug_ciudad, activa=True)

        lineas = natural_sort_qs(ciudad_actual.lineas.all(), 'slug')
        tarifas = Tarifa.objects.filter(ciudad=ciudad_actual)

        mapa = InfoMap([
            [ciudad_actual.poligono, {
                'html': "<p>Special style for this point.</p>",
                'style': {'fill_color': '#0099CC', 'strokeColor': "#0066CC"},
            }]],
            {
                "map_div_style": {"width": '100%'},
                "layers": ["google.streets", "osm.mapnik"]  # "google.streets", "google.hybrid", "ve.road", "ve.hybrid", "yahoo.map"]
            }
        )

        imagenes = ImagenCiudad.objects.filter(ciudad=ciudad_actual)

        return render_to_response('core/ver_ciudad.html',
                                  {'mapa': mapa,
                                   'imagenes': imagenes,
                                   'lineas': lineas,
                                   'tarifas': tarifas},
                                  context_instance=RequestContext(request))
    else:
        return HttpResponse(status=501)


def ver_mapa_ciudad(request, nombre_ciudad):
    if request.method == 'GET':
        desde = request.GET.get("desde")
        hasta = request.GET.get("hasta")
        slug_ciudad = slugify(nombre_ciudad)
        ciudad_actual = get_object_or_404(Ciudad, slug=slug_ciudad, activa=True)
        #        "default_lat":ciudad_actual.centro.coords[1],
        #        "default_lon":ciudad_actual.centro.coords[0],
    #    pois = Poi.objects.filter(ciudad=ciudad_actual)
    #    comercios = Comercio.objects.filter(ciudad=ciudad_actual)

        return render_to_response('core/buscador.html', {
                                        'es_vista_mapa': True,
                                        'ciudad_actual': ciudad_actual,
                                        'desde': desde,
                                        'hasta': hasta,
                                  },
                                  context_instance=RequestContext(request))
    else:
        return HttpResponse(status=501)

def ver_linea(request, nombre_ciudad, nombre_linea):
    if request.method == 'GET':
        slug_ciudad = slugify(nombre_ciudad)
        slug_linea = slugify(nombre_linea)

        ciudad_actual = get_object_or_404(Ciudad, slug=slug_ciudad, activa=True)
        """ TODO: Buscar solo lineas activas """
        linea_actual = get_object_or_404(Linea,
                                         slug=slug_linea,
                                         ciudad=ciudad_actual)
        recorridos = natural_sort_qs(Recorrido.objects.filter(linea=linea_actual), 'slug')

        return render_to_response('core/ver_linea.html',
                                  {'ciudad_actual': ciudad_actual,
                                   'linea_actual': linea_actual,
                                   'recorridos': recorridos
                                   },
                                  context_instance=RequestContext(request))
    else:
        return HttpResponse(status=501)

def ver_recorrido(request, nombre_ciudad, nombre_linea, nombre_recorrido):
    if request.method == 'GET':
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
    else:
        return HttpResponse(status=501)


def redirect_nuevas_urls(request, ciudad=None, linea=None, ramal=None, recorrido=None):
    if request.method == 'GET':
        """
        cualbondi.com.ar/la-plata/recorridos/Norte/10/IDA/ (ANTES)
        cualbondi.com.ar/la-plata/norte/10-desde-x-hasta-y (DESPUES)
        cualbondi.com.ar/cordoba/recorridos/T%20(Transversal)/Central/IDA/
        """
        url = '/'
        if not ciudad:
            ciudad = 'la-plata'
        url += slugify(ciudad) + '/'
        if linea:
            url += slugify(linea) + '/'
            if ramal and recorrido:
                try:
                    recorrido = Recorrido.objects.get(linea__nombre=linea, nombre=ramal, sentido=recorrido)
                    url += slugify(recorrido.nombre) + '-desde-' + slugify(recorrido.inicio) + '-hasta-' + slugify(recorrido.fin)
                except ObjectDoesNotExist:
                    pass
        return redirect(url)
    else:
        return HttpResponse(status=501)

@ensure_csrf_cookie
@csrf_protect
def editor_recorrido(request, id_recorrido):
    if request.method == 'GET':
        recorrido = get_object_or_404(Recorrido, pk=id_recorrido)
        return render_to_response(
            'core/editor_recorrido.html',
            {'recorrido': recorrido},
            context_instance=RequestContext(request)
        )
    elif request.method == 'POST':
        # save anyway! all info is useful
        if request.POST.get("mode") == 'save':
            mode = "save"
        else:
            mode = "draft"
        # request.POST.get("id")
        recorrido = get_object_or_404(Recorrido, pk=id_recorrido)
        # sys.stderr.write(str(GEOSGeometry(request.POST.get("geojson"))))
        if ( request.POST.get("uuid") ):
            r = RecorridoProposed.objects.get(uuid=request.POST.get("uuid"))
        else:
            r = RecorridoProposed()
        r.recorrido = recorrido
        r.nombre = recorrido.nombre
        r.linea = recorrido.linea
        r.sentido         = recorrido.sentido
        r.inicio          = recorrido.inicio
        r.fin             = recorrido.fin
        r.semirrapido     = recorrido.semirrapido
        r.color_polilinea = recorrido.color_polilinea
        r.pois            = recorrido.pois
        r.descripcion     = recorrido.descripcion
        r.ruta = GEOSGeometry(request.POST.get("geojson"))
        r.user = request.user if request.user.is_authenticated() else None
        r.parent = recorrido.uuid
        # save anyway, but respond as forbidden if not auth ;)
        r.save()
        data = '{"uuid":"'+r.uuid+'"}'
        if request.user.is_authenticated():
            return HttpResponse(data)
        else:
            return HttpResponse(data, status=403)
    else:
        return HttpResponse(status=501)

@login_required(login_url="/usuarios/login/")
@permission_required('core.moderate_recorridos')
def mostrar_ediciones(request):
    # chequear capability moderar_ediciones
    # por get, sin id: mostrar ultimos recorridos en la tabla de ediciones
    # por get con uuid: mostrar ese recorrido con diff con el parent o con el que esta publicado (recorrido_id)
    # por post con uuid: aceptar ese recorrido: mover de la tabla ediciones a la tabla posta con el recorrido_id
    if request.method == 'GET':
        ediciones = RecorridoProposed.objects.order_by('-date_update')[:50]
        return render_to_response(
            'core/moderacion_listado.html',
            {'ediciones': ediciones},
            context_instance=RequestContext(request)
        )
    else:
        return HttpResponse(status=501)

@login_required(login_url="/usuarios/login/")
@permission_required('core.moderate_recorridos')
def moderar_ediciones_id(request, id=None):
    # chequear capability moderar_ediciones
    # por get, sin id: mostrar ultimos recorridos en la tabla de ediciones
    # por get con uuid: mostrar ese recorrido con diff con el parent o con el que esta publicado (recorrido_id)
    # por post con uuid: aceptar ese recorrido: mover de la tabla ediciones a la tabla posta con el recorrido_id
    if request.method == 'GET':
        ediciones = RecorridoProposed.objects.filter(recorrido__id=id).order_by('-date_update')[:50]
        original = Recorrido.objects.get(id=id)
        return render_to_response(
            'core/moderacion_id.html',
            {
                'ediciones': ediciones,
                'original': original
            },
            context_instance=RequestContext(request)
        )
    else:
        return HttpResponse(status=501)

@login_required(login_url="/usuarios/login/")
@permission_required('core.moderate_recorridos')
def moderar_ediciones_uuid(request, uuid=None):
    # chequear capability moderar_ediciones
    # por get, sin id: mostrar ultimos recorridos en la tabla de ediciones
    # por get con uuid: mostrar ese recorrido con diff con el parent o con el que esta publicado (recorrido_id)
    # por post con uuid: aceptar ese recorrido: mover de la tabla ediciones a la tabla posta con el recorrido_id
    if request.method == 'GET':
        ediciones = RecorridoProposed.objects.filter(uuid=uuid).order_by('-date_update')[:50]
        original = Recorrido.objects.get(id=ediciones[0].recorrido.id)
        return render_to_response(
            'core/moderacion_id.html',
            {
                'ediciones': ediciones,
                'original': original
            },
            context_instance=RequestContext(request)
        )
    else:
        return HttpResponse(status=501)

@login_required(login_url="/usuarios/login/")
@permission_required('core.moderate_recorridos')
def moderar_ediciones_uuid_rechazar(request, uuid=None):
    RecorridoProposed.objects.get(uuid=uuid).logmoderacion_set.create(newStatus='N')
    #redirect('moderar_ediciones_uuid', uuid=uuid)
    return HttpResponseRedirect(request.GET.get("next"))
    
@login_required(login_url="/usuarios/login/")
@permission_required('core.moderate_recorridos')
def moderar_ediciones_uuid_aprobar(request, uuid=None):
    proposed=RecorridoProposed.objects.get(uuid=uuid)
    r = proposed.recorrido
    if not r.uuid:
        rp = RecorridoProposed(
            recorrido       = r,
            nombre          = r.nombre,
            linea           = r.linea,
            ruta            = r.ruta,
            sentido         = r.sentido,
            slug            = r.slug,
            inicio          = r.inicio,
            fin             = r.fin,
            semirrapido     = r.semirrapido,
            color_polilinea = r.color_polilinea,
            pois            = r.pois,
            descripcion     = r.descripcion
        )
        rp.save()
        proposed.parent=rp.uuid
        proposed.save()
    
    r.recorrido       = proposed.recorrido
    r.nombre          = proposed.nombre
    r.linea           = proposed.linea
    r.ruta            = proposed.ruta
    r.sentido         = proposed.sentido
    r.inicio          = proposed.inicio
    r.fin             = proposed.fin
    r.semirrapido     = proposed.semirrapido
    r.color_polilinea = proposed.color_polilinea
    r.pois            = proposed.pois
    r.descripcion     = proposed.descripcion
    r.save()
    
    try:
        parent = RecorridoProposed.objects.get(uuid=proposed.parent)
        if parent:
            parent.logmoderacion_set.create(newStatus='R')
    except ObjectDoesNotExist:
        pass
    for rp in RecorridoProposed.objects.filter(current_status='S', recorrido=r.recorrido).exclude(uuid=uuid):
        rp.logmoderacion_set.create(newStatus='R')
    proposed.logmoderacion_set.create(newStatus='S')
    return HttpResponseRedirect(request.GET.get("next"))
 

#### HASTA ACA EDITOR FEEDBACKER ####

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
                    "comment": form.data.get("comment", ""),
                    "form": form,
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
        sender=comment.__class__,
        comment=comment,
        request=request
    )

    for (receiver, response) in responses:
        if response == False:
            return CommentPostBadRequest(
                "comment_will_be_posted receiver %r killed the comment" % receiver.__name__)

    # Save the comment and signal that it was saved
    comment.save()
    signals.comment_was_posted.send(
        sender=comment.__class__,
        comment=comment,
        request=request
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
    template="comments/posted.html",
    doc="""Display a "comment was posted" success page."""
)
