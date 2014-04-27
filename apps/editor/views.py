from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from apps.core.models import Recorrido
from apps.editor.models import RecorridoProposed
from django.contrib.gis.geos import GEOSGeometry
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_exempt
import json


@ensure_csrf_cookie
@csrf_protect
def editor_recorrido(request, id_recorrido):
    if request.method == 'GET':
        recorrido = get_object_or_404(Recorrido, pk=id_recorrido)
        return render_to_response(
            'editor/editor_recorrido.html',
            {
                'recorrido': recorrido,
                'user': request.user
            },
            context_instance=RequestContext(request)
        )
    elif request.method == 'POST':
        # save anyway! all info is useful
        recorrido = get_object_or_404(Recorrido, pk=id_recorrido)
        user = request.user if request.user.is_authenticated() else None
        if (request.POST.get("uuid", False)):
            r = get_object_or_404(RecorridoProposed, uuid=request.POST.get("uuid"))
        else:
            r = RecorridoProposed()
        r.recorrido       = recorrido
        r.nombre          = recorrido.nombre
        r.linea           = recorrido.linea
        r.sentido         = recorrido.sentido
        r.inicio          = recorrido.inicio
        r.fin             = recorrido.fin
        r.semirrapido     = recorrido.semirrapido
        r.color_polilinea = recorrido.color_polilinea
        r.pois            = recorrido.pois
        r.descripcion     = recorrido.descripcion
        r.ruta            = GEOSGeometry(request.POST.get("geojson"))
        r.parent          = recorrido.uuid
        # save anyway, but respond as forbidden if not auth ;)
        r.save(user=user)
        
        data = {
            "id"    : r.id,
            "uuid"  : r.uuid,
            "nombre": r.nombre,
            "linea" : r.linea.nombre,
            "ciudad": r.ciudades[0].nombre
        }
        if request.user.is_authenticated():
            return HttpResponse(json.dumps(data), content_type="application/json")
        else:
            return HttpResponse(json.dumps(data), content_type="application/json", status=403)
    else:
        return HttpResponse(status=501)


@permission_required('editor.moderate_recorridos', login_url="/usuarios/login/", raise_exception=True)
def mostrar_ediciones(request):
    if request.method == 'GET':
        estado = request.GET.get('estado', None)
        ediciones = RecorridoProposed.objects.all()
        if estado != 'all':
            ediciones = ediciones.filter(current_status='E')
        ediciones = ediciones.order_by('-date_update')
        return render_to_response(
            'editor/moderacion_listado.html',
            {
                'ediciones': ediciones
            },
            context_instance=RequestContext(request)
        )
    else:
        return HttpResponse(status=501)

@permission_required('editor.moderate_recorridos', login_url="/usuarios/login/", raise_exception=True)
def moderar_ediciones_id(request, id=None):
    if request.method == 'GET':
        ediciones = RecorridoProposed.objects.filter(recorrido__id=id).order_by('-date_update')[:50]
        original = Recorrido.objects.get(id=id)
        #original = RecorridoProposed.objects.get(uuid=ediciones[0].parent)
        return render_to_response(
            'editor/moderacion_id.html',
            {
                'ediciones': ediciones,
                'original': original
            },
            context_instance=RequestContext(request)
        )
    else:
        return HttpResponse(status=501)


@permission_required('editor.moderate_recorridos', login_url="/usuarios/login/", raise_exception=True)
def moderar_ediciones_uuid(request, uuid=None):
    if request.method == 'GET':
        ediciones = RecorridoProposed.objects.filter(uuid=uuid).order_by('-date_update')[:50]
        original = RecorridoProposed.objects.filter(uuid=ediciones[0].parent)
        if original:
            original = original[0]
        else:
            original = Recorrido.objects.get(id=ediciones[0].recorrido.id)
        return render_to_response(
            'editor/moderacion_id.html',
            {
                'ediciones': ediciones,
                'original': original
            },
            context_instance=RequestContext(request)
        )
    else:
        return HttpResponse(status=501)


@csrf_exempt
def revision(request, id_revision=None):
    if request.method == 'GET' or request.method == 'POST':
        revision = RecorridoProposed.objects.get(id=id_revision)
        #print revision.parent
        original = RecorridoProposed.objects.filter(uuid=revision.parent)
        if original:
            original = original[0]
        else:
            original = revision.recorrido
        diffa = revision.ruta.difference(original.ruta)
        diffb = original.ruta.difference(revision.ruta)
        intersection = original.ruta.intersection(revision.ruta)
        return render_to_response(
            'editor/revision.html',
            {
                'revision': revision,
                'original': original,
                'diffa': diffa,
                'diffb': diffb,
                'intersection': intersection
            },
            context_instance=RequestContext(request)
        )
    else:
        return HttpResponse(status=501)


@permission_required('editor.moderate_recorridos', login_url="/usuarios/login/", raise_exception=True)
def moderar_ediciones_uuid_rechazar(request, uuid=None):
    RecorridoProposed.objects.get(uuid=uuid).logmoderacion_set.create(created_by=request.user,newStatus='N')
    return HttpResponseRedirect(request.GET.get("next"))


@permission_required('editor.moderate_recorridos', login_url="/usuarios/login/", raise_exception=True)
def moderar_ediciones_uuid_aprobar(request, uuid=None):
    proposed = RecorridoProposed.objects.get(uuid=uuid).aprobar(request.user)
    return HttpResponseRedirect(request.GET.get("next"))