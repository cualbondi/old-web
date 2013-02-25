# -*- coding: utf-8 -*-
# Copyright 2011-2012, Cualbondi
"""Define clases Factory que van a ser usados en los tests"""

import factory
from django.template.defaultfilters import slugify

from apps.catastro.models import Ciudad, Provincia


class ProvinciaFactory(factory.Factory):
    FACTORY_FOR = Provincia

    nombre = factory.Sequence(lambda n: 'Provincia número {0}'.format(n))
    slug = factory.LazyAttribute(lambda provincia: slugify(provincia.nombre))


class CiudadFactory(factory.Factory):
    FACTORY_FOR = Ciudad

    provincia = factory.SubFactory(ProvinciaFactory)
    nombre = factory.Sequence(lambda n: 'Ciudad número {0}'.format(n))
    slug = factory.LazyAttribute(lambda ciudad: slugify(ciudad.nombre))
