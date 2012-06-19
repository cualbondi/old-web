from django.core.management.base import BaseCommand, CommandError
from apps.catastro.models import Ciudad, Provincia
from pprint import pprint

class Command(BaseCommand):
    def handle(self, *args, **options):
        adm1 = ArgAdm1.objects.all()
        # Recorrer para cada provincia en ArgAdm1
        for obj in adm1:
            provincia = Provincia()
            provincia.id = obj.id_1
            provincia.nombre = obj.name_1
            provincia.variantes_nombre = obj.varname_1
            provincia.poligono = obj.the_geom.convex_hull
            provincia.longitud_poligono = obj.shape_leng
            provincia.area_poligono = obj.shape_area
            provincia.save()
            print provincia.nombre
            # Recorrer para cada ciudad en ArgAdm2 dentro de esta provincia
            for obj2 in ArgAdm2.objects.filter(id_1=provincia.id):
                ciudad = Ciudad()
                ciudad.id = obj2.id_2
                ciudad.provincia = provincia
                ciudad.nombre = obj2.name_2
                ciudad.variantes_nombre = obj2.varname_2
                ciudad.poligono = obj2.the_geom.convex_hull
                ciudad.longitud_poligono = obj2.shape_leng
                ciudad.area_poligono = obj2.shape_area
                ciudad.save()
                print '..' + ciudad.nombre
            print
