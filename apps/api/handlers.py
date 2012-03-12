from apps.core.models import Ciudad, Linea, Recorrido
from piston.handler import BaseHandler
from piston.utils import rc
from django.core.exceptions import ObjectDoesNotExist


class CiudadHandler(BaseHandler):
    allowed_methods = ['GET']
    model = Ciudad
    exclude = ()

    def read(self, request, id_ciudad=None):
        if id_ciudad is None:
            return Ciudad.objects.all()
        else:
            try:
                return Ciudad.objects.get(id=id_ciudad)
            except ObjectDoesNotExist:
                return rc.NOT_FOUND


class CiudadLineaHandler(BaseHandler):
    allowed_methods = ['GET']
    exclude = ()

    def read(self, request, id_ciudad=None):
        if id_ciudad is None:
            return rc.BAD_REQUEST
        else:
            try:
                return Ciudad.objects.get(id=id_ciudad).lineas.all()
            except ObjectDoesNotExist:
                return rc.NOT_FOUND


class CiudadRecorridoHandler(BaseHandler):
    allowed_methods = ['GET']
    exclude = ()

    def read(self, request, id_ciudad=None):
        if id_ciudad is None:
            return rc.BAD_REQUEST
        else:
            try:
                return Ciudad.objects.get(id=id_ciudad).recorridos.all()
            except ObjectDoesNotExist:
                return rc.NOT_FOUND


class LineaHandler(BaseHandler):
    allowed_methods = ['GET']
    model = Linea
    exclude = ()

    def read(self, request, id_linea=None):
        if id_linea is None:
            # Devolver la lista completa de Lineas
            return Linea.objects.all()
        else:
            try:
                return Linea.objects.get(id=id_linea)
            except ObjectDoesNotExist:
                return rc.NOT_FOUND


class LineaRecorridoHandler(BaseHandler):
    allowed_methods = ['GET']
    exclude = ()

    def read(self, request, id_linea=None):
        if id_linea is None:
            return rc.BAD_REQUEST
        else:
            try:
                l = Linea.objects.get(id=id_linea)
                return Recorrido.objects.filter(linea=l)
            except ObjectDoesNotExist:
                return rc.NOT_FOUND


class RecorridoHandler(BaseHandler):
    allowed_methods = ['GET']
    model = Recorrido
    exclude = ()

    def read(self, request, id_recorrido=None):
        if id_recorrido is None:
            # Devolver la lista completa de Recorridos
            return Recorrido.objects.all()
        else:
            try:
                return Recorrido.objects.get(id=id_recorrido)
            except ObjectDoesNotExist:
                return rc.NOT_FOUND




