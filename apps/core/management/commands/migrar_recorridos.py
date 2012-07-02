# -*- coding: utf-8 *-*
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import DoesNotExist
from apps.core.models import Recorrido, Linea
from apps.catastro.models import Ciudad
from django.db import connection, transaction
import psycopg2
import psycopg2.extras
from pprint import pprint
from django.template.defaultfilters import slugify

class Command(BaseCommand):
    def handle(self, *args, **options):
        cursor = connection.cursor()
        db = psycopg2.connect(
            host = '127.0.0.1',
            database = 'colectivos',
            user = 'web_colectivos',
            password = 'soylawebcolectivos'
        )
        cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("""
            SELECT
                li.nombre as li_nombre,
                li.descripcion as li_descripcion,
                li.foto as li_foto,
                li.info_empresa as li_info_empresa,
                li.info_terminal as li_info_terminal,
                li.id as li_id,
                li.semirrapido as li_semirrapido,
                li.localidad as li_localidad,
                li.cp as li_cp,
                li.telefono as li_telefono,
                ra.nombre as ra_nombre,
                ra.descripcion as ra_descripcion,
                ra.id_linea as ra_id_linea,
                ra.id as ra_id,
                re.nombre as re_nombre,
                re.zona_inicio as re_zona_inicio,
                re.zona_fin as re_zona_fin,
                re.descripcion as re_descripcion,
                re.id_ramal as re_id_ramal,
                re.color_polilinea as re_color_polilinea,
                re.horarios as re_horarios,
                re.id as re_id,
                ST_Affine(re.camino,
                    cos(pi()/2), sin(pi()/2),
                    sin(pi()/2), cos(pi()/2),
                    0,          0
                ) as re_camino,
                re.edicion_fuente_nombre as re_edicion_fuente_nombre,
                re.edicion_fuente_contacto as re_edicion_fuente_contacto,
                re.edicion_id_usuario as re_edicion_id_usuario,
                re.save_timestamp as re_save_timestamp,
                re.edicion_datatimestamp as re_edicion_datatimestamp
            FROM
                linea li
                JOIN ramal     ra on (li.id = ra.id_linea)
                JOIN recorrido re on (ra.id = re.id_ramal)
        """)
        for row in cursor.fetchall():
            try:
                linea = Linea.objects.get(nombre=row['li_nombre'])
            except DoesNotExist:
                # la linea aun no fue agregada, hay que crearla
                linea = Linea(
                    nombre = row['li_nombre'],
                    descripcion = row['li_descripcion']
                )
                linea.save()

            recorrido = Recorrido(
                nombre = row['ra_nombre'] + row['re_nombre'],
                linea = linea,
                inicio = row['re_zona_inicio'],
                fin = row['re_zona_fin'],
                semirrapido = row['li_semirrapido'],
                ruta = row['re_camino']
            )
            recorrido.save()
