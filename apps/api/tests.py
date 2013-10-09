# -*- coding: utf-8 -*-
# Copyright 2011-2012, Cualbondi
"""Tests para los API Handlers"""

import json

from django_webtest import WebTest
from pprint import pprint

from apps.api.factories import CiudadFactory


class TestCiudadHandler(WebTest):
    def setUp(self):
        for i in range(5):
            CiudadFactory()

    def test_ciudades_listado(self):
        """Debe devolver el listado de ciudades cuando no se le pasa ningun ID de ciudad como parametro"""
        response = self.app.get('/api/ciudades/')
        self.assertEqual(response.status, '200 OK')
        data = json.loads(response.content)
        self.assertTrue(type(data), list)
        self.assertEqual(len(data), 5)
        for ciudad in data:
            for field in ['nombre', 'slug', 'provincia', 'activa', 'centro',
                          'descripcion', 'poligono']:
                self.assertTrue(field in ciudad)

    def test_ciudades_por_id(self):
        """Debe devolver una ciudad en particular cuando se manda el ID por parametro"""
        ciudad = CiudadFactory(nombre='La Plata')
        response = self.app.get('/api/ciudades/{0}/'.format(ciudad.id))
        self.assertEqual(response.status, '200 OK')
        data = json.loads(response.content)
        self.assertTrue(type(data), dict)
        self.assertEqual(data['nombre'], 'La Plata')
        self.assertEqual(data['slug'], 'la-plata')
