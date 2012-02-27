from django.contrib.gis.db import models
from django.db import DatabaseError
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.contrib.gis.geos import Point

class Linea(models.Model):
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, blank=True, null=False)
    descripcion = models.TextField()
    foto = models.CharField(max_length=20, blank=True, null=True)

    def __unicode__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        self.slug = slugify("linea " + self.nombre)
        super(Linea, self).save(*args, **kwargs)

class Terminal(models.Model):
    linea = models.ForeignKey(Linea)
    descripcion = models.TextField()
    direccion = models.CharField(max_length=150)
    telefono = models.CharField(max_length=150)
    latlng = models.PointField()
    objects = models.GeoManager()


class RecorridoManager(models.GeoManager):
    def get_recorridos(self, puntoA, puntoB, distanciaA, distanciaB):
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
        return self.raw("""
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
	;""", {'puntoA':puntoA.ewkt, 'puntoB':puntoB.ewkt, 'rad1':distanciaA, 'rad2':distanciaB})

class Recorrido(models.Model):
    nombre = models.CharField(max_length=100)
    ruta = models.LineStringField()
    slug = models.SlugField(max_length=200, blank=True, null=False)
    inicio = models.CharField(max_length=100)
    fin = models.CharField(max_length=100)
    linea = models.ForeignKey(Linea)
    semirrapido = models.BooleanField()
    
    objects = RecorridoManager()

    def __unicode__(self):
        return str(self.linea) + " " + self.nombre

    def save(self, *args, **kwargs):
        self.slug = slugify("recorrido " + self.nombre + " desde " +\
                                   self.inicio + " hasta " + self.fin)
        super(Recorrido, self).save(*args, **kwargs)


class Provincia(models.Model):
    nombre = models.CharField(max_length=100)
    zona = models.PolygonField()
    objects = models.GeoManager()

    def __unicode__(self):
        return self.nombre


class Ciudad(models.Model):
    nombre = models.CharField(max_length=100)
    recorridos = models.ManyToManyField(Recorrido, blank=True, null=True)
    lineas = models.ManyToManyField(Linea, blank=True, null=True)
    slug = models.SlugField(max_length=120, blank=True, null=False)
    zona = models.PolygonField()
    zoom = models.IntegerField()
    centro = models.PointField()
    provincia = models.ForeignKey(Provincia)
    activa = models.BooleanField(default=False)
    objects = models.GeoManager()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nombre)
        super(Ciudad, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.nombre + " (" + self.provincia.nombre + ")"


class Comercio(models.Model):
    nombre = models.CharField(max_length=100)
    latlng = models.PointField()
    ciudad = models.ForeignKey(Ciudad)
    objects = models.GeoManager()


class Poi(models.Model):
    """ Un "Punto de interes" es algun lugar representativo
        de una "Ciudad". Por ej: la catedral de La Plata.
    """
    nombre = models.CharField(max_length=100)
    latlng = models.PointField()
    ciudad = models.ForeignKey(Ciudad)
    objects = models.GeoManager()


class CustomPoi(models.Model):
    """ Los usuarios pueden definir sus propios
        puntos de interes. Por ej: "Mi casa", y
        luego usarlos como puntos origen o destino 
        en las busquedas. 
    """
    usuario = models.ForeignKey(User)
    nombre = models.CharField(max_length=100)
    latlng = models.PointField()
    objects = models.GeoManager()


class RecorridoFavorito(models.Model):
    """ Los "Usuarios" pueden marcar un "Recorrido"
        como favorito. Si lo DESmarcan como favorito,
        la tupla no se borra, sino que se pone como
        activo = False
    """
    usuario = models.ForeignKey(User)
    recorrido = models.ForeignKey(Recorrido)
    activo = models.BooleanField()


class Parada(models.Model):
    nombre = models.CharField(max_length=100)
    latlng = models.PointField()
    objects = models.GeoManager()


class Horario(models.Model):
    """ Un "Recorrido" pasa por una "Parada" a
        cierto "Horario". "Horario" es el modelo 
        interpuesto entre "Recorrido" y "Parada"
    """
    recorrido = models.ForeignKey(Recorrido)
    parada = models.ForeignKey(Parada)
    hora = models.CharField(max_length=5)
