from apps.core.models import Ciudad, Linea, Recorrido
from piston.handler import BaseHandler
from piston.utils import rc
from django.core.exceptions import ObjectDoesNotExist
from settings import RADIO_ORIGEN_DEFAULT, RADIO_DESTINO_DEFAULT
from django.contrib.gis.geos import Point


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

    def _get_response_from_cache(self, origen, destino, radio_origen, radio_destino, combinar, pagina):
        return None

    def read(self, request, id_recorrido=None):
        if id_recorrido is None:
            origen = request.GET.get('origen', None)
            destino = request.GET.get('destino', None)
            radio_origen = request.GET.get('radio_origen', RADIO_ORIGEN_DEFAULT)
            radio_destino = request.GET.get('radio_destino', RADIO_DESTINO_DEFAULT)
            query = request.GET.get('query', None)

            combinar = request.GET.get('combinar', False)
            pagina = request.GET.get('pagina', 1)

            if query is not None:
                # Buscar recorridos por nombre
                rc.NOT_IMPLEMENTED
            elif origen is not None and destino is not None:
                # Buscar geograficamente en base a origen y destino
                """ TODO: Checkear que venga un float y no cualquier otra cosa! """
                origen = str(origen).split(",")
                origen = Point(float(origen[1]), float(origen[0]))

                destino = str(destino).split(",")
                destino = Point(float(destino[1]), float(destino[0]))

                recorridos = self._get_response_from_cache(origen, destino,
                                radio_origen, radio_destino, combinar, pagina)
                if recorridos is None:
                    # No se encontro en la cache, hay que buscarlo en la DB.
                    if not combinar:
                        # Buscar SIN transbordo
                        return Recorrido.objects.get_recorridos(origen, destino, radio_origen, radio_destino)
                    else:
                        # Buscar CON transbordo
                        recorridos = Recorrido.objects.get_recorridos_combinados(origen, destino, radio_origen, radio_destino)
                        rc.NOT_IMPLEMENTED
            else:
                # Sin parametros GET, devolver todos los recorridos
                return Recorrido.objects.all()
        else:
            try:
                return Recorrido.objects.get(id=id_recorrido)
            except ObjectDoesNotExist:
                return rc.NOT_FOUND




