# -*- coding: UTF-8 -*-
from django.db import DatabaseError, connection
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
import math


class RecorridoManager(models.GeoManager):
    def get_recorridos_combinados(self, puntoA, puntoB, distanciaA, distanciaB, gap):
        distanciaA = int(distanciaA)
        distanciaB = int(distanciaB)
        gap = int(gap)
        if not isinstance(puntoA, Point):
            raise DatabaseError("get_recorridos: PuntoA Expected GEOS Point instance as parameter, %s given" % type(puntoA))
        if not isinstance(puntoB, Point):
            raise DatabaseError("get_recorridos: PuntoB Expected GEOS Point instance as parameter, %s given" % type(puntoB))
        if not isinstance(distanciaA, (int, long)):
            raise DatabaseError("get_recorridos: distanciaA Expected integer as parameter, %s given" % type(distanciaA))
        if not isinstance(distanciaB, (int, long)):
            raise DatabaseError("get_recorridos: distanciaB Expected integer as parameter, %s given" % type(distanciaB))
        if not isinstance(gap, (int, long)):
            raise DatabaseError("get_recorridos: gap Expected integer as parameter, %s given" % type(gap))
        puntoA.set_srid(4326)
        puntoB.set_srid(4326)
        distanciaA = 0.0000111 * float(distanciaA) 
        distanciaB = 0.0000111 * float(distanciaB)
        gap = 0.0000111 * float(gap) 

        connection.cursor().execute('SET STATEMENT_TIMEOUT=45000')

        params = {'puntoA': puntoA.ewkt, 'puntoB': puntoB.ewkt, 'rad1': distanciaA, 'rad2': distanciaB, 'gap': gap}
        query = """
            SELECT *
            FROM 
            (
                SELECT *,
                ST_AsText(
                    ST_Line_Substring(
                        re1_ruta,
                        ST_Line_Locate_Point(re1_ruta, ll11),
                        ST_Line_Locate_Point(re1_ruta, ll12)
                        )::Geography
                    ) as ruta_corta,
                ST_AsText(
                    ST_Line_Substring(
                        re2_ruta,
                        ST_Line_Locate_Point(re2_ruta, ll21),
                        ST_Line_Locate_Point(re2_ruta, ll22)
                        )::Geography
                    ) as ruta_corta2,
                ST_Length(
                    ST_Line_Substring(
                        re1_ruta,
                        ST_Line_Locate_Point(re1_ruta, ll11),
                        ST_Line_Locate_Point(re1_ruta, ll12)
                        )::Geography
                    ) as long_ruta,
                ST_Length(
                    ST_Line_Substring(
                        re2_ruta,
                        ST_Line_Locate_Point(re2_ruta, ll21),
                        ST_Line_Locate_Point(re2_ruta, ll22)
                        )::Geography
                    ) as long_ruta2,
                ST_Distance_Sphere(ll11, re1_ruta) as long_pata,
                ST_Distance_Sphere(ll22, re2_ruta) as long_pata2,
                ST_Distance_Sphere(ll21, ll12) as long_pata_transbordo
            FROM (
                SELECT
                    re1.id as id,
                    re1.ruta as re1_ruta,
                    re2.ruta as re2_ruta,
                    li1.nombre || ' ' || re1.nombre as nombre,
                    li2.nombre || ' ' || re2.nombre as nombre2,
                    re2.id as id2,
                    coalesce(re1.color_polilinea, li1.color_polilinea, '#000') as color_polilinea,
                    coalesce(re2.color_polilinea, li2.color_polilinea, '#000') as color_polilinea2,
                    coalesce(li1.foto, 'default') as foto,
                    coalesce(li2.foto, 'default') as foto2,
                    re1.inicio as inicio,
                    re2.inicio as inicio2,
                    re1.fin as fin,
                    re2.fin as fin2,
                    re1.paradas_completas as re1_paradas_completas,
                    re2.paradas_completas as re2_paradas_completas,
                    coalesce(p11.latlng, ST_GeomFromText(%(puntoA)s)) as ll11,
                    coalesce(p12.latlng, ST_ClosestPoint(re1.ruta, coalesce(p21.latlng, re2.ruta))) as ll12,
                    coalesce(p21.latlng, ST_ClosestPoint(re2.ruta, coalesce(p12.latlng, re1.ruta))) as ll21,
                    coalesce(p22.latlng, ST_GeomFromText(%(puntoB)s)) as ll22,
                    p11.id as p11ll,
                    p12.id as p12ll,
                    p21.id as p21ll,
                    p22.id as p22ll
                FROM
                    core_recorrido as re1
                    join core_recorrido as re2 on (re1.id <> re2.id)
                    join core_linea li1 on li1.id = re1.linea_id
                    join core_linea li2 on li2.id = re2.linea_id
                    LEFT OUTER JOIN core_horario as h11 on (h11.recorrido_id = re1.id)
                    LEFT OUTER JOIN core_horario as h12 on (h12.recorrido_id = re1.id)
                    LEFT OUTER JOIN core_parada  as p11 on (p11.id = h11.parada_id)
                    LEFT OUTER JOIN core_parada  as p12 on (p12.id = h12.parada_id and p11.id <> p12.id)
                    LEFT OUTER JOIN core_horario as h21 on (h21.recorrido_id = re2.id)
                    LEFT OUTER JOIN core_horario as h22 on (h22.recorrido_id = re2.id)
                    LEFT OUTER JOIN core_parada  as p21 on (p21.id = h21.parada_id)
                    LEFT OUTER JOIN core_parada  as p22 on (p22.id = h22.parada_id and p21.id <> p22.id)
                ) as sq
            WHERE
                (
                    ST_DWithin(re1_ruta, ll11, %(rad1)s)
                    and
                    ST_DWithin(re2_ruta, ll22, %(rad2)s)
                    and
                        ST_DWithin(ll21, ll12, %(gap)s)
                    and
                        ST_Line_Locate_Point(re1_ruta, ll11)
                        <
                        ST_Line_Locate_Point(re1_ruta, ll12 )
                    and
                        ST_Line_Locate_Point(re2_ruta, ll21 )
                        <
                        ST_Line_Locate_Point(re2_ruta, ll22)
                    and
                        (not re1_paradas_completas) and (not re2_paradas_completas)
                )

            UNION
            SELECT *,
                ST_AsText(
                    ST_Line_Substring(
                        re1_ruta,
                        ST_Line_Locate_Point(re1_ruta, ll11),
                        ST_Line_Locate_Point(re1_ruta, ll12)
                        )::Geography
                    ) as ruta_corta,
                ST_AsText(
                    ST_Line_Substring(
                        re2_ruta,
                        ST_Line_Locate_Point(re2_ruta, ll21),
                        ST_Line_Locate_Point(re2_ruta, ll22)
                        )::Geography
                    ) as ruta_corta2,
                ST_Length(
                    ST_Line_Substring(
                        re1_ruta,
                        ST_Line_Locate_Point(re1_ruta, ll11),
                        ST_Line_Locate_Point(re1_ruta, ll12)
                        )::Geography
                    ) as long_ruta,
                ST_Length(
                    ST_Line_Substring(
                        re2_ruta,
                        ST_Line_Locate_Point(re2_ruta, ll21),
                        ST_Line_Locate_Point(re2_ruta, ll22)
                        )::Geography
                    ) as long_ruta2,
                ST_Distance_Sphere(ll11, re1_ruta) as long_pata,
                ST_Distance_Sphere(ll22, re2_ruta) as long_pata2,
                ST_Distance_Sphere(ll21, ll12) as long_pata_transbordo
            FROM (
                SELECT
                    re1.id as id,
                    re1.ruta as re1_ruta,
                    re2.ruta as re2_ruta,
                    li1.nombre || ' ' || re1.nombre as nombre,
                    li2.nombre || ' ' || re2.nombre as nombre2,
                    re2.id as id2,
                    coalesce(re1.color_polilinea, li1.color_polilinea, '#000') as color_polilinea,
                    coalesce(re2.color_polilinea, li2.color_polilinea, '#000') as color_polilinea2,
                    coalesce(li1.foto, 'default') as foto,
                    coalesce(li2.foto, 'default') as foto2,
                    re1.inicio as inicio,
                    re2.inicio as inicio2,
                    re1.fin as fin,
                    re2.fin as fin2,
                    re1.paradas_completas as re1_paradas_completas,
                    re2.paradas_completas as re2_paradas_completas,
                    coalesce(p11.latlng, ST_GeomFromText(%(puntoA)s)) as ll11,
                    coalesce(p12.latlng, ST_ClosestPoint(re1.ruta, coalesce(p21.latlng, re2.ruta))) as ll12,
                    coalesce(p21.latlng, ST_ClosestPoint(re2.ruta, coalesce(p12.latlng, re1.ruta))) as ll21,
                    coalesce(p22.latlng, ST_GeomFromText(%(puntoB)s)) as ll22,
                    p11.id as p11ll,
                    p12.id as p12ll,
                    p21.id as p21ll,
                    p22.id as p22ll
                FROM
                    core_recorrido as re1
                    join core_recorrido as re2 on (re1.id <> re2.id)
                    join core_linea li1 on li1.id = re1.linea_id
                    join core_linea li2 on li2.id = re2.linea_id
                    LEFT OUTER JOIN core_horario as h11 on (h11.recorrido_id = re1.id)
                    LEFT OUTER JOIN core_horario as h12 on (h12.recorrido_id = re1.id)
                    LEFT OUTER JOIN core_parada  as p11 on (p11.id = h11.parada_id)
                    LEFT OUTER JOIN core_parada  as p12 on (p12.id = h12.parada_id and p11.id <> p12.id)
                    LEFT OUTER JOIN core_horario as h21 on (h21.recorrido_id = re2.id)
                    LEFT OUTER JOIN core_horario as h22 on (h22.recorrido_id = re2.id)
                    LEFT OUTER JOIN core_parada  as p21 on (p21.id = h21.parada_id)
                    LEFT OUTER JOIN core_parada  as p22 on (p22.id = h22.parada_id and p21.id <> p22.id)
                ) as sq
            WHERE
                (
                    ST_DWithin(ST_GeomFromText(%(puntoA)s), ll11, %(rad1)s)
                    and 
                    ST_DWithin(re2_ruta, ll22, %(rad2)s)
                    and
                        ST_DWithin(ll21, ll12, %(gap)s)
                    and
                        ST_Line_Locate_Point(re1_ruta, ll11)
                        <
                        ST_Line_Locate_Point(re1_ruta, ll12 )
                    and
                        ST_Line_Locate_Point(re2_ruta, ll21 )
                        <
                        ST_Line_Locate_Point(re2_ruta, ll22)
                    and
                        re1_paradas_completas and (not re2_paradas_completas)
                    and 
                        p11ll is not null and p12ll is not null
                )
            UNION
            SELECT *,
                ST_AsText(
                    ST_Line_Substring(
                        re1_ruta,
                        ST_Line_Locate_Point(re1_ruta, ll11),
                        ST_Line_Locate_Point(re1_ruta, ll12)
                        )::Geography
                    ) as ruta_corta,
                ST_AsText(
                    ST_Line_Substring(
                        re2_ruta,
                        ST_Line_Locate_Point(re2_ruta, ll21),
                        ST_Line_Locate_Point(re2_ruta, ll22)
                        )::Geography
                    ) as ruta_corta2,
                ST_Length(
                    ST_Line_Substring(
                        re1_ruta,
                        ST_Line_Locate_Point(re1_ruta, ll11),
                        ST_Line_Locate_Point(re1_ruta, ll12)
                        )::Geography
                    ) as long_ruta,
                ST_Length(
                    ST_Line_Substring(
                        re2_ruta,
                        ST_Line_Locate_Point(re2_ruta, ll21),
                        ST_Line_Locate_Point(re2_ruta, ll22)
                        )::Geography
                    ) as long_ruta2,
                ST_Distance_Sphere(ll11, re1_ruta) as long_pata,
                ST_Distance_Sphere(ll22, re2_ruta) as long_pata2,
                ST_Distance_Sphere(ll21, ll12) as long_pata_transbordo
            FROM (
                SELECT
                    re1.id as id,
                    re1.ruta as re1_ruta,
                    re2.ruta as re2_ruta,
                    li1.nombre || ' ' || re1.nombre as nombre,
                    li2.nombre || ' ' || re2.nombre as nombre2,
                    re2.id as id2,
                    coalesce(re1.color_polilinea, li1.color_polilinea, '#000') as color_polilinea,
                    coalesce(re2.color_polilinea, li2.color_polilinea, '#000') as color_polilinea2,
                    coalesce(li1.foto, 'default') as foto,
                    coalesce(li2.foto, 'default') as foto2,
                    re1.inicio as inicio,
                    re2.inicio as inicio2,
                    re1.fin as fin,
                    re2.fin as fin2,
                    re1.paradas_completas as re1_paradas_completas,
                    re2.paradas_completas as re2_paradas_completas,
                    coalesce(p11.latlng, ST_GeomFromText(%(puntoA)s)) as ll11,
                    coalesce(p12.latlng, ST_ClosestPoint(re1.ruta, coalesce(p21.latlng, re2.ruta))) as ll12,
                    coalesce(p21.latlng, ST_ClosestPoint(re2.ruta, coalesce(p12.latlng, re1.ruta))) as ll21,
                    coalesce(p22.latlng, ST_GeomFromText(%(puntoB)s)) as ll22,
                    p11.id as p11ll,
                    p12.id as p12ll,
                    p21.id as p21ll,
                    p22.id as p22ll
                FROM
                    core_recorrido as re1
                    join core_recorrido as re2 on (re1.id <> re2.id)
                    join core_linea li1 on li1.id = re1.linea_id
                    join core_linea li2 on li2.id = re2.linea_id
                    LEFT OUTER JOIN core_horario as h11 on (h11.recorrido_id = re1.id)
                    LEFT OUTER JOIN core_horario as h12 on (h12.recorrido_id = re1.id)
                    LEFT OUTER JOIN core_parada  as p11 on (p11.id = h11.parada_id)
                    LEFT OUTER JOIN core_parada  as p12 on (p12.id = h12.parada_id and p11.id <> p12.id)
                    LEFT OUTER JOIN core_horario as h21 on (h21.recorrido_id = re2.id)
                    LEFT OUTER JOIN core_horario as h22 on (h22.recorrido_id = re2.id)
                    LEFT OUTER JOIN core_parada  as p21 on (p21.id = h21.parada_id)
                    LEFT OUTER JOIN core_parada  as p22 on (p22.id = h22.parada_id and p21.id <> p22.id)
                ) as sq
            WHERE
                (
                    ST_DWithin(re1_ruta, ll11, %(rad1)s)
                    and 
                    ST_DWithin(ST_GeomFromText(%(puntoB)s), ll22, %(rad2)s)
                    and
                        ST_DWithin(ll21, ll12, %(gap)s)
                    and
                        ST_Line_Locate_Point(re1_ruta, ll11)
                        <
                        ST_Line_Locate_Point(re1_ruta, ll12 )
                    and
                        ST_Line_Locate_Point(re2_ruta, ll21 )
                        <
                        ST_Line_Locate_Point(re2_ruta, ll22)
                    and
                        (not re1_paradas_completas) and re2_paradas_completas
                    and
                        p21ll is not null and p22ll is not null
                )
            UNION
            SELECT *,
                ST_AsText(
                    ST_Line_Substring(
                        re1_ruta,
                        ST_Line_Locate_Point(re1_ruta, ll11),
                        ST_Line_Locate_Point(re1_ruta, ll12)
                        )::Geography
                    ) as ruta_corta,
                ST_AsText(
                    ST_Line_Substring(
                        re2_ruta,
                        ST_Line_Locate_Point(re2_ruta, ll21),
                        ST_Line_Locate_Point(re2_ruta, ll22)
                        )::Geography
                    ) as ruta_corta2,
                ST_Length(
                    ST_Line_Substring(
                        re1_ruta,
                        ST_Line_Locate_Point(re1_ruta, ll11),
                        ST_Line_Locate_Point(re1_ruta, ll12)
                        )::Geography
                    ) as long_ruta,
                ST_Length(
                    ST_Line_Substring(
                        re2_ruta,
                        ST_Line_Locate_Point(re2_ruta, ll21),
                        ST_Line_Locate_Point(re2_ruta, ll22)
                        )::Geography
                    ) as long_ruta2,
                ST_Distance_Sphere(ll11, re1_ruta) as long_pata,
                ST_Distance_Sphere(ll22, re2_ruta) as long_pata2,
                ST_Distance_Sphere(ll21, ll12) as long_pata_transbordo
            FROM (
                SELECT
                    re1.id as id,
                    re1.ruta as re1_ruta,
                    re2.ruta as re2_ruta,
                    li1.nombre || ' ' || re1.nombre as nombre,
                    li2.nombre || ' ' || re2.nombre as nombre2,
                    re2.id as id2,
                    coalesce(re1.color_polilinea, li1.color_polilinea, '#000') as color_polilinea,
                    coalesce(re2.color_polilinea, li2.color_polilinea, '#000') as color_polilinea2,
                    coalesce(li1.foto, 'default') as foto,
                    coalesce(li2.foto, 'default') as foto2,
                    re1.inicio as inicio,
                    re2.inicio as inicio2,
                    re1.fin as fin,
                    re2.fin as fin2,
                    re1.paradas_completas as re1_paradas_completas,
                    re2.paradas_completas as re2_paradas_completas,
                    coalesce(p11.latlng, ST_GeomFromText(%(puntoA)s)) as ll11,
                    coalesce(p12.latlng, ST_ClosestPoint(re1.ruta, coalesce(p21.latlng, re2.ruta))) as ll12,
                    coalesce(p21.latlng, ST_ClosestPoint(re2.ruta, coalesce(p12.latlng, re1.ruta))) as ll21,
                    coalesce(p22.latlng, ST_GeomFromText(%(puntoB)s)) as ll22,
                    p11.id as p11ll,
                    p12.id as p12ll,
                    p21.id as p21ll,
                    p22.id as p22ll
                FROM
                    core_recorrido as re1
                    join core_recorrido as re2 on (re1.id <> re2.id)
                    join core_linea li1 on li1.id = re1.linea_id
                    join core_linea li2 on li2.id = re2.linea_id
                    LEFT OUTER JOIN core_horario as h11 on (h11.recorrido_id = re1.id)
                    LEFT OUTER JOIN core_horario as h12 on (h12.recorrido_id = re1.id)
                    LEFT OUTER JOIN core_parada  as p11 on (p11.id = h11.parada_id)
                    LEFT OUTER JOIN core_parada  as p12 on (p12.id = h12.parada_id and p11.id <> p12.id)
                    LEFT OUTER JOIN core_horario as h21 on (h21.recorrido_id = re2.id)
                    LEFT OUTER JOIN core_horario as h22 on (h22.recorrido_id = re2.id)
                    LEFT OUTER JOIN core_parada  as p21 on (p21.id = h21.parada_id)
                    LEFT OUTER JOIN core_parada  as p22 on (p22.id = h22.parada_id and p21.id <> p22.id)
                ) as sq
            WHERE
                (
                    ST_DWithin(ST_GeomFromText(%(puntoA)s), ll11, %(rad2)s)
                    and 
                    ST_DWithin(ST_GeomFromText(%(puntoB)s), ll22, %(rad2)s)
                    and
                        ST_DWithin(ll21, ll12, %(gap)s)
                    and
                        ST_Line_Locate_Point(re1_ruta, ll11)
                        <
                        ST_Line_Locate_Point(re1_ruta, ll12 )
                    and
                        ST_Line_Locate_Point(re2_ruta, ll21 )
                        <
                        ST_Line_Locate_Point(re2_ruta, ll22)
                    and
                        re1_paradas_completas and re2_paradas_completas
                    and
                        p21ll is not null and p22ll is not null
                    and
                        p21ll is not null and p22ll is not null
                )
            ) as sq2
            ORDER BY (cast(long_pata+long_pata2+long_pata_transbordo as integer)*100 + ( cast(long_ruta as integer) + cast(long_ruta2 as integer) ) ) ASC
        ;"""
        query_set = self.raw(query, params)
        return list(query_set)

    def get_recorridos(self, puntoA, puntoB, distanciaA, distanciaB):
        distanciaA = int(distanciaA)
        distanciaB = int(distanciaB)
        if not isinstance(puntoA, Point):
            raise DatabaseError("get_recorridos: PuntoA Expected GEOS Point instance as parameter, %s given" % type(puntoA))
        if not isinstance(puntoB, Point):
            raise DatabaseError("get_recorridos: PuntoB Expected GEOS Point instance as parameter, %s given" % type(puntoB))
        if not isinstance(distanciaA, (int, long)):
            raise DatabaseError("get_recorridos: distanciaA Expected integer as parameter, %s given" % type(distanciaA))
        if not isinstance(distanciaB, (int, long)):
            raise DatabaseError("get_recorridos: distanciaB Expected integer as parameter, %s given" % type(distanciaB))
        puntoA.set_srid(4326)
        puntoB.set_srid(4326)
        distanciaA = 0.0000111 * float(distanciaA) 
        distanciaB = 0.0000111 * float(distanciaB)

        params = {'puntoA': puntoA.ewkt, 'puntoB': puntoB.ewkt, 'rad1': distanciaA, 'rad2': distanciaB}
        query = """
                SELECT
                    re.id,
                    li.nombre || ' ' || re.nombre as nombre,
                    ruta_corta,
                    round(long_ruta::numeric, 2) as long_ruta,
                    round(long_pata::numeric, 2) as long_pata,
                    coalesce(re.color_polilinea, li.color_polilinea, '#000') as color_polilinea,
                    coalesce(li.foto, 'default') as foto,
                    p1,
                    p2
                FROM
                    core_linea as li join
                    (
                        SELECT
                            id,
                            nombre,
                            linea_id,
                            color_polilinea,
                            ST_AsText(min_path(ruta_corta)) as ruta_corta,
                            min(long_ruta) as long_ruta,
                            min(long_pata) as long_pata,
                            p1,
                            p2
                        FROM
                        (
                            SELECT
                                id,
                                nombre,
                                linea_id,
                                color_polilinea,
                                ruta_corta,
                                ST_Length(ruta_corta::Geography) as long_ruta,
                                ST_Distance_Sphere(ST_GeomFromText(%(puntoA)s),coalesce(p1ll, ruta_corta)) + ST_Distance_Sphere(ST_GeomFromText(%(puntoB)s),coalesce(p2ll, ruta_corta)) as long_pata,
                                p1,
                                p2
                            FROM
                                (
                                    SELECT
                                        id,
                                        nombre,
                                        linea_id,
                                        color_polilinea,
                                        ST_Line_Substring(
                                            ST_Line_Substring(ruta, 0, 0.5),
                                            ST_Line_Locate_Point(ST_Line_Substring(ruta, 0, 0.5),	%(puntoA)s),
                                            ST_Line_Locate_Point(ST_Line_Substring(ruta, 0, 0.5),	%(puntoB)s)
                                        ) as ruta_corta,
                                        null::integer as p1,
                                        null::integer as p2,
                                        null::geometry as p1ll,
                                        null::geometry as p2ll
                                    FROM
                                        core_recorrido
                                    WHERE
                                        ST_DWithin(ST_GeomFromText(%(puntoA)s), ST_Line_Substring(ruta, 0, 0.5), %(rad1)s) and
                                        ST_DWithin(ST_GeomFromText(%(puntoB)s), ST_Line_Substring(ruta, 0, 0.5), %(rad2)s) and
                                        ST_Line_Locate_Point(ST_Line_Substring(ruta, 0, 0.5), %(puntoA)s) <
                                        ST_Line_Locate_Point(ST_Line_Substring(ruta, 0, 0.5), %(puntoB)s) and
                                        not paradas_completas
                                
                                    UNION
                                
                                    SELECT
                                        id,
                                        nombre,
                                        linea_id,
                                        color_polilinea,
                                        ST_Line_Substring(
                                            ST_Line_Substring(ruta, 0.5, 1),
                                            ST_Line_Locate_Point(ST_Line_Substring(ruta, 0.5, 1),	%(puntoA)s),
                                            ST_Line_Locate_Point(ST_Line_Substring(ruta, 0.5, 1),	%(puntoB)s)
                                        ) as ruta_corta,
                                        null::integer as p1,
                                        null::integer as p2,
                                        null::geometry as p1ll,
                                        null::geometry as p2ll
                                    FROM
                                        core_recorrido
                                    WHERE
                                        ST_DWithin(ST_GeomFromText(%(puntoA)s), ST_Line_Substring(ruta, 0.5, 1), %(rad1)s) and
                                        ST_DWithin(ST_GeomFromText(%(puntoB)s), ST_Line_Substring(ruta, 0.5, 1), %(rad2)s) and
                                        ST_Line_Locate_Point(ST_Line_Substring(ruta, 0.5, 1), %(puntoA)s) <
                                        ST_Line_Locate_Point(ST_Line_Substring(ruta, 0.5, 1), %(puntoB)s) and
                                        not paradas_completas
                                    
                                    UNION
                                
                                    SELECT
                                        id,
                                        nombre,
                                        linea_id,
                                        color_polilinea,
                                        ST_Line_Substring(
                                            ruta,
                                            ST_Line_Locate_Point(ruta, %(puntoA)s),
                                            ST_Line_Locate_Point(ruta, %(puntoB)s)
                                        ) as ruta_corta,
                                        null::integer as p1,
                                        null::integer as p2,
                                        null::geometry as p1ll,
                                        null::geometry as p2ll
                                    FROM
                                        core_recorrido
                                    WHERE
                                        ST_DWithin(ST_GeomFromText(%(puntoA)s), ruta, %(rad1)s) and
                                        ST_DWithin(ST_GeomFromText(%(puntoB)s), ruta, %(rad2)s) and
                                        ST_Line_Locate_Point(ruta, %(puntoA)s) <
                                        ST_Line_Locate_Point(ruta, %(puntoB)s) and
                                        not paradas_completas
                                    
                                    UNION
                                
                                    SELECT
                                        cr.id,
                                        cr.nombre,
                                        cr.linea_id,
                                        cr.color_polilinea,
                                        ST_Line_Substring(
                                            ruta,
                                            ST_Line_Locate_Point(ruta, rec.p1ll),
                                            ST_Line_Locate_Point(ruta, rec.p2ll)
                                        ) as ruta_corta,
                                        rec.p1id as p1,
                                        rec.p2id as p2,
                                        rec.p1ll as p1ll,
                                        rec.p2ll as p2ll
                                    FROM
                                        core_recorrido as cr
                                        JOIN (
                                            SELECT DISTINCT
                                                r.id as rid,
                                                p1.id as p1id,
                                                p2.id as p2id,
                                                p1.latlng as p1ll,
                                                p2.latlng as p2ll
                                            FROM
                                                core_recorrido    as r
                                                JOIN core_horario as h1 on (h1.recorrido_id = r.id)
                                                JOIN core_horario as h2 on (h2.recorrido_id = r.id)
                                                JOIN core_parada  as p1 on (p1.id = h1.parada_id)
                                                JOIN core_parada  as p2 on (p2.id = h2.parada_id and p1.id <> p2.id)
                                            WHERE
                                                ST_DWithin(ST_GeomFromText(%(puntoA)s), p1.latlng, %(rad1)s) and
                                                ST_DWithin(ST_GeomFromText(%(puntoB)s), p2.latlng, %(rad2)s) and
                                                ST_Line_Locate_Point(r.ruta, p1.latlng) <
                                                ST_Line_Locate_Point(r.ruta, p2.latlng) and
                                                r.paradas_completas
                                        ) as rec on (rec.rid = cr.id)
                                ) as busquedas
                        ) as agrupar
                        GROUP BY
                            id,
                            linea_id,
                            nombre,
                            color_polilinea,
                            p1,
                            p2
                    ) as re
                    on li.id = re.linea_id
                    ORDER BY
                        long_pata*10 + long_ruta asc
            ;"""

        query_set = self.raw(query, params)
        return list(query_set)

    def fuzzy_trgm_query(self, q):
        params = {"q": q}
        query = """
            SELECT
                set_limit(0.01);
            SELECT
                r.id,
                l.nombre || ' ' || r.nombre as nombre,
                similarity(l.nombre || ' ' || r.nombre, %(q)s) as similarity,
                Astext(r.ruta) as ruta_corta
            FROM
                core_recorrido as r
                join core_linea as l on (r.linea_id = l.id)
            WHERE
                (l.nombre || ' ' || r.nombre) %% %(q)s
            ORDER BY
                similarity DESC
            LIMIT
                10
            ;
        """
        query_set = self.raw(query, params)
        return query_set

    def fuzzy_fts_query(self, q):
        params = {"q": q}
        query = """
            SELECT
                r.id,
                l.nombre || ' ' || r.nombre as nombre,
                ts_rank_cd(to_tsvector('spanish', l.nombre || ' ' || r.nombre), query, 32) as similarity,
                Astext(r.ruta) as ruta_corta
            FROM
                core_recorrido as r
                join core_linea as l on (r.linea_id = l.id)
                cross join plainto_tsquery('spanish', %(q)s) query
            WHERE
                query @@ to_tsvector('spanish', l.nombre || ' ' || r.nombre)
            ORDER BY
                similarity DESC
            LIMIT
                10
            ;
        """
        query_set = self.raw(query, params)
        return query_set

    def fuzzy_like_query(self, q, ciudad):
        params = {"q": q, "ci": ciudad}
        query = """
            SELECT
                r.id,
                l.nombre || ' ' || r.nombre as nombre,
                Astext(r.ruta) as ruta_corta,
                l.foto as foto,
                ST_Length(r.ruta::Geography) as long_ruta
            FROM
                core_recorrido as r
                join core_linea as l on (r.linea_id = l.id)
                join catastro_ciudad_lineas as cl on (cl.linea_id = l.id )
                join catastro_ciudad as c on (c.id = cl.ciudad_id)
            WHERE
                (l.nombre || ' ' || r.nombre) ILIKE ('%%' || %(q)s || '%%')
                AND c.slug = %(ci)s
            LIMIT
                10
            ;
        """
        query_set = self.raw(query, params)
        return query_set

    def fuzzy_like_trgm_query(self, q, ciudad):
        params = {"q": q, "ci": ciudad}
        query = """
            SELECT
                r.id,
                l.nombre || ' ' || r.nombre as nombre,
                Astext(r.ruta) as ruta_corta,
                l.foto as foto,
                ST_Length(r.ruta::Geography) as long_ruta,
                similarity(l.nombre || ' ' || r.nombre, %(q)s) as similarity
            FROM
                core_recorrido as r
                join core_linea as l on (r.linea_id = l.id)
                join catastro_ciudad_lineas as cl on (cl.linea_id = l.id )
                join catastro_ciudad as c on (c.id = cl.ciudad_id)
            WHERE
                (l.nombre || ' ' || r.nombre) ILIKE ('%%' || %(q)s || '%%')
                AND c.slug = %(ci)s
            ORDER BY
                similarity DESC,
                (l.nombre || ' ' || r.nombre) ASC
            ;
        """
        query_set = self.raw(query, params)
        return query_set
