from django.core.management.base import BaseCommand
from apps.catastro.models import Ciudad
from apps.core.models import Recorrido, Linea
from django.conf import settings
from optparse import make_option

from ghost import Ghost
from multiprocessing import Process
import os
from django.core.files import File
from django.contrib.sites.models import Site
from subprocess import call
import shutil

def create_screenshot(url, filename, size):
    ghost=Ghost(wait_timeout=40, viewport_size=size)
    ghost.open(url)
    ghost.wait_for_alert()
    ghost.wait_for_page_loaded()
    ghost.capture_to(filename,selector='#map')
    
def save_img(pre_name, prefix, obj, img_field):
    fname = pre_name.format(prefix, obj.slug)
    try:
        with open(fname, 'r') as f:
            setattr(obj, img_field, File(f))
            try:
                obj.save()
            except AssertionError, e:
                print "ERROR al intentar guardar imagen de objeto ", str(obj)
                print str(e)
        os.remove(fname)
    except IOError, e:
        print "ERROR abrir imagen de objeto", str(obj), ". No habia sido creada."
        print str(e)

def ghost_make_map_img(obj, prefix, ciudad=None, skip=False):
    print obj,
    if (not skip) or (not (obj.img_cuadrada and obj.img_panorama)):
        if ciudad is None:
            url = '{0}{1}?dynamic_map=True'.format(settings.HOME_URL, obj.get_absolute_url())
        else:
            url = '{0}{1}?dynamic_map=True'.format(settings.HOME_URL, obj.get_absolute_url(ciudad.slug))
        print ">>> " + url
        for size in [(500, 500), (880, 300)]:
            fname = '/tmp/{0}-{1}.{2}x{3}.png'.format(prefix, obj.slug, size[0], size[1])
            print "  >- Size: ", size
            print "   - Rendering HTML..."
            proc = Process(target=create_screenshot, args=(url, fname, size ) )
            proc.start()
            proc.join()
            # optimizamos la imagen si tenemos pngcrush
            print "   - pngcrushing it"        
            try:
                call('pngcrush -q -rem gAMA -rem cHRM -rem iCCP -rem sRGB -rem alla -rem text -reduce -brute {0} {1}.min'.format(fname, fname).split())
                os.remove(fname)
                shutil.move('{0}.min'.format(fname), fname)
            except OSError, e:
                print "pngcrush no instalado o no se encuentra en el PATH"
        save_img('/tmp/{0}-{1}.500x500.png', prefix, obj, 'img_cuadrada')
        save_img('/tmp/{0}-{1}.880x300.png', prefix, obj, 'img_panorama')
    else:
        print "WARNING: Salteando objeto porque utilizaste el parametro -s y el objeto ya tiene ambas thumbs precalculadas"
    
def ciudad_recursiva(c, skip=False):
    for l in c.lineas.all():
        ghost_make_map_img(l, 'linea', c, skip)
        for r in l.recorrido_set.all():
            ghost_make_map_img(r, 'recorrido', c, skip)

def foto_de_linea(l, recursiva=False, skip=False):
    try:
        c = l.ciudad_set.all()[0]
    except l.ciudad_set.DoesNotExist:
        print "ERROR: Salteando linea {0}. No se pudo encontrar la url porque la linea no tiene ninguna ciudad asociada [linea_id={1}]".format(l.slug, l.id)
    else:
        ghost_make_map_img(l, 'linea', c, skip)
        if recursiva:
            for r in l.recorrido_set.all():
                ghost_make_map_img(r, 'recorrido', c, skip)


class Command(BaseCommand):
    
    option_list = BaseCommand.option_list + (
        make_option(
            '--ciudad_slug',
            type    = 'string',
            action  = 'store',
            dest    = 'ciudad_slug',
            default = '',
            help    = 'Rehacer thumb de una ciudad (buscar por slug)'
        ),
        make_option(
            '--ciudad_id',
            type    = 'string',
            action  = 'store',
            dest    = 'ciudad_id',
            default = '',
            help    = 'Rehacer thumb de una ciudad (buscar por id)'
        ),
        make_option(
            '--linea_slug',
            type    = 'string',
            action  = 'store',
            dest    = 'linea_slug',
            default = '',
            help    = 'Rehacer thumb de una linea (buscar por slug)'
        ),
        make_option(
            '--linea_id',
            type    = 'string',
            action  = 'store',
            dest    = 'linea_id',
            default = '',
            help    = 'Rehacer thumb de una linea (buscar por id)'
        ),
        make_option(
            '--recorrido_slug',
            type    = 'string',
            action  = 'store',
            dest    = 'recorrido_slug',
            default = '',
            help    = 'Rehacer thumb de un recorrido (buscar por slug)'
        ),
        make_option(
            '--recorrido_id',
            type    = 'string',
            action  = 'store',
            dest    = 'recorrido_id',
            default = '',
            help    = 'Rehacer thumb de un recorrido (buscar por id)'
        ),
        make_option(
            '-C',
            action  = 'store_true',
            dest    = 'ciudades',
            default = False,
            help    = 'Rehacer thumbs de todas las ciudades'
        ),
        make_option(
            '-L',
            action  = 'store_true',
            dest    = 'lineas',
            default = False,
            help    = 'Rehacer thumbs de todas las lineas'
        ),
        make_option(
            '-R',
            action  = 'store_true',
            dest    = 'recorridos',
            default = False,
            help    = 'Rehacer thumbs de todos los recorridos'
        ),
        make_option(
            '-A',
            action  = 'store_true',
            dest    = 'todas',
            default = False,
            help    = 'Rehacer todas las thumbs (igual a -rC)'
        ),
        make_option(
            '-r',
            action  = 'store_true',
            dest    = 'recursivo',
            default = False,
            help    = 'Recursivo, dada una ciudad, rehacer las thumb de todas sus lineas y recorridos. Para una linea, rehacer la thumb de la linea mas las thumb de cada uno de los recorridos que contiene esa linea'
        ),
        make_option(
            '-s',
            action  = 'store_true',
            dest    = 'skip',
            default = False,
            help    = 'Saltear objetos que ya tienen thumbs creadas'
        )
    )

    def handle(self, *args, **options):
        #ciudad
        if ( options['ciudades'] and options['recursivo'] ) or options['todas']:
            for ciudad in Ciudad.objects.all():
                ghost_make_map_img(ciudad, 'ciudad', skip=options['skip'])
                ciudad_recursiva(ciudad, skip=options['skip'])
            return 0

        if options['ciudades']:
            for ciudad in Ciudad.objects.all():
                ghost_make_map_img(ciudad, 'ciudad', skip=options['skip'])   
        elif options['ciudad_slug'] or options['ciudad_id']:
            if options['ciudad_slug']:
                c = Ciudad.objects.get(slug=options['ciudad_slug'])
            else:
                c = Ciudad.objects.get(slug=options['ciudad_id'])
            ghost_make_map_img(c, 'ciudad', skip=options['skip'])
            if options['recursivo']:
                ciudad_recursiva(c, skip=options['skip'])
        
        #linea
        if ( options['lineas'] and options['recursivo'] ):
            for l in Linea.objects.all():
                foto_de_linea(l, True, skip=options['skip'])
            return 0

        if options['lineas']:
            for l in Linea.objects.all():
                foto_de_linea(l, skip=options['skip'])
 
        elif options['linea_slug'] or options['linea_id']:
            if options['linea_slug']:
                l = Linea.objects.get(slug=options['linea_slug'])
            else:
                l = Linea.objects.get(id=options['linea_id'])
            foto_de_linea(l, skip=options['skip'])
            if options['recursivo']:
                foto_de_linea(l, recursiva=options['recursivo'], skip=options['skip'])
        
        #recorrido
        rs=[]
        if options['recorridos']:
            rs = Recorrido.objects.all()
        elif options['recorrido_slug']:
            rs = [Recorrido.objects.get(slug=options['recorrido_slug'])]
        elif options['recorrido_id']:
            rs = [Recorrido.objects.get(id=options['recorrido_id'])]
        
        for r in rs:
            try:
                c = r.linea.ciudad_set.all()[0]
            except DoesNotExist:
                print "ERROR: Salteando recorrido {0}. No se pudo encontrar la url porque el recorrido no tiene ninguna ciudad asociada [recorrido_id={1}]".format(r.slug, r.id)
            else:
                ghost_make_map_img(r, 'recorrido', ciudad=c, skip=options['skip'])