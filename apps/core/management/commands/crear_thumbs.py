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
    
def save_img(pre_name, prefix, obj):
    fname = pre_name.format(prefix, obj.slug)
    with open(fname, 'r') as f:
        obj.img_cuadrada = File(f)
        try:
            obj.save()
        except AssertionError, e:
            print "ERROR al intentar guardar imagen de objeto ", str(obj)
            print str(e)
    os.remove(fname)

def ghost_make_map_img(obj, prefix, ciudad=None):
    if ciudad is None:
        url = '{0}{1}?dynamic_map=True'.format(settings.HOME_URL, obj.get_absolute_url())
    else:
        url = '{0}{1}?dynamic_map=True'.format(settings.HOME_URL, obj.get_absolute_url(ciudad.slug))
    print ">>> " + url
    for size in [(500, 500), (880, 300)]:
        fname = '/tmp/{0}-{1}.{2}x{3}.png'.format(prefix, obj.slug, size[0], size[1])
        proc = Process(target=create_screenshot, args=(url, fname, size ) )
        proc.start()
        proc.join()
        # optimizamos la imagen si tenemos pngcrush
        try:
            call('pngcrush -q -rem gAMA -rem cHRM -rem iCCP -rem sRGB -rem alla -rem text -reduce -brute {0} {1}.min'.format(fname, fname).split())
            os.remove(fname)
            shutil.move('{0}.min'.format(fname), fname)
        except OSError:
            pass
    save_img('/tmp/{0}-{1}.500x500.png', prefix, obj)
    save_img('/tmp/{0}-{1}.880x300.png', prefix, obj)
    
def ciudad_recursiva(c):
    for l in c.lineas.all():
        ghost_make_map_img(l, 'linea', c)
        for r in l.recorrido_set.all():
            ghost_make_map_img(r, 'recorrido', c)

def foto_de_linea(l, recursiva=False):
    try:
        c = l.ciudad_set.all()[0]
    except l.ciudad_set.DoesNotExist:
        print "ERROR: Salteando linea {0}. No se pudo encontrar la url porque la linea no tiene ninguna ciudad asociada [linea_id={1}]".format(l.slug, l.id)
    else:
        ghost_make_map_img(l, 'linea', c)
        if recursiva:
            for r in l.recorrido_set.all():
                ghost_make_map_img(r, 'recorrido', c)


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
        )
    )

    def handle(self, *args, **options):
        #ciudad
        if ( options['ciudades'] and options['recursivo'] ) or options['todas']:
            for ciudad in Ciudad.objects.all():
                ghost_make_map_img(ciudad, 'ciudad')
                ciudad_recursiva(ciudad)
            return 0

        if options['ciudades']:
            for ciudad in Ciudad.objects.all():
                ghost_make_map_img(ciudad, 'ciudad')   
        elif options['ciudad_slug'] or options['ciudad_id']:
            if options['ciudad_slug']:
                c = Ciudad.objects.get(slug=options['ciudad_slug'])
            else:
                c = Ciudad.objects.get(slug=options['ciudad_id'])
            ghost_make_map_img(c, 'ciudad')
            if options['r']:
                ciudad_recursiva(c)
        
        #linea
        if ( options['lineas'] and options['recursivo'] ):
            for l in Linea.objects.all():
                foto_de_linea(l, True)
            return 0

        if options['lineas']:
            for l in Linea.objects.all():
                foto_de_linea(l)
 
        elif options['linea_slug'] or options['linea_id']:
            if options['linea_slug']:
                l = Linea.objects.get(slug=options['linea_slug'])
            else:
                l = Linea.objects.get(id=options['linea_id'])
            foto_de_linea(l)
            if options['recursivo']:
                foto_de_linea(l, r)
        
        #recorrido
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
                ghost_make_map_img(r, 'recorrido', c)