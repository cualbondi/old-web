from apps.core.models import Linea, Recorrido
from piston.handler import BaseHandler

class LineaHandler(BaseHandler):
    allowed_methods = ['GET']
    model = Linea
    exclude = ()

    def read(self, request, id_linea=None):
        if id_linea is None:
            # Devolver la lista completa de Lineas
            return Linea.objects.all()
        else:
            return Linea.objects.filter(id=id_linea)


class RecorridoHandler(BaseHandler):
    allowed_methods = ['GET']
    model = Recorrido
    exclude = ()

    def read(self, request, id_recorrido=None):
        if id_recorrido is None:
            # Devolver la lista completa de Recorridos
            return Recorrido.objects.all()
        else:
            return Recorrido.objects.filter(id=id_recorrido)
