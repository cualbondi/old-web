# -*- coding: utf-8 -*-
# Copyright 2011-2012, Cualbondi
"""Define clases Factory que van a ser usados en los tests"""

import factory
from django.template.defaultfilters import slugify

from apps.catastro.models import Ciudad, Provincia
from apps.core.models import Recorrido, Linea


class LineaFactory(factory.Factory):
    FACTORY_FOR = Linea

    nombre = factory.Sequence(lambda n: 'Linea {0}'.format(n))


class RecorridoFactory(factory.Factory):
    FACTORY_FOR = Recorrido

    nombre = factory.Sequence(lambda n: 'Recorrido {0}'.format(n))
    linea = factory.SubFactory(LineaFactory)
    ruta = ("LINESTRING(-57.9226362705231 -34.9400027415366,"
            "-57.9250180721283 -34.9382261348933)")
    inicio = "inicio recorrido"
    fin = "fin recorrido"


class ProvinciaFactory(factory.Factory):
    FACTORY_FOR = Provincia

    nombre = factory.Sequence(lambda n: 'Provincia número {0}'.format(n))
    slug = factory.LazyAttribute(lambda provincia: slugify(provincia.nombre))


class CiudadFactory(factory.Factory):
    FACTORY_FOR = Ciudad

    provincia = factory.SubFactory(ProvinciaFactory)
    nombre = factory.Sequence(lambda n: 'Ciudad número {0}'.format(n))
    slug = factory.LazyAttribute(lambda ciudad: slugify(ciudad.nombre))
