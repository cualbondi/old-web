# -*- coding: utf-8 *-*
"""Migra los datos de la BD colectivos a los nuevos modelos de django"""

import psycopg2
from psycopg2.extras import RealDictCursor

from django.db import connection
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist

from apps.catastro.models import Provincia, Ciudad
from apps.core.models import Linea, Recorrido


class Command(BaseCommand):
    def handle(self, *args, **options):
        cursor = connection.cursor()
        db = psycopg2.connect(
            host='127.0.0.1',
            database='colectivos',
            user='web_colectivos',
            password='soylawebcolectivos'
        )
        cursor = db.cursor(cursor_factory=RealDictCursor)
        stats = {'ciudades': 0, 'lineas': 0, 'recorridos': 0}

        # agrego una provincia falsa para referenciar las ciudades
        provincia = Provincia(nombre="fake")
        provincia.save()

        cursor.execute("""
            SELECT id
            FROM ciudad;
        """)

        for row in cursor.fetchall():
            try:
                Ciudad.objects.get(slug=row['id'])
            except ObjectDoesNotExist:
                nombre = row['id'].replace("-", " ").title()
                ciudad = Ciudad(
                    nombre=nombre,
                    provincia=provincia
                )
                ciudad.save()
                stats['ciudades'] += 1

        cursor.execute("""
            SELECT nombre, descripcion, foto, info_empresa, info_terminal,
                   id, semirrapido, localidad, cp, telefono
            FROM linea;
        """)

        for row in cursor.fetchall():
            try:
                Linea.objects.get(id=row['id'])
            except ObjectDoesNotExist:
                linea = Linea(
                    id=row['id'],
                    nombre=row['nombre'],
                    descripcion=row['descripcion'],
                    foto=row['foto'],
                    info_empresa=row['info_empresa'],
                    info_terminal=row['info_terminal'],
                    localidad=row['localidad'],
                    cp=row['cp'],
                    telefono=row['telefono']
                )
                linea.save()
                stats['lineas'] += 1

        cursor.execute("""
            SELECT
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
            FROM recorrido re
            JOIN ramal ra on (ra.id = re.id_ramal);
        """)

        for row in cursor.fetchall():
            try:
                Recorrido.objects.get(id=row['re_id'])
            except ObjectDoesNotExist:
                recorrido = Recorrido(
                    id=row['re_id'],
                    nombre=row['ra_nombre'],
                    sentido=row['re_nombre'],
                    linea=Linea.objects.get(id=row['ra_id_linea']),
                    inicio=row['re_zona_inicio'],
                    fin=row['re_zona_fin'],
                    ruta=row['re_camino'],
                    color_polilinea=row['re_color_polilinea'],
                    horarios=row['re_horarios'],
                    pois=row['ra_descripcion'],
                    descripcion=row['re_descripcion']
                )
                recorrido.save()
                stats['recorridos'] += 1

        print "Se han agregado:", stats
