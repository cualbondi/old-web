from django.db import models

class Version(models.Model):
    """Version de un paquete y con respectiva noticia de lanzamiento de paquete"""

    TIPO = (
        ('a', 'Aplicacion android'),
        ('l', 'Lineas'),
        ('c', 'Ciudades'),
    )

    timestamp = models.DateTimeField()
    name      = models.CharField(max_length=20)
    tipo      = models.CharField(max_length=1, choices=TIPO)
    noticia   = models.CharField(max_length=500)

    def __unicode__(self):
        return u'{tipo} {name}'.format(
            tipo=self.get_tipo_display(),
            name=self.name
        )
