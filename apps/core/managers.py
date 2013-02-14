# -*- coding: UTF-8 -*-
from django.db import DatabaseError
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point


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

        params = {'puntoA': puntoA.ewkt, 'puntoB': puntoB.ewkt, 'rad1': distanciaA, 'rad2': distanciaB, 'gap': gap}
        query = """
            SELECT *
            FROM (
                SELECT
                    re1.id as id,
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
                    ST_AsText(
                        ST_Line_Substring(
                            re1.ruta,
                            ST_Line_Locate_Point(re1.ruta, %(puntoA)s),
                            ST_Line_Locate_Point(re1.ruta, ST_ClosestPoint(re1.ruta, re2.ruta))
                            )::Geography
                        ) as ruta_corta,
                    ST_AsText(
                        ST_Line_Substring(
                            re2.ruta,
                            ST_Line_Locate_Point(re2.ruta, ST_ClosestPoint(re1.ruta, re2.ruta)),
                            ST_Line_Locate_Point(re2.ruta, %(puntoB)s)
                            )::Geography
                        ) as ruta_corta2,
                    ST_Length(
                        ST_Line_Substring(
                            re1.ruta,
                            ST_Line_Locate_Point(re1.ruta, %(puntoA)s),
                            ST_Line_Locate_Point(re1.ruta, ST_ClosestPoint(re1.ruta, re2.ruta))
                            )::Geography
                        ) as long_ruta,
                    ST_Length(
                        ST_Line_Substring(
                            re2.ruta,
                            ST_Line_Locate_Point(re2.ruta, ST_ClosestPoint(re1.ruta, re2.ruta)),
                            ST_Line_Locate_Point(re2.ruta, %(puntoB)s)
                            )::Geography
                        ) as long_ruta2,
                    ST_Distance_Sphere(ST_GeomFromText(%(puntoA)s), re1.ruta) as long_pata,
                    ST_Distance_Sphere(ST_GeomFromText(%(puntoB)s), re2.ruta) as long_pata2,
                    ST_Distance_Sphere(re1.ruta, re2.ruta) as long_pata_transbordo

                FROM
                    core_recorrido as re1
                    join core_recorrido as re2 on (re1.id <> re2.id)
                    join core_linea li1 on li1.id = re1.linea_id
                    join core_linea li2 on li2.id = re2.linea_id
                WHERE
                    ST_Distance_Sphere(ST_GeomFromText(%(puntoA)s), re1.ruta) < %(rad1)s
                    and
                    ST_Distance_Sphere(ST_GeomFromText(%(puntoB)s), re2.ruta) < %(rad2)s
                    and
                        ST_Distance_Sphere(re1.ruta, re2.ruta) < %(gap)s
                    and
                        ST_Line_Locate_Point(re1.ruta, %(puntoA)s)
                        <
                        ST_Line_Locate_Point(re1.ruta, ST_ClosestPoint(re1.ruta, re2.ruta) )
                    and
                        ST_Line_Locate_Point(re2.ruta, ST_ClosestPoint(re1.ruta, re2.ruta) )
                        <
                        ST_Line_Locate_Point(re2.ruta, %(puntoB)s)
                ) as subquery
            ORDER BY (cast(long_pata as integer)*10 + cast(long_ruta as integer) + cast(long_ruta2 as integer)) ASC
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

        params = {'puntoA': puntoA.ewkt, 'puntoB': puntoB.ewkt, 'rad1': distanciaA, 'rad2': distanciaB}
        query = """
                SELECT
                    re.id,
                    li.nombre || ' ' || re.nombre as nombre,
                    ruta_corta,
                    long_ruta,
                    long_pata,
                    coalesce(re.color_polilinea, li.color_polilinea, '#000') as color_polilinea,
                    coalesce(li.foto, 'default') as foto
                FROM
                    core_linea as li join
                    (
                        SELECT
                            id,
                            nombre,
                            ST_AsText(min_path(ruta_corta)) as ruta_corta,
                            round(min(long_ruta)::numeric, 2) as long_ruta,
                            round(min(long_pata)::numeric, 2) as long_pata,
                            linea_id,
                            color_polilinea
                        FROM
                        (
                            (
                                SELECT
                                    *,
                                    ST_Length(ruta_corta::Geography) as long_ruta,
                                    ST_Distance_Sphere(ST_GeomFromText(%(puntoA)s),ruta_corta) +
                                    ST_Distance_Sphere(ST_GeomFromText(%(puntoB)s),ruta_corta) as long_pata
                                FROM
                                (
                                    SELECT
                                        *,
                                        ST_Line_Substring(
                                            ST_Line_Substring(ruta, 0, 0.5),
                                            ST_Line_Locate_Point(ST_Line_Substring(ruta, 0, 0.5),	%(puntoA)s),
                                            ST_Line_Locate_Point(ST_Line_Substring(ruta, 0, 0.5),	%(puntoB)s)
                                        ) as ruta_corta
                                    FROM
                                        core_recorrido
                                    WHERE
                                        ST_Distance_Sphere(ST_GeomFromText(%(puntoA)s), ST_Line_Substring(ruta, 0, 0.5)) < %(rad1)s and
                                        ST_Distance_Sphere(ST_GeomFromText(%(puntoB)s), ST_Line_Substring(ruta, 0, 0.5)) < %(rad2)s and
                                        ST_Line_Locate_Point(ST_Line_Substring(ruta, 0, 0.5), %(puntoA)s) <
                                            ST_Line_Locate_Point(ST_Line_Substring(ruta, 0, 0.5), %(puntoB)s)
                                ) as primera_inner
                            )
                        UNION
                        (
                            SELECT
                                *,
                                ST_Length(ruta_corta::Geography) as long_ruta,
                                ST_Distance_Sphere(ST_GeomFromText(%(puntoA)s),ruta_corta) + ST_Distance_Sphere(ST_GeomFromText(%(puntoB)s),ruta_corta) as long_pata
                            FROM
                            (
                                SELECT
                                    *,
                                    ST_Line_Substring(
                                        ST_Line_Substring(ruta, 0.5, 1),
                                        ST_Line_Locate_Point(ST_Line_Substring(ruta, 0.5, 1),	%(puntoA)s),
                                        ST_Line_Locate_Point(ST_Line_Substring(ruta, 0.5, 1),	%(puntoB)s)
                                    ) as ruta_corta
                                FROM
                                    core_recorrido
                                WHERE
                                    ST_Distance_Sphere(ST_GeomFromText(%(puntoA)s), ST_Line_Substring(ruta, 0.5, 1)) < %(rad1)s and
                                    ST_Distance_Sphere(ST_GeomFromText(%(puntoB)s), ST_Line_Substring(ruta, 0.5, 1)) < %(rad2)s and
                                    ST_Line_Locate_Point(ST_Line_Substring(ruta, 0.5, 1), %(puntoA)s) <
                                    ST_Line_Locate_Point(ST_Line_Substring(ruta, 0.5, 1), %(puntoB)s)
                                ) as segunda_inner
                            )
                            UNION
                            (
                                SELECT
                                    *,
                                    ST_Length(ruta_corta::Geography) as long_ruta,
                                    ST_Distance_Sphere(ST_GeomFromText(%(puntoA)s),ruta_corta) + ST_Distance_Sphere(ST_GeomFromText(%(puntoB)s),ruta_corta) as long_pata
                                FROM
                                (
                                    SELECT
                                        *,
                                        ST_Line_Substring(
                                            ruta,
                                            ST_Line_Locate_Point(ruta, %(puntoA)s),
                                            ST_Line_Locate_Point(ruta, %(puntoB)s)
                                        ) as ruta_corta
                                    FROM
                                        core_recorrido
                                    WHERE
                                        ST_Distance_Sphere(ST_GeomFromText(%(puntoA)s), ruta) < %(rad1)s and
                                        ST_Distance_Sphere(ST_GeomFromText(%(puntoB)s), ruta) < %(rad2)s and
                                        ST_Line_Locate_Point(ruta, %(puntoA)s) <
                                        ST_Line_Locate_Point(ruta, %(puntoB)s)
                                ) as completa_inner
                            )
                        ) as interior
                        GROUP BY
                            id,
                            linea_id,
                            nombre,
                            color_polilinea
                        ORDER BY
                        (
                            cast(min(long_pata)  as integer)*10 +
                            cast(min(long_ruta) as integer)
                        ) ASC
                    ) as re
                    on li.id = re.linea_id
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
