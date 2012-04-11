from django.contrib.gis.db import models
from django.contrib.gis.geos import Point


class RecorridoManager(models.GeoManager):
    def get_recorridos_combinados(self, puntoA, puntoB, distanciaA, distanciaB):
        return []

    def get_recorridos(self, puntoA, puntoB, distanciaA, distanciaB):
        distanciaA=int(distanciaA)
        distanciaB=int(distanciaB)
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

        params = {'puntoA':puntoA.ewkt, 'puntoB':puntoB.ewkt, 'rad1':distanciaA, 'rad2':distanciaB}
        query = """
                SELECT
		                id,
		                nombre,
		                ST_AsText(min_path(ruta_corta)) as ruta_corta,
		                min(long_bondi) as long_bondi,
		                min(long_pata) as long_pata
	                FROM
                (
                  (
              		  SELECT
                			*,
                			ST_Length(ruta_corta) as long_bondi,
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
                			ST_Length(ruta_corta) as long_bondi,
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
                			ST_Length(ruta_corta) as long_bondi,
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
		                nombre
	                ORDER BY
		                (
		                  cast(min(long_pata)  as integer)*10 +
		                  cast(min(long_bondi) as integer)
		                ) ASC
                ;"""

        query_set = self.raw(query, params)
        return list(query_set)


